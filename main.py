import sys
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
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
        print(dataingestionartifact)
        logging.info('Data initiation completed')
        
        logging.info("Initiating data validation")
        datavalidationconfig = DataValidationConfig(training_pipeline_config=trainingpipelineconfig)
        datavalidation = DataValidation(data_ingestion_artifact=dataingestionartifact, data_validation_config=datavalidationconfig)
        datavalidationartifact = datavalidation.initiate_data_validation()
        print(datavalidationartifact)
        logging.info("Data validation completed")
        
        logging.info("Initiating data transformation")
        datatransformationconfig = DataTransformationConfig(training_pipeline_config=trainingpipelineconfig)
        datatransformation = DataTransformation(data_validation_artifact=datavalidationartifact,
                                                data_transformation_config=datatransformationconfig)
        datatransformationartifact = datatransformation.initiate_data_transformation()
        print(datatransformationartifact)
        logging.info("Data transformation completed")
        
        logging.info('Model training started')
        modeltrainerconfig = ModelTrainerConfig(training_pipleline_config=trainingpipelineconfig)
        model_trainer = ModelTrainer(data_transformation_artifact=datatransformationartifact, 
                     model_trainer_config=modeltrainerconfig)
        modeltrainerartifact = model_trainer.initiate_model_training()
        logging.info("Model training artifact created")
        print(modeltrainerartifact)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)
        

