from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils import utils

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import sys
import os

class DataValidation:
    
    #Step 1. Read train and test data output from data ingestion
    #Step 2. Validate number of columns present in train and test datasets again schema config
    #Step 3. Check whether all numerical columns exist or not
    
    def __init__(self, 
                 data_ingestion_artifact:DataIngestionArtifact, 
                 data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = utils.read_yaml_file(SCHEMA_FILE_PATH)
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path:str)-> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    def validate_number_of_columns(self, dataframe:pd.DataFrame):
        
        try:
            number_of_expected_columns = len(self._schema_config['columns'])
            logging.info(f'Required number of columns - {number_of_expected_columns}')
            
            number_of_columns_present = len(dataframe.columns)
            logging.info(f'Number of columns present - {number_of_columns_present}')
            
            if number_of_expected_columns == number_of_columns_present:
                return True
            
            return False
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_numerical_columns(self, dataframe:pd.DataFrame):
        
        try:
            number_of_expected_numerical_columnns = len(self._schema_config['numerical_columns'])
            logging.info(f'Required number of numerical columns - {number_of_expected_numerical_columnns}')
            
            number_of_numerical_columns = len(dataframe.select_dtypes(exclude=['O']).columns)
            logging.info(f'Number of numerical columns present - {number_of_numerical_columns}')
            
            if number_of_numerical_columns == number_of_expected_numerical_columnns:
                return True
            return False
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    def detect_data_drift(self, base_df, current_df, threshold=0.05)->bool:
        try:
            report = {}
            data_drift = False
            for column in base_df.columns:
                
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if is_same_dist.pvalue > threshold:
                    diff_in_dist_found = False
                else:
                    diff_in_dist_found = True
                    data_drift = True
                report.update({column:{"pvalue":float(is_same_dist.pvalue), "drift_status":diff_in_dist_found}})
                
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            drift_report_dir = os.path.dirname(drift_report_file_path)
            os.makedirs(drift_report_dir, exist_ok=True)
            utils.write_yaml_file(file_path = drift_report_file_path, content=report)
            return data_drift
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
                    
    
        
    def initiate_data_validation(self) -> DataValidationConfig:
        
        try:
            error_message = None
            
            train_filepath = self.data_ingestion_artifact.train_file_path
            test_filepath = self.data_ingestion_artifact.test_file_path
            
            #Read train and test data
            train_df = DataValidation.read_data(train_filepath)
            test_df = DataValidation.read_data(test_filepath)
            
            #Validate number of columns
            no_of_columns_train_status = self.validate_number_of_columns(train_df)
            if not no_of_columns_train_status:
                error_message = 'Train dataset does not contain all columns'
                
            no_of_columns_test_status=self.validate_number_of_columns(test_df)
            if not no_of_columns_test_status:
                error_message = 'Test dataset does not contain all columns'
                
            #Validate numerical columns exist
            numerical_cols_train_status = self.validate_numerical_columns(train_df)
            if not numerical_cols_train_status:
                error_message = 'Train dataset doess not have all numerical columns'
                
            numerical_cols_test_status = self.validate_numerical_columns(test_df)
            if not numerical_cols_test_status:
                error_message = 'Test dataset doess not have all numerical columns'
                
            #Check datadrift
            status = self.detect_data_drift(base_df=train_df, current_df=test_df)
            
            valid_dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(valid_dir_path, exist_ok=True)
            
            invalid_dir_path = os.path.dirname(self.data_validation_config.invalid_train_file_path)
            os.makedirs(invalid_dir_path, exist_ok=True)
            
    
            if status or bool(error_message):
                train_df.to_csv(self.data_validation_config.invalid_train_file_path, index=False, header=True)
                test_df.to_csv(self.data_validation_config.invalid_test_file_path, index=False, header = True)
            else:
                train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
                test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header = True)
            
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path = self.data_validation_config.valid_train_file_path,
                valid_test_file_path = self.data_validation_config.valid_test_file_path,
                invalid_train_file_path= self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            
            return data_validation_artifact
            
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
