#!/usr/bin/env python3
#
#   Tkpoint 0.1 - Python Tkinter Trackpoint Config Tool
#
#       nvz < enveezee@gmail.com >
#

rule_file="/etc/udev/rules.d/70-tkpoint.rules"

from os import listdir
from subprocess import PIPE, run
from tkinter import *

# The Tkpoint Application Class
class Tkpoint(Frame):

    # Initial setup of the class instance
    def __init__(self, master):

        # Boilerplate code
        super().__init__(master)
        self.master = master
        self.pack()

        # dict of available trackpoints names and paths        
        self.trackpoints = {}
      
        # Trackpoint settings
        self.settings = {
            # Descriptions taken from:
            # https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-devices-platform-trackpoint
#            "bind_mode" : {
#                'default':  'auto',
#                'desc':     '',
#                'type':     'str',
#                'values':   ['auto'] },
            "draghys" : {
                'default':  255,
                'desc':     'The drag hysteresis controls how hard it is to drag with z-axis pressed.',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "drift_time" : {
                'default':  1,
                'desc':     'This parameter controls the period of time to test for a hands off condition (i.e. when no force is applied) before a drift (noise) calibration occurs.',
                'max':      255,
                'res':      1,
                'type':     'scale' },
            "ext_dev" : {
                'default':  0,
                'desc':     'Disable (0) or enable (1) external pointing device',
                'res':	    1,
                'max':      1,
                'type':     'scale' },
            "inertia" : {
                'default':  5,
                'desc':     'Negative inertia factor. High values cause the cursor to snap backward when the trackpoint is released.',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "jenks" : {
                'default':  0,
                'desc':     'Minimum curvature in degrees required to generate a double click without a release.',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "mindrag" : {
                'default':  20,
                'desc':     '''Minimum amount of force needed to trigger dragging.''',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "press_to_select" : {
                'default':  0,
                'desc':     '',
                'res':  	1,
                'max':      1,
                'type':     'scale' },
            "rate" : {
                'default':  100,
                'desc':     '''''',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "reach" : {
                'default':  10,
                'desc':     '''''',
                'res':	    1,
                'max':      255,
                'type':     'scale' },
            "resetafter" : {
                'default':  5,
                'desc':     '''''',
   		        'res':	    1,
                'max':      255,
                'type':     'scale' },
            "resolution" : {
                'default':  200,
                'desc':     '''''',
   		        'res':	    1,
                'max':      255,
                'type':     'scale' },
            "resync_time" : {
                'default':  0,
                'desc':     '''''',
           		'res':	    1,
                'max':      255,
                'type':     'scale' },
            "sensitivity" : {
                'default':  128,
                'desc':     '''''',
   		        'res':	    1,
                'max':      255,
                'type':     'scale' },
            "skipback" : {
                'default':  0,
                'desc':     '''''',
   		        'res':	    1,
                'max':      255,
                'type':     'scale' },
            "speed" : {
                'default':  100,
                'desc':     '''''',
       	    	'res':	    1,
                'max':      255,
                'type':     'scale' },
            "thresh" : {
                'default':  8,
                'desc':     '''''',
       	    	'res':	    1,
                'max':      255,
                'type':     'scale' },
            "upthresh" : {
                'default':  255,
                'desc':     '''''',
       	    	'res':	    1,
                'max':      255,
                'type':     'scale' },
            "ztime" : {
                'default':  32,
                'desc':     '''''',
                'res':	    1,
                'max':      32,
                'type':     'scale' }
        }

        self.detect()
        self.create_widgets()

    # Handle callbacks on events
    def callback(self, event):
        
        # Widget's name
        widget = str(event.widget).split('.')[-1]

        # If trackpoint listbox was clicked
        if widget == "trackpoints":
            self.path = self.trackpoints[self.devices.get('active')] + 'device/device/'
            # Load trackpoint
            self.load()
        # If a settings widget was clicked
        elif widget in self.settings:
            # Set the setting to the widget's value
            self.set(widget,event.widget.get())

    # Create the GUI widgets for the trackpoint settings
    def create_widgets(self):

        # Create a listbox for the trackpoints
        self.devices = Listbox(self, name='trackpoints', selectmode=SINGLE)
        self.devices.grid(row=0)

        # Iterate over each trackpoint
        for trackpoint in self.trackpoints:

            # Insert name into the listbox
            self.devices.insert(END, trackpoint)
                
            # Bind event to listbox
            self.devices.bind('<ButtonRelease-1>', self.callback)

        self.path = self.trackpoints[trackpoint]+'device/device/'

        # Initialize grid counters
        r = 1

        # Iterate over each setting in the settings dict
        for setting in self.settings:

            # Settings for the widget
            widget = self.settings[setting]

            # Create text label for the setting widget
            Label(self, text=setting).grid(row=r)
             
            # Handle specifics for different widget types
            if widget['type'] == 'scale':
                res = widget['res']
                top = widget['max']
                widget['widget'] = Scale(self, from_=0, to=top, orient=HORIZONTAL, resolution=res, name=setting)

            # Pack the widget into the GUI
            widget['widget'].grid(row=r, column=1)

            # Register a event handler and callback function for the widget
            widget['widget'].bind('<ButtonRelease-1>', self.callback)

            # Increment grid counter
            r+=1

        self.load()

    # Detect trackpoint devices, return a list
    def detect(self):

        # Get a list of /dev/input/mouse* devices
        mice = []
        for dev in listdir('/dev/input/'):
            if dev[0:5] == 'mouse':
                mice.append('/dev/input/' + dev)

        # Get udev information for all mice
        if mice:
            udevinfo = []
            for mouse in mice:
                r = run(['udevadm','info',mouse], stdout=PIPE)
                udevinfo.append(r.stdout.decode('utf-8').split('\n'))                 
        else:
            error('No pointing devices detected.')

        # Detect trackpoints and their sysfs path
        for info in udevinfo:
            for line in info:
                if line[0:2] == 'P:':
                    path = '/sys' + line[3:] + '/'
                elif line == 'E: ID_INPUT_POINTINGSTICK=1':
                    with open(path + 'device/name', 'r') as f:
                        name = f.read()
                        self.trackpoints[name] = path

        if not self.trackpoints:
            error('No trackpoint devices detected.')

    # Get current value of a trackpoint setting            
    def get(self, key):
        with open(self.path + key, 'r') as f:
            return f.read().split('\n')[0]

    # Load current settings for a trackpoint
    def load(self):

        # Iterate over settings
        for setting in self.settings:

            # Read setting value from sysfs
            val = self.get(setting)

            # Set value on widget
            if self.settings[setting]['type'] == 'scale':
                self.settings[setting]['widget'].set(int(val))        

    # Save trackpoint settings to a udev rule
    def save(self):
        pass

    # Set value of a trackpoint setting
    def set(self, key, val):
        with open(self.path + key,'w') as f:
            f.write(str(val))

def error(msg):
    print(msg)
    exit(1)

# Instantiate the application class
trackpoint = Tkpoint(master=Tk())

# Trigger the main application loop
trackpoint.mainloop()
