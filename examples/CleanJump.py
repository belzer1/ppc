if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from purephotonicscontrol import lasercommands, logger
from clean_scan_parameters import clean_scan_parameters
import time
from serial import SerialException

if __name__ == "__main__":  
    try:        
        #Import all the currents/temperatures for the jump sequences
        jump_setpoints = clean_scan_parameters.Parameters('7.0dBm')
        jump_setpoints.set_frequency_range(191.5,198.5,0.1)
        
        #Connect to laser
        ITLA = lasercommands.laser("COM8",9600,logger.general,logger.lasercomms)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.50)
        ITLA.SetPower(10.0)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
#        
        for idx, _ in enumerate(jump_setpoints.frequency):            
            ITLA.SetNextFrequency(jump_setpoints.frequency[idx])
            ITLA.SetNextSled(jump_setpoints.sled[idx])
            ITLA.SetNextCurrent(jump_setpoints.current[idx])
            ITLA.ExecuteJump()
            ITLA.WaitToStabilise(0.1)
                
            ITLA.FineTuneFrequency(0)
            ITLA.WaitForLaser()
            
            #Do science
            time.sleep(10)
        
    except KeyboardInterrupt:
        logger.general.info("Sequence interupted by user, shutting down laser")
        print("Sequence interupted by user, shutting down laser")
        ITLA.Shutdown()        
                
    except SerialException as err:
        print(err)

    except Exception as err:
        logger.general.info("An unknown error has occured, shutting down laser")
        logger.general.error(err)
        print("An unknown error has occured, shutting down laser")
        ITLA.Shutdown()
        print(err)  
        
    finally:        
        ITLA.sercon.close()
        logger.logging.shutdown()