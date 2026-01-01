import sys
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

if __name__ == "__main__":
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        dataingestion = DataIngestion(data_ingestion_config=dataingestionconfig)
        logging.info('Initiating data ingestion')
        dataingestionartifact = dataingestion.initiate_data_ingestion()
        logging.info('Data initiation completed')
        
        logging.info("Initiating data validation")
        datavalidationconfig = DataValidationConfig(training_pipeline_config=trainingpipelineconfig)
        datavalidation = DataValidation(data_ingestion_artifact=dataingestionartifact, data_validation_config=datavalidationconfig)
        datavalidationartifact = datavalidation.initiate_data_validation()
        print(datavalidationartifact)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
        

