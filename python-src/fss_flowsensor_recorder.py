# -*- coding: utf-8 -*-
"""
Flow rate recorder as part of the MOLTECH-FSS Flow Sensor System

This program communicates with MOLTECH-FSS modules via a USB serial link.

Hardware and firmware of the MOLTECH-FSS modules are described at
    https://github.com/mhvwerts/MANBAMM-control/tree/main/MOLTECH-flow-sensor-system


Martinus Werts, 2024
MOLTECH-Anjou, CNRS, Université d'Angers
"""
import serial

portstr = "COM8"

class MOLTECH_FSS:
    def __init__(self, port_str, baudrate=9600):
        self.port_str = port_str
        self.ser_timeout = 2.0 # should be longer than FSS unit timeout
        self.baudrate = baudrate
        self.sport = serial.Serial(port_str, 
                                 baudrate = self.baudrate,
                                 timeout = self.ser_timeout)
                               #default serial: 9600 baud, 8N1
        self.sport.read(self.sport.inWaiting()) # flush buffer
        
        # initiate communication
        
        # first "dummy cycle" to reset comms
        # this will result in a defined state of the device
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
        
    

class MOLTECH_FSS_dummy:
    def __init__(self, port_str, baudrate=9600):
        self.port_str = port_str
        self.ser_timeout = 2.0 
        self.baudrate = baudrate
        self.sport = None
        self.name = """
-------------------------
Scale factor: 4
Units: nl/min
Units code: 2115
Firmware version: v2.2
-------------------------

        """
        self.info = "simple emulation for device-less development"
        
    def get_response(self):
        pass
        
    def close(self):
        pass
        
    def get_measurement(self):
        indata = "0.15" # TO DO make a fake data generator
        return indata



if __name__=='__main__':
    from time import sleep
    from time import time
    from datetime import datetime
    
    print('hello, world')
    fss = MOLTECH_FSS(portstr)
    print(fss.name)
    print(fss.info)
    
    tfile = time()
    dtfile = datetime.fromtimestamp(tfile)
    tfstr = dtfile.isoformat().split('.')[0]
    outfname = fss.name + ' ' + tfstr + '.csv'
    
    print(outfname)
    
    for x in range(10):
        t_meas0 = time()
        flow_meas = fss.get_measurement()
        t_meas1 = time()
        t_meas = 0.5*(t_meas0+t_meas1) - tfile
        print(t_meas, flow_meas)
        sleep(0.5)
    fss.close()
    