# -*- coding: utf-8 -*-
"""
GUI for control of an Aladdin pump with the option to simultaneously
control a VICI EUHA motorized valve.

The GUI is implemented in with Remi, and may be remote via TCP/IP
"""

import sys
import re
from time import time, sleep
from datetime import datetime

import remi.gui as gui
import remi

from remi_extras import LineWriterBox

from devcomms.aladdin import Aladdin
from devcomms.aladdin import serial

from devcomms.vici_euha import VICI_EUHA

####
# configuration settings, to be externalised to a configuration file/module

# server IP address, port
IP_ADDRESS = '0.0.0.0' #localhost
IP_PORT = 9013 # make sure that every instance has its own port!!

# drop-down menu items and associated parameter strings
# They are either simple lists (when the menu items are the strings)
# or
# presented as dictionaries: the keys will be the drop-down menu items
# and the values will be the parameter strings to be sent to the functions
# that configure the pump

commports = ['COM3', 'COM4', 'COM5', 'COM6']

pumpIDs = ['01', '02']

syringetype_items = {'SGE100µl (1.456mm)': 'DIA1.456',
                     'SGE250µl (2.303mm)': 'DIA2.303',
                     'SGE500µl (3.257mm)': 'DIA3.257',
                     '2 ml plastic (9.537mm)': 'DIA9.537',
                     '5 ml plastic (12.62mm)': 'DIA12.62',
                     '10 ml plastic (15.96mm)': 'DIA15.96',         
                     '10 ml SETonic glass (14.60mm)': 'DIA14.60',
                     '20 ml plastic (20.10mm)': 'DIA20.10'}
syringetypes = list(syringetype_items.keys())

pumprates = ['0.5', '1.0', '2.0', '4.0', '10.0', '20.0', '50.0']

# healthy pauses during Aladdin communication/operations
ALADDIN_LONGSLEEP = 1.0
ALADDIN_SHORTSLEEP = 0.2

# UI update schedule - used in idle(self)
SCHEDULE_STEP = 1.0 # in seconds
EUHA_SCHEDULE_STEP = 1.0 # in seconds


# Default rest position for EUHA valve
EUHA_REST_POSITION = 'B'
# fill position
EUHA_FILL_POSITION = 'A'


# minimal injection duration for program automation mode 
PROG_INJEKT_MIN = 1.0
PROG_PRE_ROLL_S = 10. # number of seconds to first pre-fill
PROG_UI_TO_SECONDS = 60 # UI value is in minutes

####
# Utility functions

def isotimestr():
    return datetime.now().isoformat().split('.')[0]


def isostamp(tstamp):
    return datetime.fromtimestamp(tstamp).isoformat()

####


