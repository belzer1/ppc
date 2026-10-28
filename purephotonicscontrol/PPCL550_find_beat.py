#Pure Photonics Control for PPCL550 tunable interface to implement laser wavelength sweep like what is possible w/ Toptica CTL 
import lasercommands
import logger
import pypicosdk as ps 
import numpy as np 
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.fft import rfft, rfftfreq
from scipy.signal import windows
import ctypes
from datetime import date
from scipy.signal import find_peaks
import time 
import datetime
#### WORKFLOW:
#1. set up connection to laser [done]
#1a. set initial laser parameters (wavelength, power, etc) [done]
#2. set up parameters for wavelength sweep of laser [done]
#3. log data from laser about wavelength and power 
#start with defined wavelength 
#if not found at that wavelength, do a sweep between 2 setpoints as determined by user 
# need to figure out at what wavelength you get a peak in the fft that is greater than some threshold
#set the laser to that wavelength
#do a smaller sweep around that wavelength to find the peak more precisely
#set to the wavelength from the small sweep where you get maximum amplitude in the fft 

baud=9600 #specified by Pure Photonics for PPCL550 serial connections 
timeout=10 #s
samples=50_000
WRITE=1
READ=0
REG_CleanJumpCal=0xD2
REG_ID=0X03
REG_LoadSetpoint=0xD0
REG_FCF1=0x35
REG_FCF2=0x36

def find_port(desc_='str'):
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print(f"Port: {port} -> Description: {desc} HWID:{hwid}")
        if desc_ in desc:
            port_=port
        if 'PID=0403:6015' in hwid:
            port_=port
        else:
            print('Hardware not found.')
    return port_
def open_scope(SAMPLE_RATE_MHz):
    scope = ps.ps5000a()
    scope.open_unit()
    scope.set_channel(channel=ps.CHANNEL.A, range=ps.RANGE.V10, coupling=ps.COUPLING.DC, offset=0, bandwidth=ps.BANDWIDTH_CH.BW_FULL)
    scope.set_simple_trigger(channel=ps.CHANNEL.A, threshold=0, auto_trigger=0)
    TIMEBASE = scope.sample_rate_to_timebase(sample_rate=SAMPLE_RATE_MHz, unit=ps.SAMPLE_RATE.MSPS)
    return scope, TIMEBASE


