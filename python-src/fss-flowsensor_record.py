# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 15:23:36 2024

@author: MOLTECHadmin
"""

import serial
from time import sleep

portstr = "COM8"

class MOLTECH_FSS:
    def __init__(self, port_str, baudrate=9600):
        self.port_str = port_str
        self.ser_timeout = 2.0
        self.baudrate = baudrate
        self.sport = serial.Serial(port_str, 
                                 baudrate = self.baudrate,
                                 timeout = self.ser_timeout)
                               #default serial: 9600 baud, 8N1
        self.sport.read(self.sport.inWaiting()) # flush buffer
        
        # initiate communication
        
        # first "dummy cycle"
        self.sport.write(b'!')
        self.sport.read_until(b'!')
        self.sport.read(self.sport.inWaiting()) # flush
        
        # get sensor name
        self.sport.write(b'?!')
        self.name = self.get_response()
        self.sport.read(self.sport.inWaiting()) # flush
        
        # get sensor info
        self.sport.write(b'I!')
        self.info = self.get_response()
        self.sport.read(self.sport.inWaiting()) # flush
        
        
    def get_response(self):
        self.lastdata = self.sport.read_until(b'!')
        decodata = self.lastdata.decode('ascii')
        if not decodata.endswith('!'):
            decodata = None # invalid reply
        return decodata[:-1]
        
    def close(self):
        self.sport.close()
        
    def get_measurement(self):
        self.sport.write(b'M!')
        indata = self.get_response()
        return indata
        

if __name__=='__main__':
    print('hello, world')
    fss = MOLTECH_FSS(portstr)
    print(fss.name)
    print(fss.info)
    for x in range(10):
        print(fss.get_measurement())
        sleep(0.5)
    fss.close()
    