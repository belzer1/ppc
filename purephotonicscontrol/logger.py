import logging
import time
import os
import datetime

class logger:
	def __init__(self, base_path=r"C:\\Users\\lab\\Berrington\\DataLibrary\\"):
		now = datetime.datetime.now()
		path = base_path + now.strftime("%Y\\%m\\%d\\")
		if not os.path.isdir(path):
		    os.makedirs(path)
		self.formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")

		self.general = self.setup_logger('general', 'general.log')
		self.lasercomms = self.setup_logger('lasercomms', 'lasercomms.log')

	def setup_logger(self,name, log_file, level=logging.INFO):
	    """Function setup as many loggers as you want"""
	    
	    handler = logging.FileHandler(log_file)        
	    
	    handler.setFormatter(self.formatter)

	    logger = logging.getLogger(name)
	    logger.setLevel(level)
	    logger.addHandler(handler)

	    return logger

	def shutdown():
		logging.shutdown()

	   
	#Set up all the logging stuff