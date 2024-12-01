"""
Communications with MOLTECH-FLSH Flashbox
(for firmware v1.0)

Serial USB communications.

Martinus Werts, 2024
MOLTECH-Anjou, CNRS, Université d'Angers
"""

import serial

from time import sleep

class MOLTECH_FLSH:
    def __init__(self, port_str, baudrate=19200):
        self.port_str = port_str
        self.ser_timeout = 2.0 # better safe than sorry
        self.baudrate = baudrate
        self.sport = serial.Serial(port_str, 
                                 baudrate = self.baudrate,
                                 timeout = self.ser_timeout)
                                 # default serial: 8N1
        
        # sleep is important!
        sleep(2.0) # give it some time to wake up (LOTS OF TIME...)
        
        self.flush_in() # flush buffer (superfluous)
        
        # initiate communication
        if not self.status_OK():
            raise SystemError('MOLTECH-FLSH Flashbox initialization error')
       
        # set time calibration
        # 'simple' calibration (for Arduino 16MHz, firmware 1.0)
        self.s_per_tick = 6.25e-6
        
        self.flush_in() # superfluous flush
    
    
    def flush_in(self):
        self.sport.read(self.sport.inWaiting()) # flush
    
        
    def get_status(self):
        self.sport.write(b'?')
        self.lastdata = self.sport.read(1)
        decodata = self.lastdata.decode('ascii')
        if decodata in ['.', '!', 'E']:
            return decodata
        else:
            # some unhandled error occurred?
            self.flush_in() # flush
            return None
  
        
    def status_OK(self):
        return (self.get_status() in ['!', '.'])
        
        
    def stop(self):
        self.sport.write(b'.')
        if not self.status_OK():
            raise IOError('MOLTECH-FLSH Flashbox communication error (.)')
        
        
    def go(self):
        self.sport.write(b'!')
        if not self.status_OK():
            raise IOError('MOLTECH-FLSH Flashbox communication error (!)')
        
    
    def set_period_s(self, period_s):
        # Here we use the 'simple' single-coefficient calibration, assuming
        # a constant loop time for the code (which is likely the case).
        # There may be a tiny constant offset somewhere, but this will
        # only show up for very short times
        Ntk_period = round(period_s / self.s_per_tick)
        comstr = f'P{Ntk_period}d'
        self.sport.write(comstr.encode('ascii'))
        if not self.status_OK():
            raise IOError('MOLTECH-FLSH Flashbox communication error (P)')
        self.Ntk_period = Ntk_period
        self.period_s = Ntk_period * self.s_per_tick
        
        
    def set_width_s(self, width_s):
        # Here we use the 'simple' single-coefficient calibration, assuming
        # a constant loop time for the code (which is likely the case).
        # There may be a tiny constant offset somewhere, but this will
        # only show up for very short times
        Ntk_width = round(width_s / self.s_per_tick)
        Ntk_on = 0 # hard-coded, simply start at 0 #TODO introduce phase/offset
        Ntk_off = Ntk_on + Ntk_width
        comstr = f'N{Ntk_on}d'
        self.sport.write(comstr.encode('ascii'))
        if not self.status_OK():
            raise IOError('MOLTECH-FLSH Flashbox communication error (N)')
        comstr = f'F{Ntk_off}d'
        self.sport.write(comstr.encode('ascii'))      
        if not self.status_OK():
            raise IOError('MOLTECH-FLSH Flashbox communication error (F)')
        self.Ntk_width = Ntk_width
        self.width_s = Ntk_width * self.s_per_tick
        

    def close(self):
        self.sport.close()
