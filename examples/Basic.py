from purephotonicscontrol import lasercommands, logger
import time
from serial import SerialException

if __name__ == "__main__":  
    try:
        ITLA = lasercommands.laser("COM8",9600,logger.general,logger.lasercomms)
        
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
#        DO SCIENCE
        
#        turn laser off (optional)
        ITLA.Shutdown()
        
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