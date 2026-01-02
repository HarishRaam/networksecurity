import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys
import numpy as np
import pickle

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
    
def save_object(file_path:str, obj:object):
    
    try:
        logging.info("Entered the save object method of main utils class")
        dir_name = os.path.dirname(file_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save object method of main utils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
