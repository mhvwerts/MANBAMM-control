# -*- coding: utf-8 -*-
"""
This script is precursor to the "plus" version, and is now obsolete.
It does not include the optional VICI EUHA valve control mode of the
"plus" version
"""

import sys
import re
from time import time, sleep

import remi.gui as gui
import remi

from remi_extras import LineWriterBox

from aladdin import Aladdin
from aladdin import serial

####
# configuration settings, to be externalised to a configuration file/module

# server IP address, port
IP_ADDRESS = '0.0.0.0' #localhost
IP_PORT = 9000 # make sure that every script has its own port!!

# drop-down menu items and associated parameter strings
# They are either simple lists (when the menu items are the strings)
# or
# presented as dictionaries: the keys will be the drop-down menu items
# and the values will be the parameter strings to be sent to the functions
# that configure the pump

commports = ['COM7', 'COM8', 'COM9', 'COM10']

pumpIDs = ['01', '02', '03', '04']

syringetype_items = {'SGE100µl (1.456mm)': 'DIA1.456',
                     'SGE250µl (2.303mm)': 'DIA2.303',
                     'SGE500µl (3.257mm)': 'DIA3.257',
                     '2 ml (9.537mm)': 'DIA9.537',
                     '5 ml (12.62mm)': 'DIA12.62',
                     '20 ml (20.10mm)': 'DIA20.10'}
syringetypes = list(syringetype_items.keys())

pumprates = ['0.5', '1.0', '2.0', '5.0', '10.0', '20.0', '50.0']

# healthy pauses during Aladdin communication/operations
ALADDIN_LONGSLEEP = 1.0
ALADDIN_SHORTSLEEP = 0.2

# UI update schedule
SCHEDULE_STEP = 1.0


####



