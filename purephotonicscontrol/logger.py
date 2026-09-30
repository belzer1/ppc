import logging
import getpass
import datetime
import __main__
from pathlib import Path
class logger:
    def __init__(self, name, base_path=""):
        if base_path == "":
            base_path=Path(input("Enter base path for log files: ")).resolve()
        now = datetime.datetime.now()
        path = base_path + now.strftime("%Y\\%m\\%d\\")
        if not base_path.is_dir():
            base_path.mkdir(parents=True, exist_ok=True)
        self.formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")

        self.log,self.handler = self.setup_logger(name, path+name+'.log')
        self.log.info('Begining experiment ' + __main__.__file__)
#        self.lasercomms,self.lasercomms_handler = self.setup_logger('lasercomms', path+'lasercomms.log')
#        self.general.info('Begining experiment ' + __main__.__file__)

    def setup_logger(self,name, log_file, level=logging.INFO):
        """Function setup as many loggers as you want"""
        
        handler = logging.FileHandler(log_file)        
        
        handler.setFormatter(self.formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger, handler

    def shutdown(self):
        self.log.info('Experiment finished\n')
        self.log.removeHandler(self.handler)
        del self.log, self.handler