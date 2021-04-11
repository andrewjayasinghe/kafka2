import datetime
import os
from flask_cors import CORS, cross_origin
import yaml
from connexion import NoContent
import requests
from pykafka import KafkaClient
from pykafka.common import OffsetType
import json
import yaml
import logging.config
import connexion


if "TARGET_ENV" not in os.environ and os.environ["TARGET_ENV"] != "test":
    #print("In Test Environment")
    #app_conf_file = "/config/app_conf.yml"
    #log_conf_file = "/config/log_conf.yml"
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

HOST = app_config["events"]["hostname"]
PORT = app_config["events"]["port"]

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def get_grocery_reading(index):
    """ Gets new grocery scan readings after the timestamp """
    hostname = "%s:%d" % (HOST, PORT)
    client = KafkaClient(hosts=hostname)
    print(index)
    topic = client.topics[str.encode(app_config["events"]["topics"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving reading at index %d" % index)

    count = 0
    reading = None

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "gc":

                if count == index:
                    reading = msg["payload"]
                    return reading, 200
                count += 1
    except:
        logger.error("No more messages found")

    logger.error("could not find gc at index %d" %index)

    return {"message":"Not Found"}, 404


def get_produce_reading(index):
    """ Gets new grocery scan readings after the timestamp """
    hostname = "%s:%d" % (HOST, PORT)
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topics"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving reading at index %d" % index)

    count = 0
    reading = None

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "pr":

                if count == index:
                    reading = msg["payload"]
                    return reading, 200
                count += 1
    except:
        logger.error("No more messages found")

    logger.error("could not find gc at index %d" %index)

    return {"message":"Not Found"}, 404




app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml",base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, use_reloader=False)
