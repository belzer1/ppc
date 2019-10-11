import visa
import time
from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
from scopecontrol import Tektronix_TBS2000
import winsound

if __name__ == "__main__":  
    try:
        if 'ITLA' in locals():
            ITLA.Shutdown()
            ITLA.sercon.close()
            del ITLA   
        general = logger.logger('general')
        lasercomms = logger.logger('lasercomms')
        
        #Initialise the scope       
        rm = visa.ResourceManager();
        Tektronix_TBS2000.Initialise(rm,general.log)
        Tektronix_TBS2000.horizontal_scale(1.0)
        Tektronix_TBS2000.single_shot()
        Tektronix_TBS2000.set_scale_3v3("CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("CH1:SCALE 0.250")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:EDGE:SOURCE CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:LEVEL 4.455")
        Tektronix_TBS2000.Tektronix_TBS2000.write("HOR:RECORDLENGTH 20000")
        
        #Connect to laser        
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(194.0)
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
            general.log.info('Shutting down laser')
            print('Shutting down laser')
            ITLA.Shutdown()       

    except Exception as err:
        general.log.error(err)
        print(err)
        if 'ITLA' in locals():
            general.log.info('Shutting down laser')
            print('Shutting down laser')
            ITLA.Shutdown()
        
    finally:            
        general.shutdown()
        lasercomms.shutdown()