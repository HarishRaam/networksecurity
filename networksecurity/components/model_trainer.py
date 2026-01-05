import os
import sys
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact

from networksecurity.utils.main_utils.utils import load_numpy_array_data
from networksecurity.utils.main_utils.utils import save_object, load_object, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    RandomForestClassifier,
    GradientBoostingClassifier
)
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import mlflow

class ModelTrainer:
    
    def __init__(self, data_transformation_artifact:DataTransformationArtifact,
                 model_trainer_config:ModelTrainerConfig):
        
        try:
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def track_mlflow(self, model, train_metric, test_metric, x_test, y_test):
        
        with mlflow.start_run():
            
            #Log training metric
            mlflow.log_metric("train_f1", train_metric.f1_score)
            mlflow.log_metric("train_precision", train_metric.precision_score)
            mlflow.log_metric("train_recall", train_metric.recall_score)
            
            #log test metric
            mlflow.log_metric("test_f1", test_metric.f1_score)
            mlflow.log_metric("test_precision", test_metric.precision_score)
            mlflow.log_metric("test_recall", test_metric.recall_score)
            
            #log model
            mlflow.sklearn.log_model(model, "model")
            
            #log best model
            model_name = type(model).__name__
            mlflow.set_tag("model_name", model_name)
            mlflow.log_params(model.get_params())
            
            #create and log confusion matrix
            y_pred = model.predict(x_test)
            cm = confusion_matrix(y_test, y_pred)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            disp.plot(ax = ax, cmap='Blues')
            plt.title(f"Confusion Matrix : {model_name}")
            
            with tempfile.TemporaryDirectory() as tmpdir:
                plot_path = os.path.join(tmpdir, "confusion_matrix.png")
                plt.savefig(plot_path)
                mlflow.log_artifact(plot_path)
                
            plt.close(fig)
            
        
    def model_trainer(self, x_train, y_train, x_test, y_test):
        
        try:
            
            models = {'Random Forest': RandomForestClassifier(),
                      'KNN' : KNeighborsClassifier(),
                      'Decision Tree': DecisionTreeClassifier(),
                      'Gradient Boosting' : GradientBoostingClassifier(),
                      'Logistic Regression' : LogisticRegression(),
                      'Adaboost' : AdaBoostClassifier()
                    }
            
            params={
            "Decision Tree": {
                'criterion':['gini', 'entropy'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.001],
                #'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                #'n_estimators': [64,128,256]
            },
            "Logistic Regression": {"solver": ["liblinear"]},
            "KNN" : {
            'n_neighbors': np.arange(1, 10, 2), # Test odd k values from 1 to 30
            #'weights': ['uniform', 'distance'],
            #'metric': ['euclidean', 'manhattan', 'minkowski']
            #'metric': ['euclidean', 'manhattan']
            },
            "Adaboost":{
                'learning_rate':[.1,.01,.001],
                #'n_estimators': [128,256]
            }
            }
        
            model_report, model_params = evaluate_models(x_train, y_train, x_test, y_test, models = models, params=params)
            
            best_score_model = max(model_report.items(), key=lambda item: item[1])
            
            best_model_name = best_score_model[0]
            best_model_score = best_score_model[1]
            best_model = models[best_model_name]
            best_params = model_params[best_model_name]
            
            logging.info(f'Best Model - {best_model_name}')
            logging.info(f'Best Params - {best_params}')
            
            best_model_with_params = best_model.set_params(**best_params)
            
            y_train_pred = best_model_with_params.predict(x_train)
            classification_train_metric = get_classification_score(y_train, y_train_pred)
            
        
            y_test_pred = best_model_with_params.predict(x_test)
            classification_test_metric = get_classification_score(y_test, y_test_pred)
            
            #Track the experiments with mlflow
            self.track_mlflow(model = best_model_with_params,
                              train_metric = classification_train_metric,
                              test_metric = classification_test_metric,
                              x_test = x_test,
                              y_test = y_test
                              )
            
            preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
            
            make_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(make_dir_path, exist_ok=True)
            
            network_model = NetworkModel(preprocessor=preprocessor, model=best_model_with_params)
            
            save_object(self.model_trainer_config.trained_model_file_path, obj=network_model)
            
            model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                                 train_metric_artifact=classification_train_metric,
                                 test_metric_artifact=classification_test_metric
                                )
            logging.info(f'Model Trainer Artifact - {model_trainer_artifact}')
            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_model_training(self) -> ModelTrainerArtifact:
        
        try:
            self.train_file_path = self.data_transformation_artifact.transformed_train_file_path
            self.test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            self.train_arr = load_numpy_array_data(self.train_file_path)
            self.test_arr = load_numpy_array_data(self.test_file_path)
            
            x_train, y_train, x_test, y_test = (self.train_arr[:, :-1], 
                                                self.train_arr[:, -1], 
                                                self.test_arr[:, :-1], 
                                                self.test_arr[:, -1]
                                                )
            
            model_trainer_artifact = self.model_trainer(x_train, y_train, x_test, y_test)
            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        