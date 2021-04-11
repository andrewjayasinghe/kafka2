import datetime
import json
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
import connexion
import yaml
from connexion import NoContent
import requests
import os
import time

MAX_EVENTS = 10

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

HOST = app_config["events"]["hostname"]
PORT = app_config["events"]["port"]
MAX = app_config["events"]["max_try"]
TIMING = app_config["events"]["time"]

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

hostname = "%s:%d" % (HOST, PORT)



count = 0

while count < MAX: 
    try:
        logger.info("Trying to connect to Kafka! try no: %d" %count)
        client = KafkaClient(hosts=hostname) 
        topic = client.topics[str.encode(app_config["events"]["topics"])]
        producer = topic.get_sync_producer()
        break 
    except:
        logger.error("Lost connection in some other way")
        time.sleep(TIMING)
        count += 1

def grocery_item_scan(body):
    '''adds grocery item to inventory'''

    msg = { "type":"gc",
            "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event grocery_scan " + str(body["id"]) + " with status 201")

    return NoContent, 201 

def produce_item_scan(body):
    '''adds produce items to inventory'''
    msg = {"type": "pr",
        "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event produce_scan " + str(body["id"]) + " with status 201")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/reciever",  strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)

