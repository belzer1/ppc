#CALIBRATE A PURE PHOTONICS LASER FOR CLEAN SCAN / CLEAN JUMP 
from purephotonicscontrol import lasercommands as lc
COM='COM3'
baud=9600
WRITE=1
READ=0
REG_CleanJumpCal=0xD2
REG_FCF1=0x35
REG_FCF2=0x36
def calibrate_channels(laser,start_freq,stop_freq,channels):
    def freq_decomp(freq): 
        import math
        thz,ghz=math.modf(freq)
        fcf1,fcf2=thz,ghz*1000
        return fcf1,fcf2
    def freq_grid(start,stop):
        """
        For PPCL freq spacing must be multiple of 0.050 [50 GHz]
        freq must be given in THz 191.5<=f<=196.25
        creates a channel grid with the closest number of channels to desired using allowable step size 
        """
        import numpy as np
        import math
        range=np.abs(start-stop) #THz
        step=range/channels
        step=round(step/0.05)*0.05
        return np.arange(start, stop, step) 
    laser=lc.laser(port=COM,baudrate=baud,com_type="direct")
    laser.ProbeLaser()
    laser.EnableLaser(False) #do not turn laser on during calibration
    laser.EnableWhisperMode()
    num_channels=len(freq_grid(start_freq,stop_freq))
    thz_fcf1,ghz_fcf1=freq_decomp(start_freq)
    #workflow: 
    #1. set number of channels to calibrate to laser 
    #2. set fcf1, fcf2
    #3. set power
    #4. #need to query: frequency, current, sled, filter1, filter2, current, adjust1, adjust2
    #write that query to computer memory and store it 
    #set laser power 
    laser.SetPower(17.0) #in dBm 
    #set first channel frequency 
    laser.SendReceive(WRITE,REG_FCF1,)
    laser.SendReceive(WRITE,REG_CleanJumpCal,num_channels) #set number of channels to calibrate