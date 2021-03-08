import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
USER = app_config["datastore"]["user"]
PASSWORD = app_config["datastore"]["password"]
HOST = app_config["datastore"]["hostname"]
PORT = app_config["datastore"]["port"]
DB = app_config["datastore"]["db"]

db_conn = mysql.connector.connect(host=HOST, user=USER,
password=PASSWORD, database=DB)

db_cursor = db_conn.cursor()


db_cursor.execute('''
          DROP TABLE GroceryItem, ProduceItem
          ''')

db_conn.commit()
db_conn.close()
