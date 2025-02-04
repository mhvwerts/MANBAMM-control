# -*- coding: utf-8 -*-
"""
Launch two independent AladdinPilot GUIs, one for controlling sample injection,
the other for controlling carrier pump.

TODO: cleaner console output, currently all launched processes print
to the same console, creating confused output.

Created on Wed Oct 18 11:10:08 2023

@author: Martinus Werts
"""

import subprocess
import sys

print()

print('**************************************')
print('*** AladdinPilot GUI multilauncher ***')
print('**************************************')
print()
print('Will Launch (p1) carrier pump GUI (pump only)')
print('Will launch (p2) carrier pump GUI (pump only)')
print('Close both GUI apps to finish cleanly!')
print()
print('**************************************')
print()
print('All subprocess console messages will appear below.')
print()
print('**************************************')
print()
input('Press enter to proceed!')
print()


p1 = subprocess.Popen([sys.executable, 'python-src/FlowInjectPilot.py', '9707'],
                        shell = True)


p2 = subprocess.Popen([sys.executable, 'python-src/FlowInjectPilot.py', '9717'],
                        shell = True)


p1.wait()
p2.wait()

