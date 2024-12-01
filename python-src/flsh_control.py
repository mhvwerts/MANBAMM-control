# -*- coding: utf-8 -*-
"""
Control code example for MOLTECH Flashbox

A good test, and a first step to a full user interface.

M. H. V. Werts, 2024.
"""

portstr = "COM6"

from time import sleep
from devcomms.moltech_flsh import MOLTECH_FLSH



def pause():
    print('Pause 10 seconds')
    sleep(10)


flshbx = MOLTECH_FLSH(portstr)
print('Flashbox intialized.')

pause()


flshbx.stop()
print('Flashbox stopped.')
print(flshbx.get_status())


print('Set period to 0.5s')
flshbx.set_period_s(0.5)
print(flshbx.get_status())

print('Set width to 0.02s')
flshbx.set_width_s(0.02)
print(flshbx.get_status())

pause()


flshbx.go()
print('Flashbox restarted.')
print(flshbx.get_status())

pause()


flshbx.stop()
print('Flashbox stopped.')
print(flshbx.get_status())


print('Set period to 1 ms')
flshbx.set_period_s(0.001)
print(flshbx.get_status())

print('Set width to 50 µs')
flshbx.set_width_s(0.00005)
print(flshbx.get_status())

# In a first oscilloscope measurement (241201), I found
#   actual period = 1.001 ms (error +1 µs)
#   actual width = 51.60 µs (error +1.60 µs)
# This is within the ultimate resolution of the timing loop,
# which is 6.25 µs ('s_per_tick = 6.25e-6')
# This is only a problem of precise time calibration, the pulses are stable 
# and steady. No jitter on my oscilloscope!
# If needed, we can draw up a table with corrections for short pulses and
# periods. Alternatively, there may be some offset value to be applied to
# the real time part to get more precise values.



flshbx.go()
print('Flashbox restarted.')
print(flshbx.get_status())

pause()

print('wait some more for oscilloscope to be tuned!')
pause()


flshbx.stop()
print('Flashbox stopped.')
print(flshbx.get_status())


print('Set period to 2s')
flshbx.set_period_s(2)
print(flshbx.get_status())

print('Set width to 0.5s')
flshbx.set_width_s(0.5)
print(flshbx.get_status())


flshbx.go()
print('Flashbox restarted.')
print(flshbx.get_status())

pause()


flshbx.close()
