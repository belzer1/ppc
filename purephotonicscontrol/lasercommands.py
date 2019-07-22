"""Wrap made by Matt Berrington, based off the CLI python file that Pure Photonics provides. Last updated 19th Feb 2018

To use this wrapper simply import it in your script that will execute the laser control. """

import serial
import time
import struct
import os
import os.path
import time
import sys
import threading
import math
import logging
import csv
import ctypes

ITLA_NOERROR=0x00
ITLA_EXERROR=0x01
ITLA_AEERROR=0x02
ITLA_CPERROR=0x03
ITLA_NRERROR=0x04
ITLA_CSERROR=0x05
ITLA_ERROR_SERPORT=0x01
ITLA_ERROR_SERBAUD=0x02

REG_Nop=0x00
REG_Mfgr=0x02
REG_Model=0x03
REG_Serial=0x04
REG_Release=0x06
REG_Gencfg=0x08
REG_AeaEar=0x0B
REG_Iocap=0x0D
REG_Ear=0x10
REG_Dlconfig=0x14
REG_Dlstatus=0x15
REG_Channel=0x30
REG_Power=0x31
REG_Resena=0x32
REG_Grid=0x34
REG_Fcf1=0x35
REG_Fcf2=0x36
REG_Freq1=0x40
REG_Freq2=0x41
REG_Oop=0x42
REG_Opsl=0x50
REG_Opsh=0x51
REG_Lfl1=0x52
REG_Lfl2=0x53
REG_Lfh1=0x54
REG_Lfh2=0x55
REG_Lgrid=0x56
REG_Currents=0x57
REG_Temps=0x58
REG_Ftf=0x62
REG_Mode=0x90
REG_PW=0xE0
REG_Csweepsena=0xE5
REG_Csweepamp=0xE4
REG_Cscanamp=0xE4
REG_Cscanon=0xE5
REG_Csweepon=0xE5
REG_Csweepoffset=0xE6
REG_Cscanoffset=0xE6
REG_Cscancurrentadjust=0xE7
REG_Cscansled=0xF0
REG_Cscanf1=0xF1
REG_Cscanf2=0xF2
REG_Cscancurrent=0xF3
#This registry is write only
REG_CjumpTHz=0xEA
#This registry is write only
REG_CjumpGHz=0xEB
#This registry is write only
REG_CjumpSled=0xEC
#This registry is write only
REG_CjumpCurrent=0xE9
#This registry is write only
REG_Cjumpon=0xED
REG_Cjumpoffset=0xE6

READ=0
WRITE=1
latestregister=0
tempport=0
raybin=0
queue=[]
maxrowticket=0

_error=ITLA_NOERROR
seriallock=0

