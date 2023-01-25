# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 17:30:06 2023

@author: Martinus Werts


Initial explorations for 'aladdin pilot v2'

This is very preliminary and should be adapted to the experiment in the lab.
For now, testing remote configuration of pump via RS232
"""

from time import sleep

from aladdin import Aladdin


# port and pump identifiers

# port_str = '/dev/ttyUSB0'
port_str = 'COM3'
pump_id = '02'


# test configuration sequence

ala = Aladdin(port_str)
for cmdstr in [
        
               
               # step 1: prepare stopped pump
               'VER','VER','STP', # make sure pump communicating and stopped (to do check expected responses)
               
               # step 2: check preferences!
               'PF',#todo if not OK, set value (THIS SHOULD BE 0, the pump should stop after power disruption)
               
               # step 2: reset program
               # overwrite current program with standard 'unprogrammed' operation
               # I do not know how to delete steps from program via RS232
               'PHN2','FUNSTP', # second phase stop pump 'end program?)
               'PHN1','FUNRAT','VOL0.0', # first phase: infinite injection
               
               # step 3: with the standard program in place, we can use pump as normal
               'DIA20.0', # TODO select 'valid' diameters (syringes) - this control units for VOL
               'RAT17.77UM', # rate
               'DIRINF', # inject
               'CLDINF', # clear dispensed volume (inject)
               'DIS', #THIS COMMAND PROVIDES THE UNITS for the VOL command
                        # anyways, we will not use VOL now, but we will in future
               #
               ]:
    print('===============')
    print('cmdstr = ', cmdstr)
    pump_status, pump_reply = ala.pump_cmd(pump_id, cmdstr)
    print('reply = ', pump_reply, '    status = ',pump_status)
    print('================')
    sleep(1)
    
print()
print()

ala.close()


