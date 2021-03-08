
import json
from operator import and_

import connexion
import yaml
import logging.config
from connexion import NoContent
import connexion
from connexion import NoContent
from threading import Thread

from pykafka import KafkaClient
from pykafka.common import OffsetType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from grocery_inventory import GroceryInventory
from produce_inventory import ProduceInventory
import datetime

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
USER = app_config["datastore"]["user"]
PASSWORD = app_config["datastore"]["password"]
HOST = app_config["datastore"]["hostname"]
PORT = app_config["datastore"]["port"]
DB = app_config["datastore"]["db"]

DB_ENGINE = create_engine ('mysql+pymysql://'+str(USER)+':'+str(PASSWORD)+'@'+str(HOST)+':'+str(PORT)+'/'+str(DB))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def grocery_item_scan(body):
    """ Receives a blood pressure reading """

    session = DB_SESSION()

    gi = GroceryInventory(body['id'],
                       body['name'],
                       body['manufacturer'],
                       body['price'],
                       body['manufacture_date'],
                       body['expiration_date'],
                       body['quantity']
                       )

    session.add(gi)

    session.commit()
    session.close()

    logger.debug("Stored event grocery_item_scan request with a unique id of " + str(body["id"]))
    logger.info("Connecting to DB. Hostname: "+ str(HOST) + ", Port: " + str(PORT))



def produce_item_scan(body):
    """ Receives a heart rate (pulse) reading """

    session = DB_SESSION()

    pi = ProduceInventory(body['id'],
                          body['name'],
                          body['supplier'],
                          body['price'],
                          body['expiration_date'],
                          body['weight'],
                          body['quantity']
                          )

    session.add(pi)
    session.commit()
    session.close()
    logger.debug("Stored event produce_item_scan request with a unique id of " + str(body["id"]))
    logger.info("Connecting to DB. Hostname: "+ str(HOST) + ", Port: " + str(PORT))


def get_grocery_scan(start_timestamp, end_timestamp):
    """ Gets new grocery scan readings after the timestamp """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%SZ')


    readings = session.query(GroceryInventory).filter(
        and_(GroceryInventory.date_created >= start_timestamp_datetime,
            GroceryInventory.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Grocery Scan readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200

def get_produce_scan(start_timestamp, end_timestamp):
    """ Gets new produce scan readings after the timestamp """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%SZ')

    readings = session.query(ProduceInventory).filter(
        and_(ProduceInventory.date_created >= start_timestamp_datetime,
             ProduceInventory.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Produce scan readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    '''Process event messages'''
    hostname = "%s:%d" %(app_config["events"]["hostname"],
                          app_config["events"]["port"])

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topics"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,
                                            auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Messages: %s" %msg)

        payload = msg["payload"]

        if msg["type"]  == "gc":
            grocery_item_scan(payload)           
            logger.debug("Stored event assign_gate request with a unique id of " + str(payload['id']))

        elif msg["type"]  == "pr":
            produce_item_scan(payload)


        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)


