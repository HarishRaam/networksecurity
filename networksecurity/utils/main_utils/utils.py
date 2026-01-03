import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys
import numpy as np
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

def read_yaml_file(file_path:str) -> dict:
    
    try:
        with open(file_path, 'rb') as yaml_file:
            logging.info("Reading yaml file")
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def write_yaml_file(file_path:str, content:object, replace:bool=False) -> None:
    
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file_obj:
            yaml.dump(content, file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_numpy_array_data(file_path:str, array:np.array):
    
    '''
    Save numpy array data to file
    file_path: str location of file to save
    array : np.array to save
    '''
    
    try:
        dir_name = os.path.dirname(file_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path:str):
    
    try:
        if not file_path:
            raise Exception(f'File path {file_path} does not exist')
        
        with open(file_path, 'rb') as file_obj:
            return np.load(file_path)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path:str, obj:object):
    
    try:
        logging.info("Saving Object using save_object method of utils class")
        dir_name = os.path.dirname(file_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save object method of main utils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path:str) -> object:
    
    try:
        logging.info("Reading the object using load_object method of utils class")
        if not os.path.exists(file_path):
            raise Exception(f'The file path {file_path} does not exist')
        
        with open(file_path, 'rb') as file_obj:
            logging.info("Loading file object")
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def evaluate_models(x_train, y_train, x_test, y_test, models, params) -> tuple:
    
    try:
        report = {}
        parameters = {}
        
        for key, value in models.items():
            model = value
            model_param = params[key]
            logging.info(f"Training model {key} with parameters {model_param}")
            
            gs = GridSearchCV(model, param_grid=model_param, cv=3, n_jobs=1)
            gs.fit(x_train, y_train)
            
            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)
            
            y_train_pred = model.predict(x_train)
            y_test_pred = model.predict(x_test)
            
            #model_train_accuracy = accuracy_score(y_train, y_train_pred)
            model_test_accuracy = accuracy_score(y_test, y_test_pred)
            
            report[key] = model_test_accuracy
            parameters[key] = gs.best_params_
            
        return report, parameters
                
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    