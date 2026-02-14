"""
Python client module for MOLTECH-VICI-TTL-control

M. H. V. Werts, 2026


The class VICI_TTL for communication and valve control has been designed to
have the same interface as VICI_EUHA in vici_euha.py

When adapting the MOLTECH-VICI-TTL firmware, carefully check and update
the hardcoded timings and device '!' identification string in VICI_TTL.init()

If the MOLTECH-VICI-TTL device receives a command before finishing the pause
specified in the firmware, the command will be ignored and a reply will not
be sent.

The code is somewhat messy; it could be refactored. The frequent use of 
`assert` is perhaps not elegant, but it is efficient in this case as we are
in the prototype phase. The code appears to work for us. Use at your own risk!

WARNING: BEFORE USE, MAKE SURE THAT THE VALVE ACTUATOR HAS BEEN CONFIGURED TO
         FUNCTION IN TWO-POSITION MODE!
         
TODO: - see TODOs in code comments
      - instead of (in addition to) printing messages, pass these to some
        messaging/logging system so that the calling code can do something with
        it.
"""

from time import sleep
import serial
from serial import Serial

class VICI_TTL:
    def __init__(self, port_str):
        
        #####
        # Here are the communication timings.
        # They should be carefully tuned to fit with the delays
        # specified in the 'VICI_TTL_firmware.ino' Arduino firmware.
        # Hardcoded for now, need to be manually changed. A shared
        # config-file would be overkill.
        self.LPAUSE = 1.0 # "long" pause (in seconds)
        self.PAUSE = 0.12  # pause (in seconds)
        self.ser_timeout = 2.0 # give enough time for Arduino to reply!!

        self.port_str = port_str

        #####
        # Open serial port
        self.ser = Serial(port=self.port_str,
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.ser_timeout)
        sleep(1.0) # Needed for some Arduino boards... tweak if initialization
                   # problems
                
        # Serial comms: wait , flush, wait, and check if things are quiet
        sleep(self.LPAUSE) # just a pause
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        sleep(self.LPAUSE)
        assert self.ser.in_waiting == 0, "PORT NOT QUIESCENT"
        assert self.ser.out_waiting == 0, "PORT NOT QUIESCENT"
        

        #####
        # Initial communication with MOLTECH-VICI-TTL device:
        # check communications by sending a command and checking expected
        # response
        self.ser.write(b'!')
        reply = self.ser.read_until('!')
        if reply==b'Hello, this is MOLTECH-VICI-TTL control v260213a (dummy firmware)!':
            print('WARNING! Running dummy firmware. Valve actuator inactive.')
        elif not reply==b'Hello, this is MOLTECH-VICI-TTL control v260213a!':
            self.ser.close()
            print('reply = ', reply)
            raise IOError('VICI TTL control not communicating cleanly. Check device!')
            
        # The following check can not be done via VICI_TTL
        # MAKE SURE YOURSELF THAT THE VALVE HAS BEEN PROPERLY CONFIGURED!
        # # checking that operation be two-position with stops (= factory default) ...')
        # if not(self.sendrecv('AM')=='AM1'):
        #     # Valve not well configured DANGER!
        #     self.ser.close()
        #     raise Exception('EUHA valve configuration error! DANGER! (should be AM1)')

    
    def sendrecv(self, send_str):
        
        # TO DO: ADD LOGGING 
        #        (list of sends and list of replies, with time-stamps,
        #        these lists may be saved for additional experiment timing
        #        info)
        
        assert len(send_str)==1, 'Only single-character commands!'
        
        # empty read buffer before sending anything, making sure that
        # the reply read is indeed the answer to the command.
        self.ser.reset_input_buffer()
        self.ser.write(send_str)
        self.lastreply = self.ser.read(size=1)
        sleep(self.PAUSE) # GIVE TIME to arduino firmware to recover!
        return self.lastreply

        
    def get_pos(self):
        reply = self.sendrecv(b'?')
        if reply == b'B':
            pos = 'B'
        elif reply== b'A':
            pos = 'A'
        else:
            print("VICI-TTL GLITCH! did not receive valid answer to '?'...")
            pos = None
        return pos
    
    
    def set_pos(self, pos):
        if pos == 'B':
            cmdstr = b'b'
            chkstr = b'B'
        elif pos == 'A':
            cmdstr = b'a'
            chkstr = b'A'
        else:
            raise ValueError('Unknown VICI-TTL position.')
        reply = self.sendrecv(cmdstr)
        if reply != chkstr:
            print('VICI-TTL GLITCH! bad valve reply: ', reply)
            # TO DO: log this also

        
    def close(self):
        self.ser.close()



if __name__=='__main__':
    
    print('module self test.')
    
    comport = "COM6"
    immobile = False # if false will physically actuate the valve
    
    euha = VICI_TTL(comport)
    
    initialpos = euha.get_pos()
    print('initial position =', initialpos)
    
    if not immobile:
        euha.set_pos('A')
        print(euha.get_pos())
        euha.set_pos('B')
        print(euha.get_pos())
        euha.set_pos('A')
        print(euha.get_pos())
        euha.set_pos(initialpos)
        
    finalpos = euha.get_pos()
    print('final position =', finalpos)
    
    euha.close()

