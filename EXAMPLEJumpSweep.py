import ITLA_Wrap
import time
import logging

def sweep_with_monitor():
    ITLA.EnableSweep(True)
    ITLA.EnableTeensyMonitor(True)
    previous_offset = 0
    previous_slope = 0
    sweep_counter = -1   #start counter at -1 so I don't count the starting of the sweep as it turning around
    while sweep_counter<1:
            if ITLA.sercon.inWaiting() > 0:
                scan_status, current_offset = ITLA.TeensyReadStatus()
                
                if current_offset - previous_offset > 0: #if frequency is increasing
                    if previous_slope <= 0: #if previously was non-increasing
                        sweep_counter +=1
                previous_slope = current_offset - previous_offset
                print(scan_status)
            time.sleep(0.00001)
    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableSweep(False)
    time.sleep(1)
    # clear anything send my the teensy that snuck through because of timing mismatch
    while ITLA.sercon.inWaiting():
        ITLA.sercon.read(1)

class CleanScanParameters:
    def __init__(self,power):
        self.frequency_full = []
        self.sled_full = []
        self.filter1_full = []
        self.filter2_full = []
        self.adjust1_full = []
        self.adjust2_full = []
        self.current_full = []

        with open('clean_scan_parameters/' + power + '.csv','r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                self.frequency_full.append(float(row[1]))
                self.sled_full.append(float(row[2]))
                self.filter1_full.append(float(row[3]))
                self.filter2_full.append(float(row[4]))
                self.current_full.append(int(row[5]))
                self.adjust1_full.append(int(row[6]))
                self.adjust2_full.append(int(row[7])) 

    def set_frequency_range(self,freq_start,freq_stop):
        start = self.frequency_full.index(freq_start)
        stop = self.frequency_full.index(freq_stop)+1

        self.frequency = self.frequency_full[start:stop]
        self.sled = self.sled_full[start:stop]
        self.filter1 = self.filter1_full[start:stop]
        self.filter2 = self.filter2_full[start:stop]
        self.adjust1 = self.adjust1_full[start:stop]
        self.adjust2 = self.adjust2_full[start:stop]
        self.current = self.current_full[start:stop]


if __name__ == "__main__":  
    logging.basicConfig(level=logging.INFO, filename="logfile_"+time.strftime('%d%b%Y'), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")                          
    
    ITLA = ITLA_Wrap.ITLA_Class("COM4",9600,'MCU')
#     ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB0",9600)
#    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM0",115200,'MCU')
    
    CleanScan = CleanScanParameters('10.0dBm')
    CleanScan.set_frequency_range(195,196)

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
    
    for idx, _ in enumerate(CleanScan.frequency):
        print('Jumping to {} THz'.format(freq))
        ITLA.SetNextFrequency(CleanScan.frequency[idx])
        ITLA.SetNextSled(CleanScan.sled[idx])
        ITLA.SetNextCurrent(CleanScan.current[idx])
        ITLA.FineTuneFrequency(0)
        ITLA.ExecuteJump()
        ITLA.WaitForLaser()
        time.sleep(3) #Recommended by Heino in case laser overshoots
       
        #Adding some triggering of scopes here would be a good idea
        
        sweep_with_monitor()

    
    #turn everything off
    ITLA.EnableWhisperMode(False)
    ITLA.EnableLaser(False)
    ITLA.sercon.close()