import os
import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (TrainingPipelineConfig,
                                                  DataIngestionConfig,
                                                  DataValidationConfig,
                                                  DataTransformationConfig,
                                                  ModelTrainerConfig)

from networksecurity.entity.artifact_entity import (DataIngestionArtifact,
                                                    DataValidationArtifact,
                                                    DataTransformationArtifact,
                                                    ModelTrainerArtifact)


class TrainingPipeline:
    
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
    
    def start_data_ingestion(self):
        
        try:
            
            self.data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)
            data_ingestion = DataIngestion(self.data_ingestion_config)
            logging.info('Starting Data Ingestion')
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f'Data Ingestion completed with Data ingestion artifact - {data_ingestion_artifact}')
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_validation(self, data_ingestion_artifact:DataIngestionArtifact):
        
        try:
            self.data_validation_config = DataValidationConfig(self.training_pipeline_config)
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                             data_validation_config=self.data_validation_config)
            logging.info('Starting Data Validation')
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f'Data validation completed with data validation artifact - {data_validation_artifact}')
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_transformation(self, data_validation_artifact:DataValidationArtifact):
        
        try:
            self.data_transformation_config = DataTransformationConfig(self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
                                                     data_transformation_config=self.data_transformation_config)
            logging.info('Starting Data Transformation')
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info(f'Data transformation completed with data transformation artifact {data_transformation_artifact}')
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_model_trainer(self, data_transformation_artifact:DataTransformationArtifact):
        
        try:
            self.model_trainer_config = ModelTrainerConfig(self.training_pipeline_config)
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                         model_trainer_config=self.model_trainer_config)
            logging.info('Starting Model Training')
            model_trainer_artifact = model_trainer.initiate_model_training()
            logging.info(f"Model training complete with model trainer artifact {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException from e
        
    
        
    
        
    
    
    

