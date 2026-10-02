#CALIBRATE A PURE PHOTONICS LASER FOR CLEAN SCAN / CLEAN JUMP 
import lasercommands as lc
import logger
import ctypes
import numpy as np
WRITE=1
READ=0
REG_CleanJumpCal=0xD2
REG_ID=0X03
REG_FCF1=0x35
REG_FCF2=0x36
def calibrate_channels(laser,general_log,lasercomms_log,start_freq,stop_freq,power,channels):
    def freq_decomp(freq): 
        import math
        thz,ghz=math.modf(freq)
        fcf1,fcf2=thz,ghz*1000
        return int(fcf1),int(fcf2)
    def freq_grid(start,stop):
        """
        For PPCL freq spacing must be multiple of 0.050 [50 GHz]
        freq must be given in THz 191.5<=f<=196.25
        creates a channel grid with the closest number of channels to desired using allowable step size 
        """
        import numpy as np
        range=np.abs(start-stop) #THz
        step=range/channels
        step=round(step/0.05)*0.05
        return np.arange(start, stop, step) 
    channel_freqs=freq_grid(start_freq,stop_freq)
    num_channels=len(channel_freqs)
    print(num_channels)
    thz_fcf,ghz_fcf=freq_decomp(start_freq)
    #put into bytes 
    thz_byte2=(thz_fcf&0xff00)>>8
    thz_byte3=thz_fcf&0xff
    ghz_byte2=(ghz_fcf&0xff00)>>8
    ghz_byte3=ghz_fcf&0xff
    try:
        laser.ProbeLaser()
        laser.EnableLaser(False) #do not turn laser on during calibration
        laser.EnableWhisperMode(True)
        #set laser power 
        laser.SetPower(power) #in dBm 
        #set first channel frequency 
        laser.SendReceive(WRITE,REG_FCF1,thz_byte2,thz_byte3)
        laser.SendReceive(WRITE,REG_FCF2,ghz_byte2,ghz_byte3)
        #check what frequency iss
        thz_check=laser.SendReceive(READ,REG_FCF1,0,0)
        ghz_check=laser.SendReceive(READ,REG_FCF2,0,0)
        if not (thz_fcf==thz_check) or not (ghz_fcf==ghz_check):
            print("Failed to set FCF correctly, laser must be turned off. Calibration attempt discontinued.")
            laser.EnableLaser(False)
            return None
        # send command to calibrate channels 
        num_channels=ctypes.c_ushort(num_channels).value #has to be unsigned integer
        num_channels_byte3=num_channels&0xff
        num_channels_byte2=(num_channels&0xff00)>>8
        laser.SendReceive(WRITE,REG_CleanJumpCal,num_channels_byte2,num_channels_byte3)
        calibrating=laser.SendReceive(READ,REG_CleanJumpCal,0,0) #read calibration--last bit = 1 if ongoing, 0 once complete 
        while calibrating==1:
            calibrating=laser.SendReceive(READ,REG_CleanJumpCal,0,0)
        print("Laser calibration complete.")
        # log setpoints and calibration data
        general_log.info(f"Laser calibration complete. Setpoint frequencies: {channel_freqs}, Setpoint power: {power} dBm, Number of channels: {num_channels}")
        setpoints=ITLA.SendReceive(READ,REG_CleanJumpCal,num_channels_byte2,num_channels_byte3)
    except Exception as err:
        general_log.error(err)
        #close laser connection
        if 'ITLA' in locals():
            ITLA.Shutdown()
    except KeyboardInterrupt:
        print("Calibration interrupted by user. Turning off laser.")
        if 'ITLA' in locals():
            ITLA.Shutdown()
    finally:
        if 'ITLA' in locals():
            ITLA.sercon.close()
        if 'general_log' in locals():
            general_log.info("Laser connection closed.")
            general_log.close()
        if 'lasercomms_log' in locals():
            lasercomms_log.info("Laser connection closed.")
            lasercomms_log.close()
    return channel_freqs,setpoints,num_channels

def find_port(desc_='str'):
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print(f"Port: {port} -> Description: {desc}")
        if desc_ in desc:
            port_=port
    return port_
if __name__=="__main__":
    try:
        general=logger.logger(name='general',base_path='/Users/helenabelzer/Library/CloudStorage/OneDrive-USCISI/AQUARIUS/DataLogs/purephotonicstests')
        lasercomms=logger.logger(name='lasercomms', base_path='/Users/helenabelzer/Library/CloudStorage/OneDrive-USCISI/AQUARIUS/DataLogs/purephotonicstests')
        port=find_port('FT230X') #purephotonics uses FTDI interface 
        # port='/dev/cu.usbserial-DK0H8ILT'
        ITLA=lc.laser(port=port,baudrate=9600,log_general=general.log,log_lasercomms=lasercomms.log,com_type='direct')
        laser_model=ITLA.SendReceive(READ,REG_ID,0,0)
        channel_freqs,setpoints,num_channels=calibrate_channels(laser=ITLA,start_freq=191.5,stop_freq=196.25,power=17.0,channels=100)
        with open(f'calibration_info_{laser_model}.npy', 'wb') as f:
            np.save(f, channel_freqs, allow_pickle=True)
            np.save(f, num_channels, allow_pickle=True)
            np.save(f, setpoints, allow_pickle=True)
    except Exception as err:
        # general.log.error(err)
        print(err)
        if 'ITLA' in locals():
            ITLA.Shutdown()
    

