from purephotonicscontrol.purephotonicscontrol import lasercommands, logger, clean_scan_parameters
import time

if __name__ == "__main__":  
    try:       
        general = logger.logger('general',base_path='C:/Users/lab/Berrington/DataLibrary/')
        lasercomms = logger.logger('lasercomms',base_path='C:/Users/lab/Berrington/DataLibrary/')
        
        #Import all the currents/temperatures for the jump sequences
        jump_setpoints = clean_scan_parameters.Parameters('17.0dBm')
        jump_setpoints.set_frequency_range(191.5,191.8,0.1)
        
        #Connect to laser
        ITLA = lasercommands.laser("COM4",general.log,lasercomms.log)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.50)
        ITLA.SetPower(17.0)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
        while True:
            for idx, _ in enumerate(jump_setpoints.frequency):            
                ITLA.SetNextFrequency(jump_setpoints.frequency[idx])
                ITLA.SetNextSled(jump_setpoints.sled[idx])
                ITLA.SetNextCurrent(jump_setpoints.current[idx])
                ITLA.ExecuteJump()
                ITLA.WaitToStabilise(0.1)
                    
                ITLA.FineTuneFrequency(0)
                ITLA.WaitForLaser()
                
                #Do science
                time.sleep(3)
        
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