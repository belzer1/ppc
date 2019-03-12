import ITLA_Wrap
import time
import numpy as np
import csv
import logging

if __name__ == "__main__":       
    logging.basicConfig(level=logging.INFO, filename="logfile_"+time.strftime('%d%b%Y'), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

    
    # ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyUSB20",9600,'direct')
    ITLA = ITLA_Wrap.ITLA_Class("/dev/ttyACM45",115200,'MCU')
    
    frequency = []
    sled = []
    filter1 = []
    filter2 = []
    adjust1 = []
    adjust2 = []
    current = []
    with open('1dBm.csv','r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            frequency.append(float(row[1]))
            sled.append(float(row[2]))
            filter1.append(float(row[3]))
            filter2.append(float(row[4]))
            current.append(int(row[5]))
            adjust1.append(int(row[6]))
            adjust2.append(int(row[7])) 
    
    ITLA.EnableLaser(False)
    time.sleep(20)
    
    # ITLA.ProbeLaser()
    
    ITLA.SetScanSled(32000)

    ITLA.LockSled()

    ITLA.SetCurrentAdjust(adjust1[0],adjust2[0])

    ITLA.SetFrequency(191.50)

    ITLA.SetScanAmplitude(100)

    ITLA.SetPower(1000)

    ITLA.SetChannel1()

    # ITLA.ScanStatus()

    ITLA.EnableLaser(True)

    time.sleep(5)

    ITLA.EnableCleanMode(True)

    time.sleep(5)

    ITLA.EnableScan(True)

    ITLA.Send_command(255,255,255,255) 

    for idx, freq in enumerate(frequency):
        print('Setting next data point, centred on {} THz'.format(freq))
        ITLA.SetScanSled(sled[idx])
        ITLA.SetFilter1(filter1[idx])
        ITLA.SetFilter2(filter2[idx])
        ITLA.SetCurrentAdjust(adjust1[idx],adjust2[idx])
        ITLA.SetCurrent(current[idx])
        while ITLA.IsSweeping():
            ITLA.ScanStatus()
            ITLA.Send_command(1,253,253,253) 
            # print(ITLA.ReadOffsetFreq())
            # print(ITLA.SendReceive(0,0xE5,0x00,0x01))
            time.sleep(0.5)

    ITLA.Send_command(254,254,254,254) 
    ITLA.EnableScan(False)

    ITLA.EnableCleanMode(False)

    ITLA.EnableLaser(False)

