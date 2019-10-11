import visa
import time
from purephotonicscontrol.purephotonicscontrol import lasercommands, logger, clean_scan_parameters
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
#        Tektronix_TBS2000.set_scale_3v3("CH2")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:EDGE:SOURCE CH1")
        Tektronix_TBS2000.Tektronix_TBS2000.write("TRIGGER:A:LEVEL 4.455")
        Tektronix_TBS2000.Tektronix_TBS2000.write("HOR:RECORDLENGTH 20000")
        
        
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
        
#        for repeat in (1,2,3):
#        
        for idx, _ in enumerate(jump_setpoints.frequency):
#            if idx+72 not in [77,86,99,113,114,115]:
#                continue
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
            Tektronix_TBS2000.wait_until_ready()
        
#            Tektronix_TBS2000.trigger_manually()
            ITLA.SingleSweep(Tektronix_TBS2000)
            t = time.time()
            Tektronix_TBS2000.wait_to_collect()
            Tektronix_TBS2000.capture()
            Tektronix_TBS2000.single_shot()
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