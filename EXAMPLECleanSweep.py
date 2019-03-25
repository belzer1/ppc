import ITLA_Wrap
import time

if __name__ == "__main__":                            
    logging.basicConfig(level=logging.INFO, filename="logfile_"+time.strftime('%d%b%Y'), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
    
    # ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM15",115200,'MCU')
     
    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    #Turn laser off before setting frequency is easiest
    ITLA.EnableLaser(False)
    #Set frequency in THz
    ITLA.SetFrequency(195.50)
    #Set power in dBm
    ITLA.SetPower(10.0)
    #Set sweep range in GHz
    ITLA.SetSweepRange(120)
    #Set sweep rare in MHZ/s
    ITLA.SetSweepRate(20000)    
    
    ITLA.EnableLaser(True)
    
    ITLA.EnableWhisperMode(True)

    time.sleep(1)

    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)

    time.sleep(100)
    #DO SCIENCE

    #turn everything off
    ITLA.EnableSweep(False)
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)








