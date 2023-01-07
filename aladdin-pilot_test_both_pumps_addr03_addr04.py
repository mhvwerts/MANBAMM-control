# -*- coding: utf-8 -*-

__version__ = '230107'

from time import sleep

from aladdin import Aladdin



# Parameters

# port_str = '/dev/ttyUSB0'
port_str = 'COM7'



# Run
ala = Aladdin(port_str)

# check connection with pump and stop pump (addr03 addr04)
for comstr in ['04VER', '03VER',
               '03STP', '04STP']:
    print('===============')
    print('comstr = ', comstr)
    reply = ala.send_recv(comstr)
    print('reply = ', reply)
    print('================')
    sleep(1)
    
print()
print()

ala.close()
