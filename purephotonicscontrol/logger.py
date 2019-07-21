import logging
import time
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    
    handler = logging.FileHandler(log_file)        
    
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

if not os.path.exists("logs"):
    os.makedirs("logs")
    
    
#Set up all the logging stuff
formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
general = setup_logger('general', 'logs/general'+time.strftime('%d%b%Y')+'.log')
lasercomms = setup_logger('lasercomms', 'logs/lasercomms'+time.strftime('%d%b%Y')+'.log')
general.info('Starting another experiment')
lasercomms.info('Starting another experiment')