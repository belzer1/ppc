import ITLA_Wrap
import time
import logging

if __name__ == "__main__":  
    logging.basicConfig(level=logging.INFO, filename="logfile_"+time.strftime('%d%b%Y'), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")                          
    
    ITLA = ITLA_Wrap.ITLA_Class("COM4",9600,'MCU')
#     ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
#    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM0",115200,'MCU')

    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    #Turn laser off before setting frequency is easiest
    ITLA.EnableLaser(False)
    #Set frequency in THz
    ITLA.SetFrequency(195.50)
    #Set power in dBm
    ITLA.SetPower(10.0)
    ITLA.SetSweepRange(120)
    ITLA.SetSweepRate(10)    
    ITLA.EnableLaser(True)
    ITLA.EnableWhisperMode(True)
    #DO SWEEP
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    #DO JUMP
    ITLA.SetNextFrequency(195.55)
    ITLA.SetNextSled(30.35)
    ITLA.SetNextCurrent(87.9)
    ITLA.FineTuneFrequency(0)
    ITLA.ExecuteJump()
    ITLA.WaitForLaser()
    time.sleep(3) #Recommended by Heino in case laser overshoots
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    t = time.time()
    while time.time()-t < 30:
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    
    #turn everything off
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
    ITLA.sercon.close()