import visa
import time
from purephotonicscontrol.purephotonicscontrol import lasercommands, logger, clean_scan_parameters
import winsound
    
if __name__ == "__main__":  
    try:
        if 'ITLA' in locals():
            ITLA.Shutdown()
            ITLA.sercon.close()
            del ITLA           
        general = logger.logger('general')
        lasercomms = logger.logger('lasercomms')
        
        #Import all the currents/temperatures for the jump sequences
        jump_setpoints = clean_scan_parameters.Parameters('7.0dBm')
        jump_setpoints.set_frequency_range(191.5,191.8,0.1)
        #Connect to laser
        
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.22)
        ITLA.SetPower(10.0)
        ITLA.SetSweepRange(140)
        ITLA.SetSweepRate(10)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
  
        for idx, _ in enumerate(jump_setpoints.frequency):
            print('Jumping to {} THz'.format(jump_setpoints.frequency[idx]))
            ITLA.SetNextFrequency(jump_setpoints.frequency[idx])
            ITLA.SetNextSled(jump_setpoints.sled[idx])
            ITLA.SetNextCurrent(jump_setpoints.current[idx])
            ITLA.ExecuteJump()
            ITLA.WaitToStabilise(0.5)
                
            ITLA.FineTuneFrequency(0)
            ITLA.WaitForLaser()
            ITLA.EnableSweep(False) #Make sure the pure jump function is finished
            time.sleep(3) #3 secs recommended by Heino in case laser overshoots
        
            ITLA.SingleSweep()
            t = time.time()
            #wait ten seconds after end of sweep for laser to stabilise after it's temperature ramp
            while time.time() - t <10:
                time.sleep(0.1)
                        
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