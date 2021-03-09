import datetime
import json
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
import connexion
import yaml
from connexion import NoContent
import requests


MAX_EVENTS = 10
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# GROCERY_URL = app_config["Groceries"]["url"]
# PRODUCE_URL = app_config["Produce"]["url"]
HOST = app_config["events"]["hostname"]
PORT = app_config["events"]["port"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def grocery_item_scan(body):
    '''adds grocery item to inventory'''
    hostname = "%s:%d" % (HOST, PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topics"])]
    producer = topic.get_sync_producer()
    msg = { "type":"gc",
            "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event grocery_scan " + str(body["id"]) + " with status 201")

    return NoContent, 201


def produce_item_scan(body):
    '''adds produce items to inventory'''
    hostname = "%s:%d" % (HOST, PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topics"])]
    producer = topic.get_sync_producer()
    msg = {"type": "pr",
           "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event grocery_scan " + str(body["id"]) + " with status 201")

    return NoContent, 201


# def get_grocery_scan(index):
#     """ Gets new grocery scan readings after the timestamp """
#     hostname = "%s:%d" % (HOST, PORT)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config["events"]["topics"])]
#     consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
#
#     logger.info("Retrieving reading at index %d" % index)
#
#     count = 0
#     reading = None
#
#     try:
#         for msg in consumer:
#             msg_str = msg.value.decode('utf-8')
#             msg = json.loads(msg_str)
#
#             if msg["type"] == "gc":
#
#                 if count == index:
#                     reading = msg["payload"]
#                     return reading, 200
#
#                 count += 1
#
#     except:
#         logger.error("No more messages found")
#
#     logger.error("could not find gc at index %d" %index)
#
#     return {"message":"Not Found"}, 404
#
# def get_produce_scan(index):
#     """ Gets new produce scan readings after the timestamp """
#     hostname = "%s:%d" % (HOST, PORT)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config["events"]["topics"])]
#     consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
#
#     logger.info("Retrieving reading at index %d" % index)
#
#     count = 0
#     reading = None
#
#     try:
#         for msg in consumer:
#             msg_str = msg.value.decode('utf-8')
#             msg = json.loads(msg_str)
#
#             if msg["type"] == "pr":
#
#                 if count == index:
#                     reading = msg["payload"]
#                     return reading, 200
#
#                 count += 1
#
#     except:
#         logger.error("No more messages found")
#
#     logger.error("could not find pr at index %d" % index)
#
#     return {"message": "Not Found"}, 404
#
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)

