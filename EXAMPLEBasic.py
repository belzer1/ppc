import ITLA_Wrap
import time
import logging

def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    
    handler = logging.FileHandler(log_file)        
    
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

if __name__ == "__main__":  
    
    #Set up all the logging stuff
    formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
    general_logger = setup_logger('general', 'general'+time.strftime('%d%b%Y')+'.log')
    lasercomms_logger = setup_logger('lasercomms', 'lasercomms'+time.strftime('%d%b%Y')+'.log')
    general_logger.info('Starting another experiment')
    lasercomms_logger.info('Starting another experiment')
        
    
    # ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
#    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM0",115200,'MCU')
    ITLA = ITLA_Wrap.ITLA_Class("COM4",9600,'MCU',general_logger,lasercomms_logger)

    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    #Turn laser off before setting frequency is easiest
    ITLA.EnableLaser(False)
    #Set frequency in THz
    ITLA.SetFrequency(191.50)
    #Set power in dBm
    ITLA.SetPower(16.0)
    
    ITLA.EnableLaser(True)
    
    ITLA.EnableWhisperMode(True)

    time.sleep(100)
    #DO SCIENCE

    #turn everything off
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
    ITLA.sercon.close()