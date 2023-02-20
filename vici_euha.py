# -*- coding: utf-8 -*-
"""
A first example of VICI EUHA control via RS232

A child class 'Newserial' is created from 'Serial' (pyserial) to facilitate communications with the VICI EUHA interface, in particular handling ASCII conversion and CRLF handling.

This prototype script will evolve into a VICI EUHA control module, easy to import and use, much like `aladdin.py`

To do:
- put the vici_euha control into a class of its own

"""
from time import sleep
import serial
from serial import Serial

comport = "COM10"
PAUSE = 0.1
LPAUSE = 0.5



class Newserial(Serial):
    def ultraflush(self):
        # RESET and check if things are quiet
        sleep(LPAUSE) # just a pause
        self.reset_input_buffer()
        self.reset_output_buffer()
        sleep(LPAUSE)
        assert self.in_waiting == 0, "PORT NOT QUIESCENT"
        assert self.out_waiting == 0, "PORT NOT QUIESCENT"
        
    def ultrawrite(self, wstr):
        wb = bytes(wstr, encoding='ascii')
        self.write(wb+b'\r\n')
        sleep(PAUSE)        
        
    def ultraread(self):
        rcd = bytes()
        while self.in_waiting > 0:
            while self.in_waiting > 0:
                rin = sp.read()
                rcd += rin
            sleep(PAUSE)
        return rcd.decode('ascii')




sp = Newserial(port=comport,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0)

print('Ultraflushing comm buffer...')
sp.ultraflush()

print('Test comms and valve...')

print('... not yet using device ID ...')

print('... not yet checking that operation be two-position with stops (= factory default) ...')

print('... all this should be done: TO DO ...')

# try some comms
sp.ultrawrite('/?')
print(sp.ultraread())

sp.ultrawrite('VR')
print(sp.ultraread())

sp.ultrawrite('VR1')
print(sp.ultraread())

sp.ultrawrite('VR2')
print(sp.ultraread())

sp.ultrawrite('CP')
print(sp.ultraread())

sp.ultrawrite('GOA')
print(sp.ultraread())

sp.ultrawrite('CP')
print(sp.ultraread())

sp.ultrawrite('GOB')
print(sp.ultraread())

sp.close()
