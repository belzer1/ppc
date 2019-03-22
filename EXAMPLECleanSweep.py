import ITLA_Wrap
import time

if __name__ == "__main__":                            
    
    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
     
    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    #Turn laser off before setting frequency is easiest
    ITLA.EnableLaser(False)
    #Set frequency in THz
    ITLA.SetFrequency(195.50)
    #Set sweep range in GHz
    ITLA.SetSweepRange(140)
    #Set sweep rare in MHZ/s
    ITLA.SetSweepRate(6500)
    #Set power in dBm
    ITLA.SetPower(10.0)
    
    ITLA.EnableLaser(True)
    
    ITLA.EnableWhisperMode(True)

    time.sleep(1)

    ITLA.EnableSweep(True)

    time.sleep(100)
    #DO SCIENCE


    #turn everything off
    ITLA.EnableSweep(False)
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)








