import os
import sys
import json
import pandas as pd
import pymongo
import certifi
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL=os.getenv('MONGO_DB_URL')
print(MONGO_DB_URL)

ca = certifi.where()

class NetweorkDataExtract():
    
    def __init__(self, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json_convertor(self, file_path):
        
        try:
            data = pd.read_csv(file_path).reset_index(drop=True)
            logging.info("Data Read from CSV file - {file_path}")
            records = list(json.loads(data.T.to_json()).values())
            logging.info(f"Convert the data into list of JSON")
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_to_mongodb(self, records):
        
        try:
            self.records = records
            self.db = self.mongo_client[self.database]
            self.col = self.db[self.collection]
            
            logging.info('Clearing existing data from collection')
            self.col.drop()
            
            self.col.insert_many(self.records)

            logging.info(f"{len(self.records)} inserted into DB")
            return len(self.records)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
if __name__ == '__main__':
    
    FILE_PATH = 'Network_Data/phisingData.csv'
    DATABASE = 'MLProjectDB01'
    COLLECTION = 'NetworkData'
    
    network_data_extract_obj = NetweorkDataExtract(database=DATABASE, collection=COLLECTION)
    records = network_data_extract_obj.csv_to_json_convertor(file_path=FILE_PATH)
    records_count = network_data_extract_obj.insert_data_to_mongodb(records=records)
    print(f"{records_count} records inserted into DB")
    
        