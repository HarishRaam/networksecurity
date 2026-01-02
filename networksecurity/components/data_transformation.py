import sys
import os
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object

class DataTransformation:
    
    #Step 1. 
    
    def __init__(self, data_validation_artifact:DataValidationArtifact, 
                 data_transformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def read_data(file_path:str):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    
    def get_transformer_object(cls)->Pipeline:
        
        logging.info('Entered get_transformer_object method')
        
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f'KNN Imputer initialized with parameters - {DATA_TRANSFORMATION_IMPUTER_PARAMS}')
            
            processor = Pipeline([('KNNImputer', imputer)])
            
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
        
        
        
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        
        logging.info("Entered initiate data transformation method")
        
        try:
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)
            
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)
            
            preprocessor = self.get_transformer_object()
            transformed_input_train_feature = preprocessor.fit_transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor.transform(input_feature_test_df)
            
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]
            
            #save numpy array
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, obj=preprocessor)
            
            #preparing artifacts
            self.data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path = self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path = self.data_transformation_config.transformed_test_file_path,
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path
            )
            
            return self.data_transformation_artifact
            
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    
        
        
        