#need to fix 
class liveplot:
    def __init__(self, scope, TIMEBASE, SAMPLES, SAMPLE_RATE_MHz):
        self.scope=scope
        self.TIMEBASE=TIMEBASE
        self.SAMPLES=SAMPLES
        self.SAMPLE_RATE_MHz=SAMPLE_RATE_MHz
        self.fig, self.ax = plt.subplots(2,1,figsize=(10, 8))
        self.ax[0].grid(True)
        self.ax[1].grid(True)
        self.line, = self.ax[0].plot([], [], lw=0.5)
        self.line_2,=self.ax[1].plot([], [], lw=0.5)
        self.count=0
    def update_plot(self, frame):
        global windows 
        self.count+=1
        channel_buffer,time_axis=self.scope.run_simple_block_capture(self.TIMEBASE,self.SAMPLES)
        freqs=rfftfreq(self.SAMPLES,1/(self.SAMPLE_RATE_MHz*1e6))
        V_windowed=channel_buffer[ps.CHANNEL.A]*windows.hann(self.SAMPLES)
        amplitudes = np.abs(rfft(V_windowed))
        amplitudes_db = np.abs(20*np.log10(amplitudes/1e3))
        trace = channel_buffer[ps.CHANNEL.A]
        self.line.set_data(time_axis, trace)
        self.line_2.set_data(freqs[:self.SAMPLES//2], amplitudes_db[:self.SAMPLES//2])
        self.ax[0].set_xlim(time_axis.min(), time_axis.max())
        self.ax[0].set_ylim(np.min(trace), np.max(trace))
        self.ax[0].set_xlabel("Time (ns)")
        self.ax[0].set_ylabel("Amplitude (mV)")
        self.ax[1].set_xlim(freqs.min(), freqs.max())
        self.ax[1].set_ylim(np.min(amplitudes_db), np.max(amplitudes_db))
        self.ax[1].set_xlabel("Frequency (Hz)")
        self.ax[1].set_ylabel("Amplitude (dB)")
        return self.line,self.line_2,
    def animate(self):
        self.ani=FuncAnimation(
            self.fig,
            self.update_plot,
            interval=200,
            blit=True,
            cache_frame_data=False,
        )
        return self.line,self.line_2
    def show(self):
        plt.show()
    def terminate(self):
        self.scope.close_unit()
        print("Picoscope connection closed.")
def to_bytes(value):
    byte2=(value&0xff00)>>8
    byte3=value&0xff
    return byte2,byte3
#setpoints: 
#95 channels at 50 GHZ spacing each between 191.5 and 196.25 THz
#Ch1 = 191.5 THz
#Ch2 = 191.55 THz
#.....
#load desired setpoint
#execute the jump 
def freq_grid(start,stop,channels):
    """
    For PPCL freq spacing must be multiple of 0.050 [50 GHz]
    freq must be given in THz 191.5<=f<=196.25
    creates a channel grid with the closest number of channels to desired using allowable step size 
    """
    import numpy as np
    range=np.abs(start-stop) #THz
    step=range/channels
    step=round(step/0.05)*0.05
    return np.round(np.arange(start, stop, step), decimals=2)

def beat_check(scope,TIMEBASE,samples:int):
    """
    scope=picoscope object 
    samples=integer number of samples 
    TIMEBASE=picoscope timebase object 
    """
    global rfft, rfftfreq
    #run a simple capture on the scope 
    #take FFT 
    #if FFT has a peak not at DC that is greater than some threshold 
    #keep the capture, plot it, return that plot 
    #store the frequency the laser was at --> return this frequency 
    f_s=scope.get_actual_sample_rate()
    channelBuffer,timeAxis=scope.run_simple_block_capture(TIMEBASE,samples)
    X_f=rfftfreq(n=samples, d=(1/f_s))
    X=np.abs(rfft(channelBuffer[ps.CHANNEL.A],n=samples))
    fft_median=np.median(X)
    t=0
    peak_check=find_peaks(X,height=1.5*fft_median,prominence=[0.1*fft_median, 0.25*fft_median],wlen=5000) #need stricter prominences
    print(peak_check)
    # if len(peak_check)!=0:
    #     peak_loc=X_f[peak_check[0]]
    #     plt.plot(X_f,X)
    #     plt.show()
    #     return peak_loc
    # if len(peak_check)==0:
    #     print(f'Peak not found.')
    #     return peak_check
    # else:
    #     print(
    #     'Error in peak finding function.'
    #     )

# channel_freqs=freq_grid(start=191.5, stop=196.25, channels=100)
# idx=np.where(np.isclose(channel_freqs, 193.4))
def main():
    #set up connection to laser 
    try:
        general=logger.logger(name='general',base_path="")
        lasercomms=logger.logger(name='lasercomms', base_path="")
        port=find_port('FT230X') #purephotonics uses FTDI interface 
        ITLA=lasercommands.laser(port=port,baudrate=9600,log_general=general.log,log_lasercomms=lasercomms.log,com_type='direct')
        laser_model=ITLA.SendReceive(READ,REG_ID,0,0)
        ITLA.ProbeLaser()
        # ITLA.SetWavelength(1550.0) #set to nominal wavelength
        ITLA.SetFrequency(193.486)
        ITLA.SetPower(13.0) #set to nominal power
        ITLA.EnableLaser(True) #turn on laser
        ITLA.EnableWhisperMode(True) #turn on whisper mode to reduce noise in the laser output
        #set up connetion to picoscope to get FFT of laser output
        SAMPLES = 50_000
        SAMPLE_RATE_MHz = 250
        scope,TIMEBASE=open_scope(SAMPLE_RATE_MHz=SAMPLE_RATE_MHz)
        #fix live plot stuff later 
        # plot=liveplot(scope,TIMEBASE,SAMPLES,SAMPLE_RATE_MHz)
        # plot.animate()
        # plot.show()
        #start wavelength sweep -----------------------------------
        #get channels and associated indices
        start_freq=191.5
        stop_freq=196.25
        channels = freq_grid(start=start_freq, stop=stop_freq, channels=100)
        indices = [np.where(np.isclose(channels, ch))[0][0] for ch in channels]
        channel_dict = dict(zip(channels, indices))
        #initial channel and sweep channels 
        sweep_start_freq=193.4
        sweep_stop_freq=193.5
        channels_sweep={key:val for key,val in channel_dict.items() if sweep_start_freq<=key<=sweep_stop_freq}
        print(channels_sweep)
        #load initial channel 
        # ITLA.SendReceive(WRITE,REG_LoadSetpoint, *to_bytes(channels_sweep[sweep_start_freq])) #works
        ITLA.SetFrequency(193.486)
        #read frequency from laser 
        thz=ITLA.SendReceive(READ,REG_FCF1,0,0)
        ghz=ITLA.SendReceive(READ,REG_FCF2,0,0)
        print(thz,ghz) #confirm initial channel is set correctly
        beat_check(scope=scope,TIMEBASE=TIMEBASE,samples=samples)
        #check if there is a beat between the signal and LO lasers by looking at output from scope 
        # time.sleep(120)
        # ITLA.EnableLaser(False)
    except Exception as err:
        if 'ITLA' in locals():
            ITLA.Shutdown()
        if 'scope' in locals():
            scope.close_unit()
        raise err
    except KeyboardInterrupt:
        print('User interrupted, shutting down laser.')
        if 'ITLA' in locals():
            ITLA.Shutdown()
        if 'scope' in locals():
            scope.close_unit()
if __name__=="__main__":
    main()
 