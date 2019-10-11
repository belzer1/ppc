from purephotonicscontrol.purephotonicscontrol import lasercommands, logger
from clean_scan_parameters import clean_scan_parameters
import time
    
### CODE NOT TESTED SINCE LAST EDIT!!!

if __name__ == "__main__":
#    try:
        general = logger.logger('general')
        lasercomms = logger.logger('lasercomms')
        
        ITLA = lasercommands.laser("COM8",general.log,lasercomms.log)
        
        #Import all the currents/temperatures for the jump sequences
        scan_setpoints = clean_scan_parameters.Parameters('7.0dBm')
        scan_setpoints.set_frequency_range(195,196,0.1)
        
        ITLA.EnableLaser(False)
        time.sleep(5)        
        ITLA.SetScanSled(32000)
        ITLA.LockSled()
        ITLA.SetCurrentAdjust(scan_setpoints.adjust1[0],scan_setpoints.adjust2[0])
        ITLA.SetFrequency(195)
        ITLA.SetScanAmplitude(120)
        ITLA.SetSweepRate(20)    
        ITLA.SetPower(10)
        ITLA.SetChannel1()
        ITLA.EnableLaser(True)
        time.sleep(1)
        ITLA.EnableCleanMode(True)
        time.sleep(1)
        ITLA.EnableScan(True)
        scan_status = 1 #odd value means the laser is scanning 
        
        for idx, freq in enumerate(scan_setpoints.frequency):
            ITLA.EnableTeensyMonitor(False)
            print('Loading next data point, centred on {} THz'.format(freq))
            ITLA.SetScanSled(scan_setpoints.sled[idx])
            ITLA.SetFilter1(scan_setpoints.filter1[idx])
            ITLA.SetFilter2(scan_setpoints.filter2[idx])
            ITLA.SetCurrentAdjust(scan_setpoints.adjust1[idx],scan_setpoints.adjust2[idx])
            ITLA.SetCurrent(scan_setpoints.current[idx])
            #TODO fix up the scan status business
            scan_status = 1
            ITLA.EnableTeensyMonitor(True)
            while scan_status%2:   
                if ITLA.sercon.inWaiting() > 0:
                    scan_status = ITLA.TeensyReadStatus()
                time.sleep(0.0001)

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