class AladdinPumpSteady(remi.App):
    def __init__(self, *args):
        self.pump_reply_parse_re = re.compile(r"I(\d+\.?\d*)W(\d+\.?\d*)(UL|ML)")
        self.aladdin = None # this corresponds to unconnected Aladdin pump
        self.activated = False
        super(AladdinPumpSteady, self).__init__(*args)

    def main(self):
        ### DEFINE GUI LAYOUT and WIDGETS
        cntr_main = gui.Container(width = 420, height = 560)
        
        vbox_main = gui.VBox()
        
        
        vbox1 = gui.VBox(height=140, width=400,margin='10px')
        vbox1.css_border_style='solid'
        hbox11 = gui.HBox()
        hbox11.append(gui.Label('comm. port', 
                                width=120))
        self.dmenu11 = gui.DropDown.new_from_list(commports, width=120)
        hbox11.append(self.dmenu11)
        hbox12 = gui.HBox()
        hbox12.append(gui.Label('pump ID', 
                                width=120))
        self.dmenu12 = gui.DropDown.new_from_list(pumpIDs,
                                             width=120)
        hbox12.append(self.dmenu12)
        hbox13 = gui.HBox()
        hbox13.append(gui.Label('syringe type', 
                                width=100))
        self.dmenu13 = gui.DropDown.new_from_list(syringetypes,
                                             width=160)
        hbox13.append(self.dmenu13)
        hbox14 = gui.HBox()
        hbox14.append(gui.Label('fill volume', 
                                width=120))
        self.spin14 = gui.SpinBox(0.5, 0.1, 15.0, 0.1,
                             width=120)
        hbox14.append(self.spin14)
        hbox14.append(gui.Label('ml'))
        hbox15 = gui.HBox()
        self.button151 = gui.Button('activate',
                              width=100, height=24, margin='10px')

        self.button152 = gui.Button('deactivate',
                              width=100, height=24, margin='10px')
        hbox15.append([self.button151,self.button152])
        
        vbox1.append([hbox11, hbox12, hbox13, hbox14, hbox15])
        vbox_main.append(vbox1)


        vbox2 = gui.VBox(height = 120, width= 400, margin='10px')
        vbox2.css_border_style='solid'
        hbox21 = gui.HBox()
        self.button211 = gui.Button('pump',
                                    width=120, height=24, margin='10px')
        hbox21.append(self.button211)
        self.button212 = gui.Button('stop',
                                    width=120, height=24, margin='10px')
        hbox21.append(self.button212)
        vbox2.append(hbox21)
        
        

   
        hbox22 = gui.HBox()
        hbox22.append(gui.Label('pump rate', 
                                width=80))
        self.dmenu22 = gui.DropDown.new_from_list(pumprates,
                                     width=80)
        hbox22.append(self.dmenu22)
        hbox22.append(gui.Label('µl/min', 
                                width=60))    
        vbox2.append(hbox22)
        vbox_main.append(vbox2)


        self.label4 = gui.Label('Pump comms inactive', 
                                width=360, height=20, margin='10px')
        self.label4.css_border_style='solid'
        vbox_main.append(self.label4)



        vbox3 = gui.VBox(height = 160, width= 400, margin='10px')
        vbox3.css_border_style='solid'
        self.linewriter = LineWriterBox(height=140,width=360,
                                        maxlines=80,
                                        reverse_out=True,
                            initlines=['New lines are added on top.',
                                       'read this from bottom to top',
                                       'if you want chronological order',
                                       'New lines are added on top.'])
        vbox3.append(self.linewriter)
        vbox_main.append(vbox3)

        
        vbox4 = gui.VBox(height=60, width=400)
        self.button41 = gui.Button('terminate app',
                                   width=100, height=24, margin='10px')

        vbox4.append(self.button41)
        vbox_main.append(vbox4)
    
        cntr_main.append(vbox_main)

        ###########################
        # set default values (before event handlers active)
        # (Q: does the set_value method trigger event handler?)
        self.dmenu22.set_value(pumprates[0]) # this should be the lowest pump rate
        
        

        ################################
        # INITIALIZE VALUES, SET STATEs 
        self.deactivate()
        
        
        #################################
        # SET EVENT HANDLERS
        # put all event handler initializations here, 
        # to be executed
        # only when all widgets have been created
        self.button151.onclick.do(self.activate151)
        self.button152.onclick.do(self.deactivate152)
        self.button211.onclick.do(self.start211)
        self.button212.onclick.do(self.stop212)
        self.dmenu22.onchange.do(self.pumprate22)
        self.button41.onclick.do(self.close41)
        return cntr_main



    ###################
    #### Event loop, idle activity

    def idle(self):
        # HERE: monitor pump status when pump activated
        # every SCHEDULE_STEP seconds
        # update buttons color to reflect status
        # check dispensed volume
        if self.activated:
            t1 = time()
            if t1 > self.next_sched:
                # get pump state 
                pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, 'DIS')
                if pump_reply is None:
                    self.linewriter.writeln('GLITCH: pump comms lost')
                    pump_status = '?'
                else:
                    # self.linewriter.writeln('status='+pump_status +
                    #                       '    reply='+pump_reply)
                    self.label4.set_text('pump status: '+pump_status +
                                            '     ---- volumes: '+pump_reply)
                    # change UI buttons state to reflect pump state
                    if pump_status == 'W': # withdraw! => ERROR
                        self.linewriter.writeln('ERROR: Withdraw activity detected. Stopping.')
                        self.aladdin.pump_cmd(self.pumpid, 'STP')
                    elif pump_status == 'I':
                        self.button211.css_background_color = "rgb(0,200,0)"
                        self.button212.css_background_color = ""
                        self.dmenu22.set_enabled(False) # cannot change RATE when pumping
                    elif pump_status == 'P' or pump_status == 'S':
                        self.button211.css_background_color = ""
                        self.button212.css_background_color = "rgb(220,0,0)"
                        self.dmenu22.set_enabled(True) # OK to change RATE
                    else:
                        self.button211.css_background_color = ""
                        self.button212.css_background_color = ""
                        
                    # Check if total injected volume exceeds the initial fill volume
                    # of the syringe.
                    # Instead of relying entirely on the 'VOL' setting in the pump
                    # controller (which stops the pump automatically), we explicitly
                    # check here the injected volume. This is much safer, since
                    # the 'VOL' dispense volume seems to be reset upon stopping
                    # and restarting the pump, while the overall injected volume
                    # reported by the pump is true to how much volume was injected
                    # overal.
                    # (1) decode pump_reply (using precompiled regex, which
                    #      decomposes the useful information into groups)
                    #      TODO: include this directly in aladdin.py
                    prparse = self.pump_reply_parse_re.search(pump_reply)
                    if prparse:
                        injvol = float(prparse.group(1))
                        # wdvol = float(prparse.group(2))
                        units = prparse.group(3)
                        if units==self.vol_units:
                            if injvol >= self.volvalue:
                                # END PUMPING!!
                                self.linewriter.writeln('COMPLETE: syringe fill volume dispensed. deactivating.')
                                self.linewriter.writeln('Change syringe.')
                                self.deactivate()
                            else:
                                pass
                                # business as usual (TODO: we could update display of injected volume
                        else:
                            self.linewriter.writeln('WARNING: pump VOL units do no match.')
                    else:
                        self.linewriter.writeln('WARNING: could not decode pump reply.')


                # set time for next event
                while t1 > self.next_sched: # fast forward if necessary, do not execute missed events, but keep rhythm!
                    self.next_sched = self.next_sched + SCHEDULE_STEP
            


    
    ###################
    #### EVENT HANDLERS
    
    def activate151(self, widget):
        self.activate()
       
    def deactivate152(self, widget):
        #TODO dialogue: ARE YOU SURE?
        self.deactivate()
        self.linewriter.writeln('Pump comms deactivated')

    def start211(self, widget):
        self.linewriter.writeln('Start pump command')
        self.dmenu22.set_enabled(False) # cannot change RATE when pumping
        self.start_pump()


    def stop212(self, widget):
        self.linewriter.writeln('Stop command')
        self.stop_pump()
        self.dmenu22.set_enabled(True) # OK to change RATE
        
    def pumprate22(self, widget, value):
        self.pumpratestr = value
        self.linewriter.writeln('new pump rate: '+self.pumpratestr)
        self.updatepumprate()
        
    def close41(self, widget):
        closedialog = gui.GenericDialog('Please confirm',
                                        "The app will be terminated. Click 'OK', then close your browser tab.")
        closedialog.confirm_dialog.do(self.onclosedialog41_confirm)
        closedialog.show(self)
        
    def onclosedialog41_confirm(self, _):
        print('Application is being terminated')
        #stop pump deactivate comms
        # enter deactivated state
        self.deactivate()
        sleep(ALADDIN_LONGSLEEP) 
        self.close()

    
    ####################
    #### DEEPER FUNCTIONS
    

    def deactivate(self):
        if self.activated:
             self.aladdin.pump_cmd(self.pumpid, 'STP') # stop pump 
        if self.aladdin is not None: # a COM port is active
            # stop everything (if activated)
            # free COM port (destroy object?)
            #TODO: UI should react immediately?
            #    current the UI is only update after this handler exits.
            #  
            #   this will require re-programming =>
            #    put all real pump action in the 'idle' via a message queue
            self.aladdin.close()
            sleep(ALADDIN_SHORTSLEEP) # give some time to close?
            self.aladdin = None # unbind object

        # put UI in 'deactivated' state
        #self.button152.css_background_color = "rgb(255,0,0)"
        self.button151.css_background_color = ""
        self.button151.set_enabled(True)
        self.button152.set_enabled(False)
        self.dmenu11.set_enabled(True)
        self.dmenu12.set_enabled(True)
        self.dmenu13.set_enabled(True)
        self.spin14.set_enabled(True)
        self.button211.set_enabled(False)
        self.button212.set_enabled(False)
        self.dmenu22.set_enabled(False)
        
        #
        self.label4.set_text('Pump comms inactive')
        
        # set 'deactivated' state
        self.activated = False
        
        
    def activate(self):
        # enter transition between deactivate and activated state
        self.button151.css_background_color = "rgb(10,128,10)"
        self.button152.css_background_color = ""
        self.button151.set_enabled(False)
        self.dmenu11.set_enabled(False)
        self.dmenu12.set_enabled(False)
        self.dmenu13.set_enabled(False)
        self.spin14.set_enabled(False)
        
        # get configuration from UI
        self.linewriter.writeln('***CONFIGURATION***')
        self.linewriter.writeln('comm port   :'+ self.dmenu11.get_value())
        self.linewriter.writeln('pump ID     :'+ self.dmenu12.get_value())
        self.linewriter.writeln('syringe     :'+ self.dmenu13.get_value())
        #self.linewriter.writeln('        ALADDIN='+
        #                         syringetype_items[self.dmenu13.get_value()])
        self.linewriter.writeln('fill volume :'+ self.spin14.get_value()) # this is also a string, to be converted
        self.linewriter.writeln('*******************')

        initialization_OK = False
        
        # PUMP INITIALIZATION
        # get configuration from UI (for real)
        self.port_str = self.dmenu11.get_value()
        self.pumpid = self.dmenu12.get_value()
        self.syringetype = self.dmenu13.get_value()
        aladdin_syringe_cmd = syringetype_items[self.syringetype]
        self.pumpratestr = self.dmenu22.get_value()
        
        # 1. Open serial comms via Aladdin instance
        assert self.aladdin == None, 'aladdin connection already existing? (should not happen)'

        try:
            self.aladdin = Aladdin(self.port_str)
            self.linewriter.writeln('SUCCESS: serial comms port initialized.')
            initialization_OK = True
        except serial.serialutil.SerialException:
            self.linewriter.writeln('ERROR: Could not initialize serial comms port.')
            initialization_OK = False
            
        # 2. Initialization routine
        # currently this is the basic sequence from aladdin-pilot2-dev3
        if initialization_OK:
            #TODO set initialization_OK to false if error
            for cmdstr in [
                    # step 1: prepare stopped pump
                    'VER','VER','STP', # make sure pump communicating and stopped (todo check expected responses)
                    
                    # step 2: check preferences!
                    'PF',#todo if not OK, set value (THIS SHOULD BE 0, the pump should stop after power disruption)
                    
                    # step 2: reset program
                    # overwrite current program with standard 'unprogrammed' operation
                    # I do not know how to delete steps from program via RS232
                    'PHN2','FUNSTP', # second phase stop pump 'end program?)
                    'PHN1','FUNRAT','VOL0.0', # first phase: infinite injection
                    
                    # step 3: with the standard program in place, we can use pump as normal
                    aladdin_syringe_cmd, # select syringe diameter - this control units for VOL
                    'RAT'+self.pumpratestr+'UM', # rate
                    'DIRINF', # inject
                    'CLDINF', # clear dispensed volume (inject)
                    ]:
                #self.linewriter.writeln('===============')
                self.linewriter.writeln('cmdstr = '+ cmdstr)
                pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, cmdstr)
                if pump_reply is None:
                    self.linewriter.writeln('ERROR: Pump not responding (check port & pumpID)')
                    initialization_OK = False
                    break
                else:
                    self.linewriter.writeln('    reply = '+ pump_reply+  
                                            '    status = '+pump_status)
                    #self.linewriter.writeln('================')

        # if still OK then get VOL units 
        if initialization_OK:
            cmdstr = 'DIS'
            self.linewriter.writeln('cmdstr = '+ cmdstr)
            pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, cmdstr)
            if pump_reply is None:
                self.linewriter.writeln('ERROR: Pump not responding (check port & pumpID)')
                initialization_OK = False
            else:
                self.linewriter.writeln('    reply = '+ pump_reply+  
                                        '    status = '+pump_status)
                self.vol_units = pump_reply[-2:]
                if self.vol_units not in ['UL','ML']:
                    self.linewriter.writeln('ERROR: unrecognized volume (VOL) units')
                    initialization_OK = False
       
        # if still OK then set VOL
        if initialization_OK:
            # UI is always in ML, apply conversion to UL for pump if necessary
            #  vol_units are the pump volume units
            #  volvalue has the same units as pump units
            unitconv = 1000 if self.vol_units=='UL' else 1
            self.volvalue = float(self.spin14.get_value()) * unitconv
            # self.linewriter.writeln('volvalue = {0:.2f} {1:s}'\
            #                         .format(self.volvalue, self.vol_units))
            cmdstr = 'VOL{0:.2f}'.format(self.volvalue)
            if len(cmdstr)>8:
                cmdstr = cmdstr[0:8]
                if cmdstr[7]=='.':
                    cmdstr = cmdstr[0:7]
            self.linewriter.writeln('cmdstr = '+ cmdstr)
            pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, cmdstr)
            if pump_reply is None:
                self.linewriter.writeln('ERROR: Pump not responding (check port & pumpID)')
                initialization_OK = False
            else:
                #TODO!!!! check if no pump error code
                # setting an illegal volume returns a pump error!!
                self.linewriter.writeln('    reply = '+ pump_reply+  
                                        '    status = '+pump_status)
    

        # if OK then set pump control UI buttons color
        # if not OK then re-deactivate
        if not initialization_OK:
            self.deactivate()
        else:
            # fully enter 'activated' state
            self.button152.set_enabled(True)
            self.button211.set_enabled(True)
            self.button212.set_enabled(True)
            self.dmenu22.set_enabled(True)
            self.next_sched = time() + SCHEDULE_STEP
            self.activated = True


    def start_pump(self):
        pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, 'RUN')
        # no checks yet, just send command
        # if successful, the status should update itself (see idle)
        
    def stop_pump(self):
        pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, 'STP')
        # no checks yet, just send command
        # if successful, the status should update itself (see idle)
        
    def updatepumprate(self):
        cmdstr = 'RAT'+self.pumpratestr+'UM'
        pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, cmdstr)
        # no checks yet, just send command and print return
        # WARNING for best performance, we should check and set pump rate
        # menu to the value reported back by the pump
        # The pump rate can not be changed when pumping
        self.linewriter.writeln('cmdstr = '+ cmdstr)
        if pump_reply is None:
            self.linewriter.writeln('ERROR: Pump not responding (check port & pumpID)')
        else:
            self.linewriter.writeln('    reply = '+ pump_reply+  
                                    '    status = '+pump_status)
            #self.linewriter.writeln('================')
        
        

    

if __name__ == "__main__":
    print('Hello.')
    
    if len(sys.argv) == 2:
        # change IP_PORT from default value
        IP_PORT = int(sys.argv[1])
    
    assert IP_PORT >= 8000, 'IP_PORT should be 8000 or beyond'
    
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    print('running on {0:s}:{1:d}'.format(IP_ADDRESS, IP_PORT))
    # print('you should open your browser yourself')
    remi.start(AladdinPumpSteady,
               title='AladdinPilot {0:d}'.format(IP_PORT), 
               debug=False, # debug set to false
               address=IP_ADDRESS, port=IP_PORT,
               start_browser=True, 
               multiple_instance=False) # multiple_instance set to false