class laser:
    def __init__(self,port,baudrate, general_logger,lasercomms_logger, com_type = 'MCU'):
        
        self.SetLoggers(general_logger,lasercomms_logger)
            
        if com_type == 'direct':
            self.sercon = self.ITLAConnect(port,baudrate)
            self.teensy_connected = False
        elif com_type == 'MCU':
            self.sercon = serial.Serial(port, baudrate)
            self.sercon.reset_input_buffer()
            self.sercon.reset_output_buffer()
            self.teensy_connected = True
        else:
            print("com_type must be 'direct' or 'MCU'")

        self.min_frequency = self.SendReceive(READ,REG_Lfl1,0,0) + self.SendReceive(READ,REG_Lfl2,0,0)*0.0001
        print('This lasers minimum frequency is {} THz'.format(self.min_frequency))
        self.max_frequency = self.SendReceive(READ,REG_Lfh1,0,0) + self.SendReceive(READ,REG_Lfh2,0,0)*0.0001
        print('This lasers maximum frequency is {} THz'.format(self.max_frequency))
        self.min_power = self.SendReceive(READ,REG_Opsl,0,0)*0.01
        print('This lasers minimum power is {} dBm'.format(self.min_power))
        self.max_power = self.SendReceive(READ,REG_Opsh,0,0)*0.01
        print('This lasers maximum power is {} dBm'.format(self.max_power))
        self.min_grid = self.SendReceive(READ,REG_Lgrid,0,0)*0.1
        print('This lasers minumum grid spacing is {} GHz'.format(self.min_grid))

    def stripString(self,inp):
        outp=''
        inp=str(inp)
        teller=0
        while teller<len(inp) and ord(inp[teller])>47:
            outp=outp+inp[teller]
            teller=teller+1
        return(outp)

    def ITLALastError(self):
        return(_error)

    def SerialLock(self):
        global seriallock
        return seriallock

    def SerialLockSet(self):
        global seriallock
        global queue
        seriallock=1
    
    def SerialLockUnSet(self):
        global seriallock
        global queue
        seriallock=0
        queue.pop(0)
    
    def checksum(self,byte0,byte1,byte2,byte3):
        bip8=(byte0&0x0f)^byte1^byte2^byte3
        bip4=((bip8&0xf0)>>4)^(bip8&0x0f)
        return bip4
    
    def Send_command(self,byte0,byte1,byte2,byte3):
        b0 = struct.pack('!B',byte0)
        b1 = struct.pack('!B',byte1) 
        b2 = struct.pack('!B',byte2)
        b3 = struct.pack('!B',byte3)
        # print('Sending')
        # print(b0,b1,b2,b3)

        self.sercon.write(b0)
        self.sercon.write(b1)
        self.sercon.write(b2)
        self.sercon.write(b3)
        self.lasercomms_logger.info("Sent {}, {}, {}, {}".format(byte0, byte1, byte2, byte3))


    def Receive_response(self):
        global _error,queue
        reftime=time.clock()
        while self.sercon.inWaiting()<4:
            if time.clock()>reftime+0.25:
                _error=ITLA_NRERROR
                return(0xFF,0xFF,0xFF,0xFF)
            time.sleep(0.0001)
        try:
            byte0=ord(self.sercon.read(1))
            byte1=ord(self.sercon.read(1))
            byte2=ord(self.sercon.read(1))
            byte3=ord(self.sercon.read(1))
        except:
            print('problem with serial communication. queue[0] =',queue)
            byte0=0xFF
            byte1=0xFF
            byte2=0xFF
            byte3=0xFF
        if self.checksum(byte0,byte1,byte2,byte3)==byte0>>4:
            _error=byte0&0x03
            # print('Receiving:')
            # print(byte0,byte1,byte2,byte3)
            self.lasercomms_logger.info("Receive {}, {}, {}, {}".format(byte0, byte1, byte2, byte3))
            return(byte0,byte1,byte2,byte3)
        else:
            _error=ITLA_CSERROR
            return(byte0,byte1,byte2,byte3)

    def Receive_simple_response(self):
        global _error,CoBrite
        reftime=time.clock()
        while self.sercon.inWaiting()<4:
            if time.clock()>reftime+0.25:
                _error=ITLA_NRERROR
                return(0xFF,0xFF,0xFF,0xFF)
            time.sleep(0.0001)
        byte0=ord(self.sercon.read(1))
        byte1=ord(self.sercon.read(1))
        byte2=ord(self.sercon.read(1))
        byte3=ord(self.sercon.read(1))

    def ITLAConnect(self,port,baudrate=9600):
        global CoBrite
        reftime=time.clock()
        connected=False
        try:
            self.sercon = serial.Serial(port,baudrate , timeout=1)
        except serial.SerialException:
            return(ITLA_ERROR_SERPORT)
        baudrate2=4800
        while baudrate2<115200:
            self.ITLA(REG_Nop,0,0)
            if self.ITLALastError()!=ITLA_NOERROR:
                #go to next baudrate
                if baudrate2==4800:baudrate2=9600
                elif baudrate2==9600: baudrate2=19200
                elif baudrate2==19200: baudrate2=38400
                elif baudrate2==38400:baudrate2=57600
                elif baudrate2==57600:baudrate2=115200
                self.sercon.close()
                
                self.sercon = serial.Serial(port,baudrate2 , timeout=1)
            else:
                return(self.sercon)
        self.sercon.close()
        print('Dammit, couldnt find laser')
        self.sercon = serial.Serial(port,baudrate2 , timeout=1)
        print(ITLA_ERROR_SERBAUD)
        return(ITLA_ERROR_SERBAUD)

    def ITLA(self,register,data,rw):
        global latestregister
        lock=threading.Lock()
        lock.acquire()
        global queue
        global maxrowticket
        rowticket=maxrowticket+1
        maxrowticket=maxrowticket+1
        queue.append(rowticket)
        lock.release()
        while queue[0]!=rowticket:
            rowticket=rowticket
        if rw==0:
            byte2=int(data/256)
            byte3=int(data-byte2*256)
            latestregister=register
            self.Send_command(int(self.checksum(0,register,byte2,byte3))*16,register,byte2,byte3)
            test=self.Receive_response()
            b0=test[0]
            b1=test[1]
            b2=test[2]
            b3=test[3]
            if (b0&0x03)==0x02:
                test=AEA(b2*256+b3)
                lock.acquire()
                queue.pop(0)
                lock.release()
                return test
            lock.acquire()
            queue.pop(0)
            lock.release()
            return b2*256+b3
        else:
            byte2=int(data/256)
            byte3=int(data-byte2*256)
            self.Send_command(int(self.checksum(1,register,byte2,byte3))*16+1,register,byte2,byte3)
            test=self.Receive_response()
            lock.acquire()
            queue.pop(0)
            lock.release()
            return(test[2]*256+test[3])

    def ITLA_send_only(self,register,data,rw):
        global latestregister
        global queue
        global maxrowticket
        rowticket=maxrowticket+1
        maxrowticket=maxrowticket+1
        queue.append(rowticket)
        while queue[0]!=rowticket:
            time.sleep(.1)
        SerialLockSet()
        if rw==0:
            latestregister=register
            self.Send_command(int(self.checksum(0,register,0,0))*16,register,0,0)
            Receive_simple_response()
            SerialLockUnSet()
        else:
            byte2=int(data/256)
            byte3=int(data-byte2*256)
            self.Send_command(int(self.checksum(1,register,byte2,byte3))*16+1,register,byte2,byte3)
            Receive_simple_response()
            SerialLockUnSet()
         
    def AEA(self,bytes):
        outp=''
        while bytes>0:
            self.Send_command(int(self.checksum(0,REG_AeaEar,0,0))*16,REG_AeaEar,0,0)
            test=self.Receive_response()
            outp=outp+chr(test[2])
            outp=outp+chr(test[3])
            bytes=bytes-2
        return outp

    def ITLAFWUpgradeStart(self,raydata,salvage=0):
        global tempport,raybin
        #set the baudrate to maximum and reconfigure the serial connection
        if salvage==0:
            ref=stripString(ITLA(REG_Serial,0,0))
            if len(ref)<5:
                print('problems with communication before start FW upgrade')
                return(self.sercon,'problems with communication before start FW upgrade')
            ITLA(REG_Resena,0,1)
        ITLA(REG_Iocap,64,1) #bits 4-7 are 0x04 for 115200 baudrate
        #validate communication with the laser
        tempport=self.sercon.portstr
        self.sercon.close()
        self.sercon = serial.Serial(tempport, 115200, timeout=1)
        if stripString(ITLA(REG_Serial,0,0))!=ref:
            return(self.sercon,'After change baudrate: serial discrepancy found. Aborting. '+str(stripString(ITLA(REG_Serial,0,0)))+' '+str( params.serial))
        #load the ray file
        raybin=raydata
        if (len(raybin)&0x01):raybin.append('\x00')
        ITLA(REG_Dlconfig,2,1)  #first do abort to make sure everything is ok
        #print ITLALastError()
        if ITLALastError()!=ITLA_NOERROR:
            return( self.sercon,'After dlconfig abort: error found. Aborting. ' + str(ITLALastError()))
        #initiate the transfer; INIT_WRITE=0x0001; TYPE=0x1000; RUNV=0x0000
        #temp=ITLA(self.sercon,REG_Dlconfig,0x0001 ^ 0x1000 ^ 0x0000,1)
        #check temp for the correct feedback
        ITLA(REG_Dlconfig,3*16*256+1,1) # initwrite=1; type =3 in bits 12:15
        #print ITLALastError()
        if ITLALastError()!=ITLA_NOERROR:
            return(self.sercon,'After dlconfig init_write: error found. Aborting. '+str(ITLALastError() ))
        return(self.sercon,'')

    def ITLAFWUpgradeWrite(self,count):
        global tempport,raybin
        #start writing bits
        teller=0
        while teller<count:
            ITLA_send_only(REG_Ear,struct.unpack('>H',raybin[teller:teller+2])[0],1)
            teller=teller+2
        raybin=raybin[count:]
        #write done. clean up
        return('')

    def ITLAFWUpgradeComplete(self):
        global tempport,raybin
        time.sleep(0.5)
        self.sercon.flushInput()
        self.sercon.flushOutput()
        ITLA(REG_Dlconfig,4,1) # done (bit 2)
        if ITLALastError()!=ITLA_NOERROR:
            return(self.sercon,'After dlconfig done: error found. Aborting. '+str(ITLALastError()))
        #init check
        ITLA(REG_Dlconfig,16,1) #init check bit 4
        if ITLALastError()==ITLA_CPERROR:
            while (ITLA(REG_Nop,0,0)&0xff00)>0:
                time.sleep(0.5)
        elif ITLALastError()!=ITLA_NOERROR:
            return(self.sercon,'After dlconfig done: error found. Aborting. '+str(ITLALastError() ))
        #check for valid=1
        temp=ITLA(REG_Dlstatus,0,0)
        if (temp&0x01==0x00):
            return(self.sercon,'Dlstatus not good. Aborting. ')
        #write concluding dlconfig
        ITLA(REG_Dlconfig,3*256+32, 1) #init run (bit 5) + runv (bit 8:11) =3
        if ITLALastError()!=ITLA_NOERROR:
            return(self.sercon, 'After dlconfig init run and runv: error found. Aborting. '+str(ITLALastError()))
        time.sleep(1)
        #set the baudrate to 9600 and reconfigure the serial connection
        ITLA(REG_Iocap,0,1) #bits 4-7 are 0x0 for 9600 baudrate
        self.sercon.close()
        #validate communication with the self.sercon
        self.sercon = serial.Serial(tempport, 9600, timeout=1)
        ref=stripString(ITLA(REG_Serial,0,0))
        if len(ref)<5:
            return( self.sercon,'After change back to 9600 baudrate: serial discrepancy found. Aborting. '+str(stripString(ITLA(REG_Serial,0,0)))+' '+str( params.serial))
        return(self.sercon,'')

    def ITLASplitDual(self,input,rank):
        
        teller=rank*2
        return(ord(input[teller])*256+ord(input[teller+1]))

    ##############################################################################################################
    #   This is the beginning of functions written by Matt Berrington. Functions prior to this are proivided by PurePhotonics
    #   This section has functions you should only need if you want to manually address known registers for troubleshooting etc
    ##############################################################################################################


    def ProbeLaser(self):
        """Checks the laser responds correctly to a zero input
        It's a decent test to see if the laser is behaving

        Args:
            None

        Returns:
            None
        """

        self.Send_command(0x00,0x00,0x00,0x00)
        response = self.Receive_response()
        if response != (84, 0, 0, 16):
            print('Laser is not behaving! Turning the laser off...')
            self.EnableLaser(False)
            sys.exit()

    def SendReceive(self,readwrite,register,byte2,byte3):
        """This command should be all you need if you want to address a known register

        Args:
            readwrite (int): 0 = read, 1 = write
            register (int): laser register to address
            byte2 (int): first databyte to send
            byte3 (int): second data byte to send

        Returns:
            int: the value returned by the laser
        """
        
        self.Send_command(*self.CommandWithChecksum(readwrite,register,byte2,byte3))
        byte0, byte1, byte2, byte3 = self.Receive_response()
        response = (byte2 << 8) + byte3
        return response

    def CommandWithChecksum(self,byte0,byte1,byte2,byte3):
        """Changes byte zero to include the checksum for communication

        Args:
            byte0 (int): the first byte, normally just 0 or 1 for read or write
            byte1 (int): laser register to address
            byte2 (int): first data byte to send
            byte3 (int): second data byte to send

        Returns:
            int: byte0
            int: byte1
            int: byte2
            int: byte3
        """

        newbyte0 = (self.checksum(byte0,byte1,byte2,byte3)<<4) + byte0
        return newbyte0, byte1, byte2, byte3

    ##############################################################################################################
    #   Basic functions you'll probably always need
    ##############################################################################################################

    def SetWavelength(self,wavelength):
        """Set the laser wavelength in nm
        The wavelength will the rounded to the nearest 0.1 GHz

        Args:
            wavelength (float): The wavelength in nm

        Returns:
            None
        """
        
        freq = round((2.99792*10**8/(wavelength*10**-9))*10**-12,4)
        #Set THz register
        freqTHz = int(freq)
        THzbyte3 = freqTHz&0xff
        THzbyte2 = (freqTHz&0xff00)>>8
        self.SendReceive(WRITE,REG_Fcf1,THzbyte2,THzbyte3)

        #Set GHz register
        freqGHz = int((freq-freqTHz)*10000)
        GHzbyte3 = freqGHz&0xff
        GHzbyte2 = (freqGHz&0xff00)>>8
        self.SendReceive(WRITE,REG_Fcf2,GHzbyte2,GHzbyte3)
        
        #Check what frequency is now set to
        THz = self.SendReceive(READ,REG_Fcf1,0,0)
        GHz = self.SendReceive(READ,REG_Fcf2,0,0)
        if THz == freqTHz and GHz == freqGHz:
            print('Frequency set to ' + str(freqTHz) + '.' + str(freqGHz) + ' THz')
            self.general_logger.info("Laser frequency set to " + str(freqTHz) + "." + str(freqGHz) + " THz")
        else:
            print('Failed to change laser frequency. Laser needs to be turned off')
            self.general_logger.error("Failed to change laser frequency. Laser needs to be turned off")

    def SetFrequency(self,freq):
        """Set the laser frequency in THz
        The frequency will the rounded to the nearest 0.1GHz

        Args:
            freq (float): The frequency in THz

        Returns:
            None
        """
        if not self.min_frequency <= freq <= self.max_frequency:
            print("Requested frequency is outside this lasers range")
            return
        freqTHz = int(freq)
        THzbyte3 = freqTHz&0xff
        THzbyte2 = (freqTHz&0xff00)>>8
        
        self.SendReceive(WRITE,REG_Fcf1,THzbyte2,THzbyte3)
        
        #Set GHz register
        freqGHz = int(round((freq-freqTHz)*10000.0))
        GHzbyte3 = freqGHz&0xff
        GHzbyte2 = (freqGHz&0xff00)>>8
        self.SendReceive(WRITE,REG_Fcf2,GHzbyte2,GHzbyte3)
        
        #Check what frequency is now set to
        THz = self.SendReceive(READ,REG_Fcf1,0,0)
        GHz = self.SendReceive(READ,REG_Fcf2,0,0)
        if THz == freqTHz and GHz == freqGHz:
            print('Frequency set to ' + str(freqTHz) + '.' + str(freqGHz) + ' THz')
            self.general_logger.info("Laser frequency set to " + str(freqTHz) + "." + str(freqGHz) + " THz")
        else:
            print('Failed to change laser frequency. Laser needs to be turned off')
            self.general_logger.error("Failed to change laser frequency. Laser needs to be turned off")

    def SetPower(self,power):
        """Set the laser power in dBm
        The power will be rounded to the nearest 0.01 dBm

        Args:
            power (float): The power in dBm

        Returns:
            None
        """
        if not self.min_power <= power <= self.max_power:
            print("Requested frequency is outside this lasers range")
            return

        power_int = int(power*100)
        byte3 = power_int&0xff
        byte2 = (power_int&0xff00)>>8
        resp = self.SendReceive(WRITE,REG_Power,byte2,byte3)
        self.general_logger.info("Laser power set to " + str(power) + " dBm")
        print("Laser power set to " + str(power) + " dBm")
        

    def EnableLaser(self,state):
        """Turn the laser on/off
        Will automatically wait for laser to lock

        Args:
            state (bool): True -> turn on laser. False -> turn off laser

        Returns:
            None
        """

        if state == True:
            self.general_logger.info("Turning on laser...")
            self.SendReceive(WRITE,REG_Resena,0x00,0x08)
            print('Please wait, laser is turning on...')
            self.WaitForLaser()
            self.general_logger.info("Laser is on")
            print('Laser is on')
        else:
            self.SendReceive(WRITE,REG_Resena,0x00,0x00)
            self.general_logger.info("Laser disabled")
            self.WaitForLaser()
            print('Laser is off')

    def WaitForLaser(self):
        """Wait for the pending flag on the laser to drop
        Useful for waiting until the laser locks

        Args:
            None

        Returns:
            None
        """

        pending = 1
        while pending:
            self.Send_command(0x00,0x00,0x00,0x00)
            resp = self.Receive_response()
            pending = resp[2]
            time.sleep(0.5)

    def EnableWhisperMode(self,state):
        """In the whisper mode, all possible control loops are disabled.
        This significantly reduces the 1-10,000 Hz noise. 
        PurePhotonics recommend switching back to the normal mode occasionally.
        Such a switch-back could be done in less than 10 seconds. 

        There is also "Clean Mode", that is accessed by writing "0x00 0x01".
        PurePhotonics now recommends using "Whisper Mode" for all applications

        Args:
            state (bool): True -> Whispher Mode. False -> Normal/Dither Mode

        Returns:
            None
        """

        if state == True:
            self.SendReceive(WRITE,REG_Mode,0x00,0x02)
            print("Whisper mode enabled")
            self.general_logger.info("Whisper mode enabled")
            time.sleep(0.5)
        else:
            self.SendReceive(WRITE,REG_Mode,0x00,0x00)
            print("Whisper mode disabled")
            self.general_logger.info("Whisper mode disabled")
            time.sleep(0.5)

    def FineTuneFrequency(self,ftf):
        """Adjust laser frequency small amount, in GHz
        Rounded to nearest MHz
        Default laser can accept -30 to +30 GHz

        Args:
            ftf (float): frequency adjustment in MHz

        Returns:
            None
        """
        ftf_MHz = int(ftf*1000)
        ftf_MHz = ctypes.c_ushort(ftf_MHz).value #convert signed integer to unsigned integer

        byte3 = ftf_MHz&0xff
        byte2 = (ftf_MHz&0xff00)>>8
        resp = self.SendReceive(WRITE,REG_Ftf,byte2,byte3)
        self.general_logger.info("Fine tune frequency set to " + str(ftf))
        return resp

    def SetChannel1(self):
        """Makes sure the laser turns on in it's standard channel

        Args:
            None

        Returns:
            None
        """

        self.SendReceive(WRITE,REG_Channel,0x00,0x01)
        self.general_logger.info("Set to channel 1 to make sure laser comes on at FCF")
        
    def Shutdown(self):
        """Ends any sweeps laser might be doing, turns laser off and closes serial port

        Args:
            None

        Returns:
            None
        """

        self.EnableSweep(False)
        self.EnableWhisperMode(False)
        self.EnableLaser(False)
        self.sercon.close()
        self.general_logger.info("Safely shutting down laser and closing serial port")
        
    ##############################################################################################################
    #   Functions for the Clean Sweep feature
    ##############################################################################################################

    def SetSweepRange(self,range):
        """Set Clean Sweep range in GHz
        Range will be rounded to nearest GHz

        Args:
            range (int): Range in GHz

        Returns:
            None
        """

        byte3 = range&0xff
        byte2 = (range&0xff00)>>8
        self.SendReceive(WRITE,REG_Csweepamp,byte2,byte3)
        self.general_logger.info("Sweep range set to " + str(range) + " GHz")
        print("Sweep range set to " + str(range) + " GHz")

    def SetSweepRate(self,rate):
        """Set Clean Sweep rate in GHz/s
        Rate will be rounded to nearest 0.001 GHz/s

        Args:
            range (float): Rate in GHz/s

        Returns:
            None
        """

        rateMHz = int(rate*1000)
        byte3 = rateMHz&0xff
        byte2 = (rateMHz&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscanf1,byte2,byte3)
        self.general_logger.info("Sweep rate set to " + str(rate) + " GHz/s")
        print("Sweep rate set to " + str(rate) + " GHz/s")

    def EnableSweep(self,state):
        """Turn sweeping on/off
        Will automatically wait for laser to relock after disabling sweep

        Args:
            state (bool): True -> start sweep. False -> stop sweep

        Returns:
            None
        """

        if state == True:
            self.SendReceive(WRITE,REG_Csweepsena,0x00,0x01)
            self.general_logger.info("Laser sweep enabled")
            print("Sweep enabled")
            if self.teensy_connected:
                self.EnableTeensyMonitor(True)
        else:
            if self.teensy_connected:
                self.EnableTeensyMonitor(False)
                # clear anything sent my the teensy that snuck through because of timing mismatch
                time.sleep(1)
                while self.sercon.inWaiting():
                    self.sercon.read(1)
            self.SendReceive(WRITE,REG_Csweepsena,0x00,0x00)
            self.general_logger.info("Laser sweep disabled")
            print("Sweep disabled")
            

    def ReadOffsetFreq(self):
        """Reads laser current frequency offset

        Args:
            None

        Returns:
            float: the frequency offset in GHz
        """

        data = self.SendReceive(READ,REG_Csweepoffset,0x00,0x00)
        # if data > 65535/2:
        #   data = (data - 65535)*0.1
        (data - 2000)*0.1
        return data

    def SweepWithMonitor(self, num_sweeps,scope=''):
        self.EnableSweep(True)
        previous_offset = 0
        previous_slope = 0
        sweep_counter = -1   #start counter at -1 so I don't count the starting of the sweep as it turning around
        has_triggered = False
        while sweep_counter < num_sweeps:
            if self.sercon.inWaiting() > 0:
                scan_status, current_offset = self.TeensyReadStatus()
                if current_offset - previous_offset > 0: #if frequency is increasing
                    if previous_slope <= 0: #if previously was non-increasing
                        sweep_counter +=1
                if current_offset - previous_offset < 0: #if frequency is decreasing
                    if scope!='': #if a scope was given, then trigger it now
                        if not has_triggered:
                            has_triggered = True
                            scope.trigger_manually()
                previous_slope = current_offset - previous_offset
                previous_offset = current_offset
            time.sleep(0.00001)
        self.EnableSweep(False)
        # clear anything sent my the teensy that snuck through because of timing mismatch
        time.sleep(1)
        while self.sercon.inWaiting():
            self.sercon.read(1)

    ##############################################################################################################
    #   Functions for the Clean Jump feature
    #   Note I haven't used these functions thoroughly so there might be bugs
    ##############################################################################################################

    def SetNextFrequency(self,freq):
        """Set the next frequency to jump to, in THz
        The frequency will the rounded to the nearest 0.1GHz

        Args:
            freq (float): The frequency in THz

        Returns:
            None
        """

        #Set THz register
        freqTHz = int(freq)
        THzbyte3 = freqTHz&0xff
        THzbyte2 = (freqTHz&0xff00)>>8
        dataTHz = self.SendReceive(WRITE,REG_CjumpTHz,THzbyte2,THzbyte3)
        
        #Set GHz register
        freqGHz = int(round((freq-freqTHz)*10000.0))
        GHzbyte3 = freqGHz&0xff
        GHzbyte2 = (freqGHz&0xff00)>>8
        dataGHz = self.SendReceive(WRITE,REG_CjumpGHz,GHzbyte2,GHzbyte3)
        print('Next jump frequency set to ' + str(dataTHz) + '.' + str(dataGHz) + ' THz')
        self.general_logger.info("Next jump frequency set to " + str(dataTHz) + "." + str(dataGHz) + " THz")

    def SetNextSled(self,sled):
        """Set the next temperature sled to jump to, in degrees celcius
        The temperature will the rounded to the nearest 0.01 C

        Args:
            sled (float): The temperature in C

        Returns:
            None
        """
        sled = int(sled*100)
        byte3 = sled&0xff
        byte2 = (sled&0xff00)>>8
        datasled = self.SendReceive(WRITE,REG_CjumpSled,byte2,byte3)
        self.general_logger.info("Next jump sled set to " + str(datasled/100.0) + " C")

    def SetNextCurrent(self,current):
        """Set the next current to jump to, in milliamps
        The current will the rounded to the nearest 0.1 mA

        Args:
            sled (current): The current in mA

        Returns:
            None
        """

        current = int(current*10)
        byte3 = current&0xff
        byte2 = (current&0xff00)>>8
        datacurrent = self.SendReceive(WRITE,REG_CjumpCurrent,byte2,byte3)
        self.general_logger.info("Next jump current set to " + str(datacurrent/10.0) + " mA")

    def ExecuteJump(self):
        """Execute jump

        Args:
            None

        Returns:
            None
        """
        self.general_logger.info("Executing jump")
        print("Executing jump")
        #You need to send the command four times:
        #First transfers frequency, temperature and current to memory
        #Second calculates filter 1
        #Third calculates fitler 2
        #Fourth executes the jump
        self.SendReceive(WRITE,REG_Cjumpon,0x00,0x01)
        self.SendReceive(WRITE,REG_Cjumpon,0x00,0x01)
        self.SendReceive(WRITE,REG_Cjumpon,0x00,0x01)
        self.SendReceive(WRITE,REG_Cjumpon,0x00,0x01)

    def ReadError(self):
        """Reads error from target jump frequency

        Args:
            None

        Returns:
            float: the error in GHz
        """
        error = self.SendReceive(READ,REG_Cjumpoffset,0x00,0x00)
        error = unsigned_to_signed(error)*0.1 
        return error
    
    def WaitToStabilise(self, threshold):
        """Wait until the error after a jump is within a threshold of the target frequency

        Args:
            threshold (float): the threshold in GHz

        Returns:
            None
        """
        while True:
                    error = self.ReadError()
                    if abs(error) <= threshold:
                        print('Locked at a temperature of {} C'.format(self.ReadTemp()))
                        self.general_logger.info('Locked at a temperature of {} C'.format(self.ReadTemp()))
                        
                        break
                    time.sleep(0.1)

    ##############################################################################################################
    #   Functions for the Clean Scan feature
        # Note you need a different firmware to use this functionality
    ##############################################################################################################

    def SetScanSled(self,sled):
        """Set the sled temperature of the next sweep, in degrees celcius
        The temperature will the rounded to the nearest 0.01 C

        Args:
            sled (float): The temperature in C

        Returns:
            None
        """
        sled_temp = int(sled*1000)
        byte3 = sled_temp&0xff
        byte2 = (sled_temp&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscansled,byte2,byte3)
        self.general_logger.info("Next scan sled set to " + str(sled) + " C")

    def SetFilter1(self,temp):
        """Set filter 1 temperature of the next sweep, in degrees celcius
        Temperature is rounded to nearest 0.001 C

        Args:
            temp (float): The temperature in C

        Returns:
            None
        """

        temp_temp = int((temp-50)*1000)
        byte3 = temp_temp&0xff
        byte2 = (temp_temp&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscanf1,byte2,byte3)
        self.general_logger.info("Filter 1 set to " + str(temp) + " C")

    def SetFilter2(self,temp):
        """Set filter 1 temperature of the next sweep, in degrees celcius
        Temperature is rounded to nearest 0.001 C

        Args:
            temp (float): The temperature in C

        Returns:
            None
        """

        temp_temp = int((temp-50)*1000)
        byte3 = temp_temp&0xff
        byte2 = (temp_temp&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscanf2,byte2,byte3)
        self.general_logger.info("Filter 2 set to " + str(temp) + " C")

    def SetCurrent(self,current):
        """Set the current of the next sweep, in milliamps
        Current is rounded to nearest 0.1 mA

        Args:
            current (float): The current in mA

        Returns:
            None
        """
        current = int(current*10)
        byte3 = current&0xff
        byte2 = (current&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscancurrent,byte2,byte3)
        self.general_logger.info("Current in centre of scan set to " + str(current) + " mA")

    def SetCurrentAdjust(self,adjust1,adjust2):
        """Set the current of the next sweep, in milliamps
        Current is rounded to nearest 0.1 mA

        Args:
            adjust1 (float): Current adjust 1
            adjust2 (float): Current adjust 2

        Returns:
            None
        """
        adjust1 = int(adjust1*10)
        adjust2 = int(adjust2*10)
        byte3 = adjust2&0xff
        byte2 = adjust1&0xff
        self.SendReceive(WRITE,REG_Cscancurrentadjust,byte2,byte3)
        self.general_logger.info("Current adjust set to {}, {}".format(adjust1,adjust2))

    def EnableScan(self,state):
        """Turn clean scan on/off

        Args:
            state (bool): True -> turn on scan. False -> turn off scan

        Returns:
            None
        """
        if state == True:
            self.SendReceive(WRITE,REG_Cscanon,0x00,0x01)
            self.general_logger.info("Laser scan enabled")
            print("scan enabled")
        else:
            self.SendReceive(WRITE,REG_Cscanon,0x00,0x00)
            self.general_logger.info("Laser scan disabled")
            print("scan disabled")

    def SetScanAmplitude(self,freq):
        """Set the amplitude of the continuous scan segments, in gigahertz
        Rounded to the nearest 1 GHz

        Args:
            current (freq): The scan amplitude in GHz

        Returns:
            None
        """

        byte3 = freq&0xff
        byte2 = (freq&0xff00)>>8
        self.SendReceive(WRITE,REG_Cscanamp,byte2,byte3)
        self.general_logger.info("Scan amplitude set to " + str(freq) + " GHz")
    
    def LockSled(self):
        """Lock the sled temperature
        If clean mode is on, this this will instead start the clean scan

        Args:
            None

        Returns:
            None
        """

        self.SendReceive(WRITE,REG_Cscanon,0x00,0x01)
        self.general_logger.info("Set sled temperature. If clean mode is on, this this will instead start the clean scan")

    def EnableCleanMode(self,state):
        """Adjust laser frequency small amount, in GHz
        Rounded to nearest MHz

        Args:
            ftf (float): frequency adjustment in MHz

        Returns:
            None
        """

        if state == True:
            self.SendReceive(WRITE,REG_Mode,0x00,0x01)
            self.general_logger.info("Clean mode enabled")
            print("Clean mode enabled")
        else:
            self.SendReceive(WRITE,REG_Mode,0x00,0x00)
            self.general_logger.info("Clean mode disabled")
            print("Clean mode disabled")        

    def ScanStatus(self):
        """Gives a full status update of where the laser is in the clean scan

        Args:
            None

        Returns:
            None
        """


        power = self.SendReceive(READ,REG_Oop,0x00,0x00)/100

        #The Reg_Sscanon (0xE5) register is rather involved:
        # Provides status information about the clean scan
        # bit 0 is set to 1 if the next setpoint has been loaded
        # bit 1 is set to 1 if the CleanScan is ongoing
        # bit 3 and 2 are 01 if the sweep is going to higher frequency
        # bit 3 and 2 are 10 if the sweep is going to lower frequency
        resp = self.SendReceive(READ,REG_Cscanon,0x00,0x00)

        mask1 = 0b0001
        mask2 = 0b0110

        if resp & mask1 == 1:
            loaded = True
        else:
            loaded = False

        if ((resp & mask2)>>1) == 1:
            slope = "Increasing"
        elif ((resp & mask2)>>1) == 2:
            slope = "Decreasing"
        else:
            slope = "Error!"
        

        #This is an AEA address, check the manual
        self.SendReceive(READ,0x58,0x00,0x00)       
        gainchip_temp = self.SendReceive(READ,REG_AeaEar,0x00,0x00)
        gainchip_temp = (ctypes.c_short(gainchip_temp).value)/100
        case_temp = self.SendReceive(READ,REG_AeaEar,0x00,0x00)
        case_temp = (ctypes.c_short(case_temp).value)/100

        #This is an AEA address, check the manual
        self.SendReceive(READ,0x57,0x00,0x00)
        gainchip_current = self.SendReceive(READ,REG_AeaEar,0x00,0x00)*0.1
        TEC_current = self.SendReceive(READ,REG_AeaEar,0x00,0x00)*0.1

        # offset = self.SendReceive(READ,REG_Cscanoffset,0x00,0x00)
        # offset = (offset - 2000)*0.1
        offset =  1

        print("Next point loaded: {}, slope: {}, {:5.2f} dBm, Chip {:05.2f} C, Case {:05.2f} C, Offset {:.1f} GHz".format(loaded,slope,power,gainchip_temp,case_temp,offset))


    ##############################################################################################################
    #   Other functions
    ##############################################################################################################

    def ReadTemp(self):
        #I think this reads laser temperature
        data = self.SendReceive(READ,0x43,0x00,0x00)
        data = data*0.01
        self.general_logger.info("Laser temperature is " + str(data))
        return data

    def ReadDeviceTemp(self):
        #This reads the 'device temperature' instead of the 'laser temperature'. I'm unsure what the difference is
        data = self.SendReceive(READ,0x58,0x00,0x00)
        data = data
        self.general_logger.info("Device temperature is " + str(data))
        return data

    def ReadDeviceCurrent(self):
        data = self.SendReceive(READ,0x57,0x00,0x00)
        data = data
        self.general_logger.info("Device current is " + str(data))
        return data

    ##############################################################################################################
    #   Functions for communicating with Teensy
    ##############################################################################################################

    def TeensyReadStatus(self):
        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 66:
            print('Error! I expected to read the power level but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 66, got " + byte1)
        power = ((byte2 << 8) + byte3)/100

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 11:
            print('Error! I expected to read the AEA but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 11, got " + byte1)
        laser_temperature = ((byte2 << 8) + byte3)/100

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 11:
            print('Error! I expected to read the AEA but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 11, got " + byte1)
        case_temperature = ((byte2 << 8) + byte3)/100

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 11:
            print('Error! I expected to read the AEA but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 11, got " + byte1)
        laser_current = (byte2 << 8) + byte3

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 11:
            print('Error! I expected to read the AEA but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 11, got " + byte1)
        TEC_current = (byte2 << 8) + byte3

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 230:
            print('Error! I expected to read the frequency offset but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 230, got " + byte1)
        offset = ((byte2 << 8) + byte3 - 2000)*0.1  #encoding for CleanScan
        offset = (unsigned_to_signed((byte2 << 8) + byte3))*0.1  #encoding for CleanSweep
        

        byte0, byte1, byte2, byte3 = self.Receive_response()
        if byte1 != 229:
            print('Error! I expected to read the scan status but instead got a response from register ' + str(byte1))
            self.general_logger.error("Expected register 229, got " + byte1)
        scan_status = (byte2 << 8) + byte3

#        print("{:5.2f} dBm, Chip {:05.2f} C, Case {:05.2f} C, Offset {:.1f} GHz".format(power,laser_temperature,case_temperature,offset))
        
        return scan_status, offset

    def EnableTeensyMonitor(self,state):
        if state == True:
            self.Send_command(255,255,255,255)
            self.general_logger.info("Putting teensy in to monitor mode")
        else:
            self.Send_command(254,254,254,254)
            self.general_logger.info("Taking teensy out of monitor mode")
            
    
    def SetLoggers(self,general_logger,lasercomms_logger):
        self.general_logger = general_logger
        self.lasercomms_logger = lasercomms_logger
    
def unsigned_to_signed(num):
    if 0 <= num < 2**15:
        ret = num
    elif 2**15 <= num <= 2**16:
        ret = (num-2**16)
    else:
        print('Error! input it outside the range of a 2 byte number')
    return ret

