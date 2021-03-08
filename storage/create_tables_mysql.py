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
          CREATE TABLE GroceryItem
          (reading_id INT NOT NULL AUTO_INCREMENT,
           id VARCHAR(250) NOT NULL, 
           name VARCHAR(250) NOT NULL,
           manufacturer VARCHAR(100) NOT NULL,
           price VARCHAR(100) NOT NULL,
           manufacture_date VARCHAR(250) NOT NULL,
           expiration_date VARCHAR(250) NOT NULL,  
           quantity INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT grocery_item_pk PRIMARY KEY (reading_id))
          ''')


db_cursor.execute('''
          CREATE TABLE ProduceItem
          (reading_id INT NOT NULL AUTO_INCREMENT,
           id VARCHAR(250) NOT NULL, 
           name VARCHAR(250) NOT NULL,
           supplier VARCHAR(250) NOT NULL,
           price VARCHAR(250) NOT NULL,
           expiration_date VARCHAR(100) NOT NULL,
           weight VARCHAR(100) NOT NULL,
           quantity INTEGER NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT produce_item_pk PRIMARY KEY (reading_id))
          ''')

db_conn.commit()
db_conn.close()
