import ITLA_Wrap
import time

if __name__ == "__main__":                            
    
    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
     
    #Probe laser and check it's happy
    ITLA.ProbeLaser()
    
    ITLA.SetScanSled(32000?)

    ITLA.LockSled()

    ITLA.SetCurrentAdjust(100?)

    ITLA.SetFrequency(190.90)

    ITLA.SetPower(1300)

    ITLA.SetChannel1()

    ITLA.EnableLaser(True)

    ITLA.EnableCleanMode(True)

    time.sleep(0.5)

    ITLA.EnableScan(True)

    sledlist = [29.973, 29.973]
    filter1list = [62.123, 62.123]
    filter2list = [81.875, 81.875]
    currentadjustlist = [10, 10, ]
    currentlist = [134.3, 134.3]


    for ii in len(filter1list):
        ITLA.SetScanSled(sledlist[ii])

        ITLA.SetFilter1(filter1list[ii])

        ITLA.SetFilter2(filter2list[ii])

        ITLA.SetCurrentAdjust(currentadjustlist[ii])

        ITAL.SetCurrent(currentlist[ii])

    ITLA.EnableScan(False)

    ITLA.EnableCleanMode(False)

    ITLA.EnableLaser(False)

