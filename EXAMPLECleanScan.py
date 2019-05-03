import ITLA_Wrap
import time
import DualLogger
import CleanScanParameters
from serial import SerialException

def shutdown_sequence():
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableScan(False)
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
    ITLA.sercon.close()        
    DualLogger.logging.shutdown()
    
if __name__ == "__main__":
    try:
        ITLA = ITLA_Wrap.ITLA_Class("COM4",9600,'MCU',DualLogger.general,DualLogger.lasercomms)
        
        #Import all the currents/temperatures for the jump sequences
        CleanScan = CleanScanParameters.CleanScanParameters('10.0dBm')
        CleanScan.set_frequency_range(195,196,0.1)
        
        ITLA.EnableLaser(False)
        time.sleep(5)        
        ITLA.SetScanSled(32000)
        ITLA.LockSled()
        ITLA.SetCurrentAdjust(CleanScan.adjust1[0],CleanScan.adjust2[0])
        ITLA.SetFrequency(195)
        ITLA.SetScanAmplitude(120)
        ITLA.SetSweepRate(20000)    
        ITLA.SetPower(10)
        ITLA.SetChannel1()
        ITLA.EnableLaser(True)
        time.sleep(1)
        ITLA.EnableCleanMode(True)
        time.sleep(1)
        ITLA.EnableScan(True)
        scan_status = 1 #odd value means the laser is scanning 
        
        for idx, freq in enumerate(CleanScan.frequency):
            ITLA.EnableTeensyMonitor(False)
            print('Loading next data point, centred on {} THz'.format(freq))
            ITLA.SetScanSled(CleanScan.sled[idx])
            ITLA.SetFilter1(CleanScan.filter1[idx])
            ITLA.SetFilter2(CleanScan.filter2[idx])
            ITLA.SetCurrentAdjust(CleanScan.adjust1[idx],CleanScan.adjust2[idx])
            ITLA.SetCurrent(CleanScan.current[idx])
            scan_status = 1
            ITLA.EnableTeensyMonitor(True)
            while scan_status%2:            
                if ITLA.sercon.inWaiting() > 0:
                    scan_status = ITLA.TeensyReadStatus()
                time.sleep(0.0001)
                
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