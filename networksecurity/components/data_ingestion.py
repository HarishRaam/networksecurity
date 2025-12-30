import sys
import os
import pandas as pd
import numpy as np
import pymongo
from typing import List
from sklearn.model_selection import train_test_split

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    
    # Step 1. Connect to MongoDB and pull the collection and convert it to dataframe
    # Step 2. Export data to feature store
    # Step 3. Split data as train and test
    # Step 4. Return Data ingestion artifact - with train and test folder paths
    
    def __init__(self, data_ingestion_config:DataIngestionConfig):
        
        try: 
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
            
        

    def export_collection_as_dataframe(self):
        
        """
        Read data from Mongodb
        """
        
        try:
            self.database_name = self.data_ingestion_config.database_name
            self.collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            
            self.collection = self.mongo_client[self.database_name][self.collection_name]
            df = pd.DataFrame(list(self.collection.find()))
            
            if '_id' in df.columns.to_list():
                df = df.drop(columns=['_id'])
            
            df.replace('na', np.nan)
            
            return df
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self, dataframe:pd.DataFrame):
        
        try:
            self.feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            #creating directory
            dir_name = os.path.dirname(self.feature_store_file_path)
            os.makedirs(dir_name, exist_ok=True)
            dataframe.to_csv(self.feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_into_train_test(self, dataframe:pd.DataFrame):
        
        try:
            train_set, test_set = train_test_split(dataframe, 
                                                   test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info('Performed train test split')
            
            self.train_set_file_path = self.data_ingestion_config.training_file_path
            self.test_set_file_path = self.data_ingestion_config.testing_file_path
            
            
            os.makedirs(os.path.dirname(self.train_set_file_path), exist_ok = True)
            os.makedirs(os.path.dirname(self.test_set_file_path), exist_ok = True)
            logging.info('Created folder structure to store train and test datasets')
            
            train_set.to_csv(self.train_set_file_path, index=False, header=True)
            test_set.to_csv(self.test_set_file_path, index=False, header=True)
            logging.info('Exported data into train and test datasets')
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    def initiate_data_ingestion(self):
        
        try:
            
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe=dataframe)
            self.split_data_into_train_test(dataframe=dataframe)
            dataingestionartifact = DataIngestionArtifact(self.train_set_file_path, self.test_set_file_path)
            return dataingestionartifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        


