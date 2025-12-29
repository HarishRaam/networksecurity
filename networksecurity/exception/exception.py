import sys
from networksecurity.logging.logger import logging

class NetworkSecurityException(Exception):
    
    def __init__(self, error_message, error_detail:sys):
        
        self.error_message = error_message
        _, _, exc_tb = error_detail.exc_info()
        self.lineno = exc_tb.tb_lineno
        self.filename = exc_tb.tb_frame.f_code.co_filename
        
    def __str__(self):
        
        return f"Error occured in script - [{self.filename}] line number - [{self.lineno}] \
                error message - [{self.error_message}]"
                

if __name__ == "__main__":
    try:
        logging.info('Trying division by zero')
        a = 1/0
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    
        
        
    
    