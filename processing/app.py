import datetime
import os
from flask_cors import CORS, cross_origin
import yaml
from connexion import NoContent
import requests
import json
import yaml
import logging.config
import connexion
from apscheduler.schedulers.background import BackgroundScheduler

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

EVENT_STORE = app_config['eventstore']['url']
FILE_NAME = app_config["datastore"]["filename"]


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    stats={}
    if os.path.isfile(FILE_NAME):
        stats_file = open(FILE_NAME)
        data = stats_file.read()
        stats = json.loads(data)

        stats_file.close()

    last_updated = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    if "last_updated" in stats:
        last_updated = stats["last_updated"]
    
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    payload = {'start_timestamp': last_updated, 'end_timestamp': current_timestamp}
    response = requests.get(EVENT_STORE+"/scans/Groceries",params=payload)

    if response.status_code == 200:
        if "num_grc_readings" in stats.keys():
            stats["num_grc_readings"]+= len(response.json())
        else:
            stats["num_grc_readings"] = len(response.json())

        for event in response.json():
            if "max_grc_qty" in stats.keys() and event["quantity"] >= stats["max_grc_qty"]:
                stats["max_grc_qty"] = event["quantity"]
            elif "max_grc_qty" not in stats.keys():
                stats["max_grc_qty"] = event["quantity"]

        logger.info("Processed %d Grocery scans!" % len(response.json()))

    response = requests.get(EVENT_STORE+"/scans/Produce",params=payload)
    if response.status_code == 200:
        if "num_pr_readings" in stats.keys():
            stats["num_pr_readings"] += len(response.json())
        else:
            stats["num_pr_readings"] = len(response.json())
        for event in response.json():
            if "max_pr_qty" in stats.keys() and event["quantity"] >= stats["max_pr_qty"]:
                stats["max_pr_qty"] = event["quantity"]
            elif "max_pr_qty" not in stats.keys():
                stats["max_pr_qty"] = event["quantity"]

        logger.info("Processed %d Produce scans!" % len(response.json()))
    stats["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    stats_file = open(FILE_NAME, "w")
    stats_file.write(json.dumps(stats, indent=4))
    stats_file.close()
    logger.info("End Periodic Processing")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats():
    '''Gets statistics from the data file'''
    logger.info("GET Request has been started")
    stats={}
    if os.path.isfile(FILE_NAME):
        stats_file = open(FILE_NAME)
        data = stats_file.read()

        stats = json.loads(data)

        stats_file.close()
    else:
        logger.error("Statistics do not exist")
        return 404

    logger.debug(stats)
    logger.info("GET Request has been completed")

    return stats, 200




app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
