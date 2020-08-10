from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
import time

if __name__ == "__main__":                            
    try:
        general = logger.logger('general',base_path='C:/Users/lab/Berrington/DataLibrary/')
        lasercomms = logger.logger('lasercomms',base_path='C:/Users/lab/Berrington/DataLibrary/')
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
        #Probe laser and check it's happy
        ITLA.ProbeLaser()
        #Turn laser off before setting frequency is easiest
        ITLA.EnableLaser(False)
        #Set frequency in THz
        ITLA.SetFrequency(195.935)   
        #Set power in dBm
        ITLA.SetPower(10.0)
        #Set sweep range in GHz
        ITLA.SetSweepRange(140)
        #Set sweep rate in GHZ/s
        ITLA.SetSweepRate(10)  
        
        ITLA.EnableLaser(True)
        
        ITLA.EnableWhisperMode(True)
    
        time.sleep(1)
    
        ITLA.EnableSweep(True)
    
        time.sleep(10)
        #Do science
    
        #turn laser off (this is optional)
        ITLA.Shutdown()
      
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