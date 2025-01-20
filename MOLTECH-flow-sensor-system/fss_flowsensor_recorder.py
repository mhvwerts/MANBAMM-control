"""
Flow rate recorder as part of the MOLTECH-FSS Flow Sensor System

This program communicates with MOLTECH-FSS modules via a USB serial link.

Hardware and firmware of the MOLTECH-FSS modules are described at
    https://github.com/mhvwerts/MANBAMM-control/tree/main/MOLTECH-flow-sensor-system


Martinus Werts, 2024
MOLTECH-Anjou, CNRS, Université d'Angers
"""

#%% CONFIGURATION
portstr = "COM5"
# portstr = None # development

Tsleep = 1.0
MAXITER = 20000

#%%

from time import sleep
from time import time
from datetime import datetime

if portstr is not None:
    from moltech_fss import MOLTECH_FSS
else:
    # simulated module for development purposes
    from moltech_fss import MOLTECH_FSS_dummy as MOLTECH_FSS



print('hello, world')
print()


fss = MOLTECH_FSS(portstr)


print(fss.name)
print(fss.info)

tfile = time()
dtfile = datetime.fromtimestamp(tfile)
tfstr_full = dtfile.isoformat()
tfstr = tfstr_full.split('.')[0]
outfname = fss.name + ' ' + tfstr.replace(':','-') + '.csv'

print(outfname)


fout = open(outfname, 'w')
fout.write('t0_abs_time_iso\t')
fout.write(tfstr_full)
fout.write('\n')
fout.write('time(s)\tflow(nlmin)\n')
for x in range(MAXITER):
    t_meas0 = time()
    flow_meas = fss.get_measurement()
    t_meas1 = time()
    t_meas = 0.5*(t_meas0+t_meas1) - tfile
    print(f"{t_meas:8.3f}\t{flow_meas}")
    fout.write(f"{t_meas:.3f}\t{flow_meas}\n")
    sleep(Tsleep)
    fout.flush()

fout.close()    
    
fss.close()
