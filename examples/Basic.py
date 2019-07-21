if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from purephotonicscontrol import lasercommands, logger, shutdown
import time
from serial import SerialException

if __name__ == "__main__":  
    try:
        shutdown.laser()

        ITLA = lasercommands.laser("COM4",9600,'MCU',logger.general,logger.lasercomms)
        
        #Probe laser and check it's happy
        ITLA.ProbeLaser()
        #Turn laser off before setting frequency is easiest
        ITLA.EnableLaser(False)
        #Set frequency in THz
        ITLA.SetFrequency(191.50)
        #Set power in dBm
        ITLA.SetPower(7.0)
        
        ITLA.EnableLaser(True)
        
        ITLA.EnableWhisperMode(True)
        
        time.sleep(100)
        #DO SCIENCE
        
        #turn everything off
        shutdown.laser()
        shutdown.logs()
        
    except KeyboardInterrupt:
        logger.general.info("Sequence interupted by user, shutting down laser")
        print("Sequence interupted by user, shutting down laser")
        shutdown.laser()
        shutdown.logs()
                
    except SerialException as err:
        print(err)

    except Exception as err:
        logger.general.info("An unknown error has occured, shutting down laser")
        logger.general.error(err)
        print("An unknown error has occured, shutting down laser")
        shutdown.laser()
        shutdown.logs()
        print(err)  