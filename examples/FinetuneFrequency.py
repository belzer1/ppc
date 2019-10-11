from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
import time
import numpy as np

if __name__ == "__main__":  
    try:
        if 'ITLA' in locals():
            ITLA.Shutdown()
            ITLA.sercon.close()
            del ITLA           
        general = logger.logger('general')
        lasercomms = logger.logger('lasercomms')
        
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
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
        time.sleep(5)
        
        for frequency in np.linspace(-1,1,21):
            ITLA.FineTuneFrequency(frequency)
            ITLA.WaitForLaser()
            time.sleep(5)
            #take measurement
            
#        turn laser off (optional)
        ITLA.Shutdown()
        
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