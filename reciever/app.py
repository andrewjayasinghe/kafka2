# import datetime
# import json
# import logging.config
# from pykafka import KafkaClient
# from pykafka.common import OffsetType
# import connexion
# import yaml
# from connexion import NoContent
# import requests


# MAX_EVENTS = 10
# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

# # GROCERY_URL = app_config["Groceries"]["url"]
# # PRODUCE_URL = app_config["Produce"]["url"]
# HOST = app_config["events"]["hostname"]
# PORT = app_config["events"]["port"]

# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

# def grocery_item_scan(body):
#     '''adds grocery item to inventory'''
#     hostname = "%s:%d" % (HOST, PORT)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config["events"]["topics"])]
#     producer = topic.get_sync_producer()
#     msg = { "type":"gc",
#             "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
#             "payload": body}

#     msg_str = json.dumps(msg)
#     producer.produce(msg_str.encode('utf-8'))

#     logger.info("Returned event grocery_scan " + str(body["id"]) + " with status 201")

#     return NoContent, 201


# def produce_item_scan(body):
#     '''adds produce items to inventory'''
#     hostname = "%s:%d" % (HOST, PORT)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config["events"]["topics"])]
#     producer = topic.get_sync_producer()
#     msg = {"type": "pr",
#            "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
#            "payload": body}

#     msg_str = json.dumps(msg)
#     producer.produce(msg_str.encode('utf-8'))

#     logger.info("Returned event grocery_scan " + str(body["id"]) + " with status 201")

#     return NoContent, 201

# app = connexion.FlaskApp(__name__, specification_dir='')
# app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


# if __name__ == "__main__":
#     app.run(port=8080)

import connexion
from connexion import NoContent
import json
import requests
import yaml
import logging
import logging.config
import datetime
from pykafka import KafkaClient
import os

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

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

AIR_EVENT = 'Air Reading'
ENV_EVENT = 'Env. Reading'

kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']



def measure_air_quality(body):
    """Takes in an air reading, and sends to Data storage service"""
    logger.info(f'Received event {AIR_EVENT} request with unique id ({body["sensor_id"]})')
    # response = requests.post(app_config['air_reading']['url'], json.dumps(body),
    #                          headers={'content-type': 'application/json'})
    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[kafka_topic]
    producer = topic.get_sync_producer()
    msg = {"type": "air_reading",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f'Returned event {AIR_EVENT} response id ({body["sensor_id"]}) with status code 201  ')
    return NoContent, 201


def measure_environment(body):
    """Takes in an environment reading, and sends to Data storage service"""
    logger.info(f'Received event {ENV_EVENT} request with unique id({body["sensor_id"]})')
    # response = requests.post(app_config['env_reading']['url'], json.dumps(body),
    #                          headers={'content-type': 'application/json'})
    # logger.info(f'Returned event {ENV_EVENT} response id ({body["sensor_id"]}) with status code {response.status_code}  ')
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[kafka_topic]
    producer = topic.get_sync_producer()
    msg = {"type": "env_reading",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    logger.info("Message: %s" % msg)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)