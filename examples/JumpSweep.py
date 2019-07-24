from purephotonicscontrol import lasercommands, logger
import CleanScanParameters
import time
from serial import SerialException
    
if __name__ == "__main__":  
    try:
        ITLA = lasercommands.laser("COM8",9600,logger.general,logger.lasercomms)
        
        #Import all the currents/temperatures for the jump sequences
        CleanScan = CleanScanParameters.CleanScanParameters('7.0dBm')
        CleanScan.set_frequency_range(191.5,198.5,0.1)        
    
        #Probe laser and check it's happy
        ITLA.ProbeLaser()
        #Turn laser off before setting frequency is easiest
        ITLA.EnableLaser(False)
        #Set frequency in THz
        ITLA.SetFrequency(195.50)
        #Set power in dBm
        ITLA.SetPower(10.0)
        #Set sweep range in GHz
        ITLA.SetSweepRange(140)
        #Set sweep rate in GHZ/s
        ITLA.SetSweepRate(10)   
        
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
        
        for idx, _ in enumerate(CleanScan.frequency):            
            print('Jumping to {} THz'.format(CleanScan.frequency[idx]))
            ITLA.SetNextFrequency(CleanScan.frequency[idx])
            ITLA.SetNextSled(CleanScan.sled[idx])
            ITLA.SetNextCurrent(CleanScan.current[idx])
            ITLA.ExecuteJump()
            ITLA.WaitToStabilise(0.5)
                
            ITLA.FineTuneFrequency(0)
            ITLA.WaitForLaser()
            ITLA.EnableSweep(False) #Make sure the pure jump function is finished
            time.sleep(5) #3 secs recommended by Heino in case laser overshoots
            ITLA.SweepWithMonitor(1)
            #wait ten seconds after end of sweep for laser to stabilise after it's temperature ramp
            t = time.time()
            while time.time() - t <10:
                time.sleep(0.1)

    
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