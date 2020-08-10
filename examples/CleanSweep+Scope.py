import visa
import time
from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
from scopecontrol import Tektronix_TBS2000
import winsound

if __name__ == "__main__":  
    try:
        general = logger.logger('general',base_path='C:/Users/lab/Berrington/DataLibrary/')
        lasercomms = logger.logger('lasercomms',base_path='C:/Users/lab/Berrington/DataLibrary/'))
        
        #Initialise the scope       
        rm = visa.ResourceManager();
        Tektronix_TBS2000.Initialise(rm,general.log)
        
        #Connect to laser        
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.93)
        ITLA.SetPower(10.0)
        ITLA.SetSweepRange(140)
        ITLA.SetSweepRate(10)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
#                    
        ITLA.WaitForLaser()
        time.sleep(3) #3 secs recommended by Heino in case laser overshoots
        Tektronix_TBS2000.wait_until_ready()
    
#            Tektronix_TBS2000.trigger_manually()
        ITLA.SingleSweep(Tektronix_TBS2000)
        Tektronix_TBS2000.wait_to_collect()
        Tektronix_TBS2000.capture()

        winsound.Beep(1500,200)
        
    except KeyboardInterrupt:
        general.log.info("Sequence interupted by user, shutting down laser")
        print("Sequence interupted by user, shutting down laser")
        if 'ITLA' in locals():
            ITLA.Shutdown()       

    except Exception as err:
        general.log.error(err)
        print(err)
        if 'ITLA' in locals():
            ITLA.Shutdown()
        
    finally:
        #Always close the laser serial port and the logging handles
        if 'ITLA' in locals():
            ITLA.sercon.close()
        if 'general' in locals():
            general.shutdown()
        if 'lasercomms' in locals():
            lasercomms.shutdown()