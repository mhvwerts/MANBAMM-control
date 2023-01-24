# -*- coding: utf-8 -*-

from time import sleep
import serial

class Aladdin:
    def __init__(self, port_str, baudrate = 9600):
        self.port_str = port_str
        self.ser_timeout = 1.0
        self.baudrate = baudrate
        self.ser = serial.Serial(port_str, 
                                 baudrate = self.baudrate,
                                 timeout = self.ser_timeout)
                               #default serial: 9600 baud, 8N1
        self.ser.read(self.ser.inWaiting()) # flush buffer
        #TODO: establish and test communication
        #TODO: make communications with pump more robust towards interrupts (reconnect after error)
    
    def send_recv(self, sendstr_in):
        sendstr = sendstr_in.encode(encoding='ascii') + b'\r'
        self.ser.write(sendstr)
        reply = bytes()
        readch = self.ser.read(1)
        if len(readch) == 0:
            reply = None
        else:
            if readch != b'\x02':
                print('Warning: STX not received')
                reply = readch + self.ser.read(self.ser.inWaiting())
            else:
                readch = self.ser.read(1)
                while ((readch != b'\x03') and (len(readch) != 0)):
                    reply = reply + readch
                    readch = self.ser.read(1)
        if reply is not None:
            try:
                reply = reply.decode(encoding='ascii')
            except UnicodeDecodeError:
                print("Error in decoding reply from pump. Check communication cables.")
                sleep(self.ser_timeout) # wait a while
                self.ser.read(self.ser.inWaiting()) # flush buffer
                reply = "<COMMUNICATION ERROR>"
        self.last_reply = reply
        return reply
    
    def close(self):
        self.ser.close()



if __name__=='__main__':
    # TODO put some self test code here
    pass