class AladdinPumpSteady(remi.App):
    def __init__(self, *args):
        self.pump_reply_parse_re = re.compile(r"I(\d+\.?\d*)W(\d+\.?\d*)(UL|ML)")

        self.aladdin = None # this corresponds to unactivated Aladdin connection
        self.activated = False # status of Aladdin communications
        self.next_sched = 0.0 # just to initialize (contains time of next scheduled aladdin idle loop event)

        self.euha = None # this corresponds to unactivated VICI EUHA connection
        self.euha_activated = False  # status of VICI EUHA communications
        self.euha_next_sched = 0.0
        
        self.program_running = False
        
        # set number of program cycles TODO: set this in UI!!!
        self.program_maxcycles = 5 # 0 = indefinitely
        
        super(AladdinPumpSteady, self).__init__(*args)


    def main(self):
        ### DEFINE GUI LAYOUT and WIDGETS
        
        
        global VICI_EUHA_MODE
        # use a global variable to indicate whether to activate 'DOUBLE' mode
        # (i.e. have room for VICI EUHA control)
        
        
        if not VICI_EUHA_MODE:
            containerw = 420
        else:
            containerw = 780
        
        cntr_main = gui.Container(width = containerw, height = 560)
        
        #DOUBLE
        doublebox = gui.HBox()
               
                
        if VICI_EUHA_MODE:
            vbox_main2 = gui.VBox()
            
            vbox_main2.append(gui.Label('VICI EUHA valve',margin='10px'))
            
            m2_vbox1 = gui.VBox(height=120, width=320,margin='10px')
            m2_vbox1.css_border_style='solid'
                       
            m2_hbox11 = gui.HBox()
            m2_hbox11.append(gui.Label('comm. port', 
                                    width=120))
            self.m2_dmenu11 = gui.DropDown.new_from_list(commports, width=120)
            m2_hbox11.append(self.m2_dmenu11)
            m2_vbox1.append(m2_hbox11)
            
            m2_hbox15 = gui.HBox()
            self.m2_button151 = gui.Button('activate',
                                  width=100, height=24, margin='10px')

            self.m2_button152 = gui.Button('deactivate',
                                  width=100, height=24, margin='10px')
            m2_hbox15.append([self.m2_button151,self.m2_button152])
            m2_vbox1.append(m2_hbox15)

            vbox_main2.append(m2_vbox1)
            
            

            m2_vbox2 = gui.VBox(height = 100, width= 320, margin='10px')
            m2_vbox2.css_border_style='solid'
            m2_hbox21 = gui.HBox()
            self.m2_button211 = gui.Button('pos. A',
                                        width=120, height=24, 
                                        margin='10px')
            m2_hbox21.append(self.m2_button211)
            self.m2_button212 = gui.Button('pos. B',
                                        width=120, height=24, 
                                        margin='10px')
            m2_hbox21.append(self.m2_button212)
            m2_vbox2.append(m2_hbox21)
            
            vbox_main2.append(m2_vbox2)
            
            
            
            self.m2_label4 = gui.Label('EUHA comms inactive', 
                                    width=320, height=20, margin='10px')
            self.m2_label4.css_border_style='solid'
            vbox_main2.append(self.m2_label4)
            
            
            
            
            m2_vbox3 = gui.VBox(height = 240, width= 320, margin='10px')
            m2_vbox3.css_border_style='solid'
            
            m2_hbox31 = gui.HBox()
            m2_hbox31.append(gui.Label('Period', 
                                    width=120))
            self.m2_spin31 = gui.SpinBox(20, 5, 120, 1,
                                 width=120)
            m2_hbox31.append(self.m2_spin31)
            m2_hbox31.append(gui.Label('min.'))
            m2_vbox3.append(m2_hbox31)
            
            m2_hbox32 = gui.HBox()
            m2_hbox32.append(gui.Label('Pre-fill', 
                                    width=120))
            self.m2_spin32 = gui.SpinBox(1, 1, 15, 1,
                                 width=120)
            m2_hbox32.append(self.m2_spin32)
            m2_hbox32.append(gui.Label('min.'))
            m2_vbox3.append(m2_hbox32)
            
            m2_hbox33 = gui.HBox()
            m2_hbox33.append(gui.Label('Fill', 
                                    width=120))
            self.m2_spin33 = gui.SpinBox(1, 1, 15, 1,
                                 width=120)
            m2_hbox33.append(self.m2_spin33)
            m2_hbox33.append(gui.Label('min.'))
            m2_vbox3.append(m2_hbox33)
            
            m2_hbox34 = gui.HBox()
            m2_hbox34.append(gui.Label('Post-fill', 
                                    width=120))
            self.m2_spin34 = gui.SpinBox(1, 1, 15, 1,
                                 width=120)
            m2_hbox34.append(self.m2_spin34)
            m2_hbox34.append(gui.Label('min.'))
            m2_vbox3.append(m2_hbox34)
            

            m2_hbox35 = gui.HBox()
            self.m2_button351 = gui.Button('Run program',
                                        width=120, height=24, 
                                        margin='10px')
            m2_hbox35.append(self.m2_button351)
            self.m2_button352 = gui.Button('End program',
                                        width=120, height=24, 
                                        margin='10px')
            m2_hbox35.append(self.m2_button352)
            m2_vbox3.append(m2_hbox35)
            vbox_main2.append(m2_vbox3)
            
            
            
            
            #DOUBLE
            doublebox.append(vbox_main2)
        
        
        
        
        vbox_main = gui.VBox()
        
        vbox_main.append(gui.Label('Aladdin syringe pump',margin='10px'))
        
        
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


        self.label4 = gui.Label('Aladdin pump comms inactive', 
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

        #DOUBLE
        doublebox.append(vbox_main)



        #DOUBLE
        #cntr_main.append(vbox_main)
        cntr_main.append(doublebox)
        

        ###########################
        # set default values (before event handlers active)
        # (Q: does the set_value method trigger event handler?)
        self.dmenu22.set_value(pumprates[0]) # this should be the lowest pump rate
        
        

        ################################
        # INITIALIZE VALUES, SET STATEs 
        self.deactivate()
        if VICI_EUHA_MODE:
            self.euha_deactivate()
        
        
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
        if VICI_EUHA_MODE:
            self.m2_button151.onclick.do(self.m2_activate151)
            self.m2_button152.onclick.do(self.m2_deactivate152)
            self.m2_button211.onclick.do(self.m2_euha_posA_211)
            self.m2_button212.onclick.do(self.m2_euha_posB_212)
            self.m2_spin31.onchange.do(self.m2_check_spin3x)
            self.m2_spin32.onchange.do(self.m2_check_spin3x)
            self.m2_spin33.onchange.do(self.m2_check_spin3x)
            self.m2_spin34.onchange.do(self.m2_check_spin3x)
            self.m2_button351.onclick.do(self.m2_runprog351)
            self.m2_button352.onclick.do(self.m2_stopprog352)
        
        
        return cntr_main



    ###################
    #### Event loop, idle activity

    def idle(self):
        global VICI_EUHA_MODE
        
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
                    self.linewriter.writeln('GLITCH: Aladdin comms lost')
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
                    
        if VICI_EUHA_MODE and self.euha_activated: # the VICI_EUHA_MODE is redundant, in principle
            t2 = time()
            if t2 > self.euha_next_sched:
                pos = self.euha.get_pos()
                self.m2_label4.set_text(isotimestr()+\
                                        ' - EUHA active. pos='+pos)
                if pos == 'A':
                    self.m2_button211.css_background_color = "rgb(0,200,0)"
                    self.m2_button212.css_background_color = ""
                elif pos == 'B':
                    self.m2_button211.css_background_color = ""
                    self.m2_button212.css_background_color = "rgb(0,200,0)"
                else:
                    self.m2_button211.css_background_color = ""
                    self.m2_button212.css_background_color = ""
                    
                # set time for next event
                while t2 > self.euha_next_sched: # fast forward if necessary, do not execute missed events, but keep rhythm!
                    self.euha_next_sched = self.euha_next_sched + SCHEDULE_STEP                
                

        if self.program_running:
            # fast event processing (program stages)
            t3 = time()
            if t3 > self.prog_Tnext:
                if self.prog_step==0:
                    self.prog_step=1
                    
                    self.linewriter.writeln('PROGRAM EVENT: start pre-fill')
                    self.aladdin.pump_cmd(self.pumpid, 'STP')
                    self.euha.set_pos(EUHA_FILL_POSITION)

                    self.prog_logfile.write(isostamp(t3)+'\t'+\
                                            'pre-fill'+'\n')
                    self.prog_Tnext = self.prog_Tnext + PROG_UI_TO_SECONDS*self.prog_prefill
                elif self.prog_step==1:
                    self.prog_step=2
                    
                    self.linewriter.writeln('PROGRAM EVENT: start fill')
                    # self.euha.set_pos(EUHA_FILL_POSITION)
                    self.aladdin.pump_cmd(self.pumpid, 'RUN')

                    self.prog_logfile.write(isostamp(t3)+'\t'+\
                                            'fill'+'\n')
                    self.prog_Tnext = self.prog_Tnext + PROG_UI_TO_SECONDS*self.prog_fill
                elif self.prog_step==2:
                    self.prog_step=3
                    
                    self.linewriter.writeln('PROGRAM EVENT: start post-fill')
                    # self.euha.set_pos(EUHA_FILL_POSITION)
                    self.aladdin.pump_cmd(self.pumpid, 'STP')
                    
                    self.prog_logfile.write(isostamp(t3)+'\t'+\
                                            'post-fill'+'\n')
                    self.prog_Tnext = self.prog_Tnext + PROG_UI_TO_SECONDS*self.prog_postfill
                elif self.prog_step==3:
                    self.prog_step=0
                    
                    self.linewriter.writeln('PROGRAM EVENT: *** INJEKT and return to initial state ***')
                    self.euha.set_pos(EUHA_REST_POSITION)
                    # self.aladdin.pump_cmd(self.pumpid, 'STP')
                    
                    self.prog_logfile.write(isostamp(t3)+'\t'+\
                                            'INJEKT'+'\n')
                    self.prog_logfile.flush() # Flush so that the injection event is directly written to disk    
                        
                    self.prog_Tnext = self.prog_Tnext +\
                        PROG_UI_TO_SECONDS*(self.prog_period-(self.prog_prefill+\
                            self.prog_fill+self.prog_postfill))
                    self.linewriter.writeln('next event (pre-fill): '+\
    datetime.fromtimestamp(self.prog_Tnext).isoformat().split('T')[1])
                        
                    # complete cycle
                    # max number of cycles
                    self.program_cycles += 1
                    if (self.program_maxcycles > 0)\
                           and (self.program_cycles >= self.program_maxcycles):
                        # end program
                        t4 = time()
                        self.prog_logfile.write(isostamp(t4)+'\t'+\
                                                'Number of cycles reached. Ending program.'+'\n')
                        # the following should work
                        self.m2_stopprog352(None)   
                    
                    
            
        


    
    ###################
    #### EVENT HANDLERS
    
    def activate151(self, widget):
        self.activate()
       
    def deactivate152(self, widget):
        #TODO dialogue: ARE YOU SURE?
        self.deactivate()
        self.linewriter.writeln('Aladdin pump comms deactivated')

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
        if VICI_EUHA_MODE:
            self.euha_deactivate()
        self.deactivate()
        sleep(ALADDIN_LONGSLEEP) 
        self.close()
        
    def m2_check_spin3x(self, widget, value):
        self.m2_getvalues_spin3x()
        total_preinjekt = self.prog_prefill+self.prog_fill+self.prog_postfill
        if (self.prog_period < PROG_INJEKT_MIN+total_preinjekt):
            self.prog_period = PROG_INJEKT_MIN+total_preinjekt
            self.m2_spin31.set_value(self.prog_period)
    
    def m2_getvalues_spin3x(self):
        self.prog_period = float(self.m2_spin31.get_value())
        self.prog_prefill = float(self.m2_spin32.get_value())
        self.prog_fill = float(self.m2_spin33.get_value())
        self.prog_postfill = float(self.m2_spin34.get_value())
        
        

    def m2_runprog351(self, widget):
        if self.program_running:
            # quick protection against multiple RUN PROGRAMS
            return
        if (self.aladdin is None) or (self.euha is None):
            self.linewriter.writeln('Activate both Aladdin and VICI EUHA...')
            return
        
        
        self.linewriter.writeln('RUN PROGRAM')
        
        self.aladdin.pump_cmd(self.pumpid, 'STP')
        self.euha.set_pos(EUHA_REST_POSITION)
        self.linewriter.writeln('pump stopped. valve in rest position')

        self.m2_getvalues_spin3x()
        
        t0 = time()
        # intialize log file
        logfname = 'program_log_'+\
   datetime.fromtimestamp(t0).strftime('%y%m%d_%H%M%S')+'.txt'
        self.prog_logfile = open(logfname, 'w')
        
        # Set UI button to active (Green)
        self.m2_button351.css_background_color = "rgb(0,200,0)"
        
        # max number of cycles
        self.program_cycles = 0
        ## self.program_maxcycles = 0 # TODO get from UI (for now defined in __init__)
        self.linewriter.writeln('number of cycles: {0:d} !!! '\
                                'TO DO make UI Spinbox to set value !!!'\
                                    .format(self.program_maxcycles))
        
        # initialize program
        self.prog_step = 0
        Tnext = t0+PROG_PRE_ROLL_S
        self.prog_Tnext = Tnext
        self.program_running = True
        
        self.linewriter.writeln('next event (pre-fill): '+\
            datetime.fromtimestamp(self.prog_Tnext).isoformat().split('T')[1])
        
       
    def m2_stopprog352(self, widget):
        if not self.program_running:
            # quick protection against multiple END PROGRAMS
            return
        self.program_running = False
        self.prog_logfile.close()
        self.linewriter.writeln('END PROGRAM')
        
        self.aladdin.pump_cmd(self.pumpid, 'STP')
        self.euha.set_pos(EUHA_REST_POSITION)
        self.linewriter.writeln('pump stopped. valve in rest position')
        
        # Set UI button to inactive (default colour)
        self.m2_button351.css_background_color = ""
    
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
        self.label4.set_text('Aladdin pump comms inactive')
        
        # set 'deactivated' state
        self.activated = False
        
        
    def activate(self):
        # enter transition between deactivate and activated state
        self.button151.css_background_color = "rgb(0,200,0)"
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
                try:
                    pump_status, pump_reply = self.aladdin.pump_cmd(self.pumpid, cmdstr)
                except AssertionError:
                    # during initialization, apparent comm errors can occur
                    # if trying to communicate with a connected device that is
                    # not an Aladdin pump!
                    # In that case, we conclude that we are not communicating
                    # with an Aladdin pump
                    print('Unexpected reply from connected device (not an Aladdin pump)')
                    pump_reply = None
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
            
    
            
    ###################
    ###################
    ###################            
    #### VICI EUHA functions
    
    ###################
    #### EUHA EVENT HANDLERS
    
    def m2_activate151(self, widget):
        self.linewriter.writeln(isotimestr()+' EUHA activate')
        self.euha_activate()

       
    def m2_deactivate152(self, widget):
        self.linewriter.writeln(isotimestr()+' EUHA deactivate')
        self.euha_deactivate()

    def m2_euha_posA_211(self, widget):
        self.linewriter.writeln(isotimestr()+' EUHA pos. A')
        self.euha_posA()

    def m2_euha_posB_212(self, widget):
        self.linewriter.writeln(isotimestr()+' EUHA pos. B')
        self.euha_posB()


            
    ####################
    #### EUHA DEEPER FUNCTIONS
    

    def euha_deactivate(self):
        if self.euha_activated:
            self.euha.set_pos(EUHA_REST_POSITION)
            assert self.euha.get_pos()=='B', 'Something very wrong with EUHA Valve... cannot move'

        # set 'deactivated' state
        self.euha_activated = False

        if self.euha is not None: # a COM port is active
            self.euha.close()
            sleep(ALADDIN_SHORTSLEEP) # give some time to close?
            self.euha = None # unbind object

        # put UI in 'deactivated' state
        #self.button152.css_background_color = "rgb(255,0,0)"
        self.m2_button151.css_background_color = ""
        self.m2_button151.set_enabled(True)
        self.m2_button152.set_enabled(False)
        self.m2_dmenu11.set_enabled(True)
        self.m2_button211.set_enabled(False)
        self.m2_button212.set_enabled(False)
        
        self.m2_button351.set_enabled(False)
        self.m2_button352.set_enabled(False)

        self.m2_label4.set_text('EUHA comms inactive')
        

        
        
    def euha_activate(self):
        # enter transition between deactivate and activated state
        self.m2_button151.css_background_color = "rgb(0,200,0)"
        self.m2_button152.css_background_color = ""
        self.m2_button151.set_enabled(False)
        self.m2_dmenu11.set_enabled(False)

        # get configuration from UI
        self.linewriter.writeln('***EUHA CONFIGURATION***')
        self.linewriter.writeln('comm port   :'+ self.m2_dmenu11.get_value())
        self.linewriter.writeln('*******************')


        
        # EUHA INITIALIZATION
        # get configuration from UI (for real)
        self.euha_port_str = self.m2_dmenu11.get_value()

        
        # 1. Open serial comms via Aladdin instance
        assert self.euha == None, 'EUHA connection already existing? (should not happen)'

        initialization_OK = False
      
        try:
            self.euha = VICI_EUHA(self.euha_port_str)
            initialization_OK = True
        except Exception as ex:
            self.linewriter.writeln('EUHA init error: '+str(ex))
            self.euha = None
            initialization_OK = False
        
        
        # 2. Initialization routine
        if initialization_OK:
            self.euha.set_pos(EUHA_REST_POSITION)
            assert self.euha.get_pos()=='B', 'Something very wrong with EUHA Valve... cannot move'
           

        # if OK then set pump control UI buttons color
        # if not OK then re-deactivate
        if not initialization_OK:
            self.euha_deactivate()
        else:
            # fully enter 'activated' state
            self.m2_button152.set_enabled(True)
            self.m2_button211.set_enabled(True)
            self.m2_button212.set_enabled(True)
                    
            self.m2_button351.set_enabled(True)
            self.m2_button352.set_enabled(True)
            
            self.euha_activated = True
            self.euha_next_sched = time() + EUHA_SCHEDULE_STEP
            self.linewriter.writeln('EUHA valve comms successfully activated!')
            self.linewriter.writeln('EUHA valve position: '+self.euha.get_pos())
            
    def euha_posA(self):
        self.euha.set_pos('A')
        
    def euha_posB(self):
        self.euha.set_pos('B')
        

    

if __name__ == "__main__":
    print('Hello.')
    
    
    
    if len(sys.argv) == 2:
        # change IP_PORT from default value
        IP_PORT = int(sys.argv[1])
    
    assert IP_PORT >= 8000, 'IP_PORT should be 8000 or beyond'
    
    
    # further decode IP_PORT 
    # and set configuration accordingly
    
    # TODO: each specific port number could correspond to a custom configuration
    # limiting choices for pumpID etc. such that no mix-ups occur
    
    if IP_PORT < 9500:
        VICI_EUHA_MODE = True
    else:
        VICI_EUHA_MODE = False
    

    
    
    
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
