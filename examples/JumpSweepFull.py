if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from purephotonicscontrol import lasercommands, logger, shutdown
import sys
import visa
import time
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
        Tektronix_TBS2000.Tektronix_TBS2000.write("CH1:SCALE 0.450")
        Tektronix_TBS2000.set_scale_3v3("CH2")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:EDGE:SOURCE CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:LEVEL 4.455")
        Tektronix_TBS2000.Tektronix_TBS2000.write("HOR:RECORDLENGTH 20000")
        
        #Import all the currents/temperatures for the jump sequences
        CleanScan = CleanScanParameters.CleanScanParameters('7.0dBm')
        CleanScan.set_frequency_range(191.5,198.5,0.1)
        
        #Connect to laser
        shutdown.close_previous_session()
        ITLA = lasercommands.laser("COM4",9600,'MCU',logger.general,logger.lasercomms)
        
        #Set up laser initial parameters
        ITLA.ProbeLaser()
        ITLA.EnableLaser(False)
        ITLA.SetFrequency(195.50)
        ITLA.SetPower(10.0)
        ITLA.SetSweepRange(140)
        ITLA.SetSweepRate(10)
        ITLA.EnableLaser(True)
        ITLA.EnableWhisperMode(True)
#        
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
            time.sleep(3) #3 secs recommended by Heino in case laser overshoots
            Tektronix_TBS2000.wait_till_ready()
        
#            Tektronix_TBS2000.trigger_manually()
            ITLA.SweepWithMonitor(1,Tektronix_TBS2000)
            t = time.time()
            Tektronix_TBS2000.wait_to_collect()
            Tektronix_TBS2000.capture()
            Tektronix_TBS2000.single_shot()
            #wait ten seconds after end of sweep for laser to stabilise after it's temperature ramp
            while time.time() - t <10:
                time.sleep(0.1)
                
        shutdown.shutdown()        
        winsound.Beep(1500,200)
        
    except KeyboardInterrupt:
        logger.general.info("Sequence interupted by user, shutting down laser")
        print("Sequence interupted by user, shutting down laser")
        shutdown.shutdown()
                
    except SerialException as err:
        print(err)

    except Exception as err:
        logger.general.info("An unknown error has occured, shutting down laser")
        logger.general.error(err)
        print("An unknown error has occured, shutting down laser")
        shutdown.shutdown_sequence()
        print(err)
