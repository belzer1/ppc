import ITLA_Wrap
import DualLogger
import time
from serial import SerialException

def shutdown_sequence():
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
    ITLA.sercon.close()        
    DualLogger.logging.shutdown()

if __name__ == "__main__":                            
    try:
        ITLA = ITLA_Wrap.ITLA_Class("COM4",9600,'MCU',DualLogger.general,DualLogger.lasercomms)
         
        #Probe laser and check it's happy
        ITLA.ProbeLaser()
        #Turn laser off before setting frequency is easiest
        ITLA.EnableLaser(False)
        #Set frequency in THz
        ITLA.SetFrequency(195.50)
        #Set power in dBm
        ITLA.SetPower(10.0)
        #Set sweep range in GHz
        ITLA.SetSweepRange(120)
        #Set sweep rare in GHZ/s
        ITLA.SetSweepRate(20)    
        
        ITLA.EnableLaser(True)
        
        ITLA.EnableWhisperMode(True)
    
        time.sleep(1)
    
        ITLA.EnableSweep(True)
        ITLA.EnableTeensyMonitor(True)
    
        time.sleep(100)
        #DO SCIENCE
    
        #turn everything off
        shutdown_sequence()

    except KeyboardInterrupt:
        DualLogger.general.info("Sequence interupted by user, shutting down laser")
        print("Sequence interupted by user, shutting down laser")
        shutdown_sequence()
                
    except SerialException:
        print('Port already open')

    except Exception as err:
        DualLogger.general.info("An error has occured, shutting down laser")
        DualLogger.general.error(err)
        print("An error has occured, shutting down laser")
        shutdown_sequence()
        print(err)