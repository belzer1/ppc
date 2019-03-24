import ITLA_Wrap
import time
import numpy as np
import csv
import logging

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
    logging.basicConfig(level=logging.INFO, filename="logfile_"+time.strftime('%d%b%Y'), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

    # ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB20",9600,'direct')
    # ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM4",115200,'MCU')
    
    CleanScan = CleanScanParameters('10.0dBm')
    CleanScan.set_frequency_range(195,196)
    
    ITLA.EnableLaser(False)
    time.sleep(20)
    
    # ITLA.ProbeLaser()
    
    ITLA.SetScanSled(32000)

    ITLA.LockSled()

    ITLA.SetCurrentAdjust(adjust1[0],adjust2[0])

    ITLA.SetFrequency(191.50)

    ITLA.SetScanAmplitude(120)

    ITLA.SetPower(1000)

    ITLA.SetChannel1()

    ITLA.EnableLaser(True)

    time.sleep(1)

    ITLA.EnableCleanMode(True)

    time.sleep(1)

    ITLA.EnableScan(True)
    scan_status = 1 #odd value means the laser is scanning 

    for idx, freq in enumerate(CleanScan.frequency):
        ITLA.EnableTeensyMonitor(False)
        print('Loading next data point, centred on {} THz'.format(freq))
        ITLA.SetScanSled(CleanScan.sled[idx])
        ITLA.SetFilter1(CleanScan.filter1[idx])
        ITLA.SetFilter2(CleanScan.filter2[idx])
        ITLA.SetCurrentAdjust(CleanScan.adjust1[idx],CleanScan.adjust2[idx])
        ITLA.SetCurrent(CleanScan.current[idx])
        scan_status = 1
        ITLA.EnableTeensyMonitor(True)
        while scan_status%2:            
            if ITLA.sercon.inWaiting() > 0:
                scan_status = ITLA.TeensyReadStatus()
            time.sleep(0.0001)

    ITLA.EnableTeensyMonitor(False)
    ITLA.EnableScan(False)
    ITLA.EnableCleanMode(False)
    ITLA.EnableLaser(False)