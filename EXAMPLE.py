import ITLA_Wrap
import time

if __name__ == "__main__":                            
    
    ITLA = ITLA_Wrap.ITLA_Class("COM6",9600)
     
    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    
    #Laser is happier if we set all the parameters when it's off
    ITLA.EnableLaser(False)
    
    ITLA.SetFrequency(195.50)
    
    ITLA.SetSweepRange(140)
    
    ITLA.SetSweepRate(6500)
    
    ITLA.SetPower(1000)
    
    ITLA.EnableLaser(True)

    ITLA.EnableWhisperMode(True)

    time.sleep(1)

    ITLA.EnableSweep(True)

    time.sleep(100)


    #turn everything off
    ITLA.EnableSweep(False)
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
