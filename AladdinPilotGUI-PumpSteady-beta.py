# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 22:43:40 2023

@author: Martinus Werts
"""

from time import time,sleep

import remi.gui as gui
import remi

from remi_extras import LineWriterBox

####
# configuration settings, to be externalized

# server IP address, port
IP_ADDRESS = '0.0.0.0' #localhost
IP_PORT = 8082 # make sure that every script has its own port!!

# drop-down menu items and associated parameter strings
# They are either simple lists (when the menu items are the strings)
# or
# presented as dictionaries: the keys will be the drop-down menu items
# and the values will be the parameter strings to be sent to the functions
# that configure the pump

commports = ['COM2', 'COM3', 'COM4']

pumpIDs = ['01', '02', '03', '04']

syringetype_items = {'1mL (/ 5.333mm)': 'AladdinString1',
                     '5mL (/ 10.26mm)': 'AladdinString2',
                     '10mL (/ 15.22mm)': 'AladdinString3',
                     '20mL (/ 26.66mm)': 'AladdinString4'}
syringetypes = list(syringetype_items.keys())

pumprates = ['0.5', '1.0', '2.0', '5.0', '10.0', '20.0', '50.0']

# UI update schedule
SCHEDULE_STEP = 1.0


####




class AladdinPumpSteady(remi.App):
    def __init__(self, *args):
        self.activated = False
        super(AladdinPumpSteady, self).__init__(*args)

    def idle(self):
        # HERE: monitor pump status if comms activated
        # every second (schedule_next = schedule_next + 1)
        #          while time > schedule_next:
        #               schedule_next = schedule_next + schedule_step
        # update buttons color to reflect status
        #   do not grey out buttons
        if self.activated:
            t1 = time()
            if t1 > self.next_sched:
                # TODO get pump state (send-receive)

                # TODO: blink buttons according to pump state
                # print(self.button211.css_background_color)
                # For now, toggle button color (to get the idea)
                if self.button211.css_background_color == '':
                    self.button211.css_background_color = "rgb(0,200,0)"
                else:
                    self.button211.css_background_color = ''
                while t1 > self.next_sched: # fast forward if necessary, do not execute missed events, but keep rhythm!
                    self.next_sched = self.next_sched + SCHEDULE_STEP
            

    def main(self):
        
        ### DEFINE GUI LAYOUT and WIDGETS
        cntr_main = gui.Container(width = 320, height = 480)
        
        vbox_main = gui.VBox()
        
        
        vbox1 = gui.VBox(height=120, width=300,margin='10px')
        vbox1.css_border_style='solid'
        hbox11 = gui.HBox()
        hbox11.append(gui.Label('comm. port', 
                                width=100))
        self.dmenu11 = gui.DropDown.new_from_list(commports, width=100)
        hbox11.append(self.dmenu11)
        hbox12 = gui.HBox()
        hbox12.append(gui.Label('pump ID', 
                                width=100))
        self.dmenu12 = gui.DropDown.new_from_list(pumpIDs,
                                             width=100)
        hbox12.append(self.dmenu12)
        hbox13 = gui.HBox()
        hbox13.append(gui.Label('syringe type', 
                                width=100))
        self.dmenu13 = gui.DropDown.new_from_list(syringetypes,
                                             width=140)
        hbox13.append(self.dmenu13)
        hbox14 = gui.HBox()
        hbox14.append(gui.Label('fill volume', 
                                width=100))
        self.spin14 = gui.SpinBox(0.5, 0.1, 10.0, 0.1,
                             width=100)
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


        vbox2 = gui.VBox(height = 100, width= 300, margin='10px')
        vbox2.css_border_style='solid'
        hbox21 = gui.HBox()
        self.button211 = gui.Button('injekt',
                                    width=120, height=24, margin='10px')
        hbox21.append(self.button211)
        self.button212 = gui.Button('pause',
                                    width=120, height=24, margin='10px')
        hbox21.append(self.button212)
        vbox2.append(hbox21)        
        hbox22 = gui.HBox()
        hbox22.append(gui.Label('pump rate', 
                                width=80))
        self.dmenu22 = gui.DropDown.new_from_list(pumprates,
                                     width=80)
        hbox22.append(self.dmenu22)
        hbox22.append(gui.Label('ulmin-1', 
                                width=50))    
        vbox2.append(hbox22)
        vbox_main.append(vbox2)


        vbox3 = gui.VBox(height = 140, width= 300, margin='10px')
        vbox3.css_border_style='solid'
        self.linewriter = LineWriterBox(height=120,width=280,
                                        maxlines=50,
                                        reverse_out=True,
                            initlines=['New lines are added on top.',
                                       'read this from bottom to top',
                                       'if you want chronological order',
                                       'New lines are added on top.'])
        vbox3.append(self.linewriter)
        vbox_main.append(vbox3)

        
        vbox4 = gui.VBox(height=40, width=300)
        self.button41 = gui.Button('terminate app',
                                   width=100, height=24, margin='10px')

        vbox4.append(self.button41)
        vbox_main.append(vbox4)
    
        cntr_main.append(vbox_main)

        ################################
        # INITIALIZE VALUES, SET STATEs 
        self.deactivate()
        
        
        #################################
        # SET EVENT HANDLERS
        #TODO put all event handler initializations here, to be executed
        # only when all widgets have been created
        self.button151.onclick.do(self.activate151)
        self.button152.onclick.do(self.deactivate152)
        self.button211.onclick.do(self.injekt211)
        self.button212.onclick.do(self.pause212)
        self.dmenu22.onchange.do(self.pumprate22)
        self.button41.onclick.do(self.close41)
        return cntr_main


    
    ###################
    #### EVENT HANDLERS
    
    def activate151(self, widget):
        self.activate()

        
       
    def deactivate152(self, widget):
        #TODO dialogue: ARE YOU SURE?
        
        self.deactivate()
        
        #TODO: remove below
        self.linewriter.writeln('deactivate152')

        

    def injekt211(self, widget):
        #TODO send START command to pump
        
        #TODO set pump rate? 
        self.linewriter.writeln('injekt211')



    def pause212(self, widget):
        #TODO send PAUSE command to pump

        self.linewriter.writeln('pause212')
        self.linewriter.writeln('sleep test... scheduler??')
        sleep(3)
        #IT WOULD BE GOOD TO NOT HAVE A CLICK EVENT BUFFER => if clicked when busy, do nothing!
        
        
        
    def pumprate22(self, widget, value):
        #TODO decode and send RATE command to pump
        # or schedule new pump rate for next good occasion?? (is rate change possible without stopping?)
        
        self.linewriter.writeln('new pump rate: '+value)



        
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
        #TODO: dramatically wait a few seconds to let the system rest?    
        self.close()

    
    ####################
    #### DEEPER FUNCTIONS
    

    def deactivate(self):
        if self.activated:
            pass
            # stop everything (if activated)
            # free COM port (destroy object?)

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
        self.linewriter.writeln('        ALADDIN='+
                                syringetype_items[self.dmenu13.get_value()])
        self.linewriter.writeln('fill volume :'+ self.spin14.get_value()) # this is also a string, to be converted
        self.linewriter.writeln('*******************')

        initialization_OK = True
        #TODO call pump initialization
        #  create pump object?
        # make sure pump is in stopped state
        #IF ERROR THEN deactivate
        # if OK then set pump control UI buttons color
        
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
        
        

    

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    print('running on {0:s}:{1:d}'.format(IP_ADDRESS, IP_PORT))
    print('you should open your browser yourself')
    remi.start(AladdinPumpSteady, debug=True, # debug set to false
               address=IP_ADDRESS, port=IP_PORT,
               start_browser=False, 
               multiple_instance=False) # multiple_instance set to false
