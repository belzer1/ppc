import visa
import time
from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
from scopecontrol import Tektronix_TBS2000_v2 as Tektronix_TBS2000
from serial import SerialException
import winsound

if __name__ == "__main__":  
    try:
        #Initialise the scope
        rm = visa.ResourceManager();
        Tektronix_TBS2000.Initialise(rm)
        Tektronix_TBS2000.horizontal_scale(1.0)
        Tektronix_TBS2000.single_shot()
        Tektronix_TBS2000.set_logger(logger.general)
        Tektronix_TBS2000.set_scale_3v3("CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("CH1:SCALE 0.250")
#        Tektronix_TBS2000.set_scale_3v3("CH2")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:EDGE:SOURCE CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:LEVEL 4.455")
        Tektronix_TBS2000.Tektronix_TBS2000.write("HOR:RECORDLENGTH 20000")

        #Connect to laser        
        ITLA = lasercommands.laser("COM8",9600,logger.general,logger.lasercomms)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.22)
        ITLA.SetPower(15.5)
        ITLA.SetSweepRange(140)
        ITLA.SetSweepRate(10)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
#                    
        ITLA.WaitForLaser()
        time.sleep(3) #3 secs recommended by Heino in case laser overshoots
        Tektronix_TBS2000.wait_till_ready()
    
#            Tektronix_TBS2000.trigger_manually()
        ITLA.SweepWithMonitor(1,Tektronix_TBS2000)
        t = time.time()
        Tektronix_TBS2000.wait_to_collect()
        Tektronix_TBS2000.capture()
#        Tektronix_TBS2000.single_shot()
        #wait ten seconds after end of sweep for laser to stabilise after it's temperature ramp
        while time.time() - t <10:
            time.sleep(0.1)
                   
        winsound.Beep(1500,200)
        
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
