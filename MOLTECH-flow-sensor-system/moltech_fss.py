"""
Communications with MOLTECH-FSS Flow Sensor modules

Serial USB communications.
"""
import serial

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
            # invalid reply received
            return None 
        else:
            return decodata[:-1]
        
    def close(self):
        self.sport.close()
        
    def get_measurement(self):
        self.sport.write(b'M!')
        indata = self.get_response()
        return indata
        
    

class MOLTECH_FSS_dummy:
    """Dummy version, for development purposes
    
    Does not need a connected FSS module
    """
    def __init__(self, port_str, baudrate=9600):
        self.port_str = port_str
        self.ser_timeout = 2.0 
        self.baudrate = baudrate
        self.sport = None
        self.name = "MOLTECH flow sensor 00 (dummy)"
        self.info = """
-------------------------
Scale factor: 4
Units: nl/min
Units code: 2115
Firmware version: v2.2
-------------------------

        """
        
        self.simvalue = 0.5
        self.simdelta = 8.5
        self.simmax = 5000.
        self.simmin = -50.
        
    def get_response(self):
        pass
        
    def close(self):
        pass
        
    def get_measurement(self):
        indata = f"{self.simvalue:.2f}"
        self.simvalue += self.simdelta
        if (self.simvalue > self.simmax)\
           or (self.simvalue < self.simmin):
            self.simdelta = -self.simdelta
        return indata


