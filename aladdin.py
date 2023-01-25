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
        self.last_sendstr = None
        self.last_reply = None
        self.last_pumpid = None
        self.last_pumpstatus = None
        self.last_pumpreply = None

    def send_recv(self, sendstr_in):
        self.last_sendstr = sendstr_in
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
    
    def pump_cmd(self, idstr: str, cmdstr: str ) -> (str, str):
        #TODO: check idstr (using regexp)
        #TODO; check cmdstr
        sendstr = idstr + cmdstr
        reply = self.send_recv(sendstr)
        # decode expected reply, and raise error if not coherent
        # TODO: improve error handling by raising Exceptions
        # reply can be None!! this should be handled
        # if error raised => close communications? or try recovery... (retries...)
        #   for now, make that decision in the main program
        assert len(reply) > 2, 'unexpected response. sent: '+sendstr+\
            ', received: '+reply
        pumpid = reply[0:2]
        assert pumpid == idstr, 'pump idstr not OK. sent: '+sendstr+\
            ', received: '+reply
        pumpstatus = reply[2]
        # allowable pump statuses (for now - we do not support withdraw)
        assert pumpstatus in ['A', 'P','S','I'],\
            'pump status not supported. sent: '+sendstr+\
                ', received: '+reply
        pumpreply = reply[3:]
        self.last_pumpid = pumpid
        self.last_pumpstatus = pumpstatus
        self.last_pumpreply = pumpstatus
        return (pumpstatus, pumpreply)
    
    def close(self):
        self.ser.close()



if __name__=='__main__':
    # TODO put some self test code here
    pass
