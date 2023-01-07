# -*- coding: utf-8 -*-

__version__ = '230107'

from time import sleep, time, strftime

from aladdin import Aladdin        



# Parameters

logfname = 'INJEKTxxxxxxA.txt'
time_on = 60.
time_period = 1200.
timer_sleep = 0.02

# port_str = '/dev/ttyUSB0'
port_str = 'COM6'
baudrate = 9600



# Run
ala = Aladdin(port_str, baudrate)

# check connection with pump 4 and stop pump
for comstr in ['04VER', '04STP']:
    print('===============')
    print('comstr = ', comstr)
    reply = ala.send_recv(comstr)
    print('reply = ', reply)
    print('================')
    sleep(1)
    
print()
print()

t0 = time()
t00 = t0
N = 0

fout = open(logfname,'w')
while True:
    N+=1
    print('---')
    print(N, strftime('%Y-%m-%d %H:%M:%S'), time()-t00, sep='\t')
    fout.write('{0:d}\tRUN\t{1:f}\n'.format(N, time()))
    print('\t',ala.send_recv('04RUN'), time()-t0)
    while ((time()-t0) < time_on):
        sleep(timer_sleep)
    print('\t',ala.send_recv('04STP'), time()-t0)
    fout.write('{0:d}\tSTP\t{1:f}\n'.format(N, time()))
    fout.flush()
    while ((time()-t0) < time_period):
        sleep(timer_sleep)
    t0 += time_period
   
fout.close()
ala.close()

