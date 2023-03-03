# -*- coding: utf-8 -*-
"""
VICI EUHA control via RS232

This  is the VICI EUHA control module, easy to import and use, much like `aladdin.py`

A child class 'Newserial' is created from 'Serial' (pyserial) to facilitate communications with the VICI EUHA interface, in particular handling ASCII conversion and CRLF handling.

"""
from time import sleep
import serial
from serial import Serial



class Newserial(Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.PAUSE = 0.1  # should this be fine-tuned? 0.05 too short for valve change, 0.1 seems OK
        self.LPAUSE = 0.5
        
    def ultraflush(self):
        # RESET and check if things are quiet
        sleep(self.LPAUSE) # just a pause
        self.reset_input_buffer()
        self.reset_output_buffer()
        sleep(self.LPAUSE)
        assert self.in_waiting == 0, "PORT NOT QUIESCENT"
        assert self.out_waiting == 0, "PORT NOT QUIESCENT"
        
    def ultrawrite(self, wstr):
        wb = bytes(wstr, encoding='ascii')
        self.write(wb+b'\r\n')
        sleep(self.PAUSE) # give it some time to execute the command
        
    def ultraread(self):
        rcd = bytes()
        while self.in_waiting > 0:
            while self.in_waiting > 0:
                rin = self.read()
                rcd += rin
            sleep(self.PAUSE) # give it some time to cough up the full reply
        return rcd.decode('ascii')



class VICI_EUHA:
    def __init__(self, port_str):
        self.port_str = port_str
        self.ser_timeout = 1.0
        self.ser = Newserial(port=self.port_str,
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.ser_timeout)
        self.ser.ultraflush()
        
        # check communications by sending a command and checking expected
        # response
        if not(self.sendrecv('VR')[-10:]=='UA_MAIN_EQ'):
            # device reply not recognized. close serial
            self.ser.close()
            raise Exception('After opening serial comms: unexpected (or empty) device response')
            
        # checking that operation be two-position with stops (= factory default) ...')
        if not(self.sendrecv('AM')=='AM1'):
            # Valve not well configured DANGER!
            self.ser.close()
            raise Exception('EUHA valve configuration error! DANGER! (should be AM1)')

    
    def sendrecv(self, send_str):
        self.ser.ultrawrite(send_str)
        self.lastreply = self.ser.ultraread()
        return self.lastreply.strip()

        
    def autotest(self, immobile = True):
        print('Test comms...')
        if not immobile:
            print('     and valve...')
       
        # try some comms, just send in burst
        self.ser.ultrawrite('/?')
        print(self.ser.ultraread())
        
        self.ser.ultrawrite('VR')
        print(self.ser.ultraread())
        
        self.ser.ultrawrite('VR1')
        print(self.ser.ultraread())
        
        self.ser.ultrawrite('VR2')
        print(self.ser.ultraread())
        
        self.ser.ultrawrite('CP')
        print(self.ser.ultraread())
        
        if not immobile:
            self.ser.ultrawrite('GOA')
            print(self.ser.ultraread())
            
            self.ser.ultrawrite('CP')
            print(self.ser.ultraread())
            
            self.ser.ultrawrite('GOB')
            print(self.ser.ultraread())
            
        self.ser.ultrawrite('CP')
        print(self.ser.ultraread())


    def get_pos(self):
        pos_str = self.sendrecv('CP')
        if pos_str=='CPB':
            pos = 'B'
        elif pos_str=='CPA':
            pos = 'A'
        else:
            print('EUHA GLITCH! did not receive valid answer to CP...')
            pos = None
        return pos
    
    def set_pos(self, pos):
        if pos == 'B':
            cmd_str = 'GOB'
        elif pos == 'A':
            cmd_str = 'GOA'
        else:
            raise ValueError('Unknown EUHA position.')
        self.sendrecv(cmd_str)

        
    def close(self):
        self.ser.close()


if __name__=='__main__':
    
    print('module self test.')
    
    comport = "COM10"
    immobile = False # if false will physically actuate the valve
    
    euha = VICI_EUHA(comport)
    
    euha.autotest(immobile = True)
    
    if not immobile:
        euha.set_pos('A')
        print(euha.get_pos())
        euha.set_pos('B')
        print(euha.get_pos())
    
    euha.close()
