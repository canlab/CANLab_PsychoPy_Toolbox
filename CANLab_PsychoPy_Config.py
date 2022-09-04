#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CANLab PsychoPy Configuration File
Michael Sun, Ph.D.



"""

"""
1. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB'] # Set a preferred audio library to PsychToolBox (best), so psychopy doesn't yell at you.
from psychopy import sound, gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy.hardware import keyboard

from builtins import str
from builtins import range

import pandas as pd
import collections
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict=dict

import random
from datetime import datetime

"""
2. Global Variable Configurations
"""

debug = 1
autorespond = 1
# Device togglers
biopac_exists = 0
thermode_exists = 0

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
s_text='[s]-press confirmed.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 
fmriStart=None # Set to None until confirmRunStart() is called.

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

"""
3. Autoresponse objects for when autorespond=1
"""
class simKeys:
    '''
    an object to simulate key presses    
    keyList: a list of keys/ to watch
    name: randomly selected from keyList
    rtRange: [min RT, max RT] where min and max RT are sepecified in ms
        
    '''
    def __init__(self, keyList, rtRange):
        self.name=np.random.choice(keyList)
        self.rt = np.random.choice(np.linspace(rtRange[0], rtRange[1])/1000)

# pick an RT
thisRT=randint(0,5)
thisSimKey=simKeys(keyList=['space'], 
    rtRange=[200,1000])

"""
4. Configure Devices
"""
if biopac_exists == 1:
    # Initialize LabJack U3 Device, which is connected to the Biopac MP150 psychophysiological amplifier data acquisition device
    # This involves importing the labjack U3 Parallelport to USB library
    # U3 Troubleshooting:
    # Check to see if u3 was imported correctly with: help('u3')
    # Check to see if u3 is calibrated correctly with: cal_data = biopac.getCalibrationData()
    # Check to see the data at the FIO, EIO, and CIO ports: biopac.getFeedback(u3.PortStateWrite(State = [0, 0, 0]))
    try:
        from psychopy.hardware.labjacks import U3
        # from labjack import u3
    except ImportError:
        import u3
    # Function defining setData to use the FIOports (address 6000)
    def biopacSetData(self, byte, endian='big', address=6000): 
        if endian=='big':
            byteStr = '{0:08b}'.format(byte)[-1::-1]
        else:
            byteStr = '{0:08b}'.format(byte)
        [self.writeRegister(address+pin, int(entry)) for (pin, entry) in enumerate(byteStr)]
    biopac = U3()
    biopac.setData = biopacSetData
    # Set all FIO bits to digital output and set to low (i.e. “0")
    # The list in square brackets represent what’s desired for the FIO, EIO, CIO ports. We will only change the FIO port's state.
    biopac.configIO(FIOAnalog=0, EIOAnalog=0)
    for FIONUM in range(8):
        biopac.setFIOState(fioNum = FIONUM, state=0)
    # Set all channels to 0 before the experiment begins.
    biopac.setData(biopac, 0)

# Medoc TSA2 parameters ______________________________________________
# Initialize the Medoc TSA2 thermal stimulation delivery device
    # Medoc Troubleshooting:
    # To find the computer IP address, check with MMS Arbel's External Control (or Windows ipconfig alternatively)
    # Communication port is always 20121

if thermode_exists == 1:
    # Import medocControl library, python library custom written for Medoc with pyMedoc pollforchange functionality. 
    # Make sure medocControl.py is in the same directory 
    from medocControl import *

"""
5. Prepare Experimental Dictionaries for Medoc Temperature Programs

EDIT BELOW FOR YOUR STUDY (if you use the Medoc Thermode)
"""

"""
0c. Prepare Devices: Biopac Psychophysiological Acquisition
"""  
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.getFeedback(u3.PortStateWrite(State = [15, 0, 0]))
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)
#     Another command that may work: biopac.setData(byte)

task_ID=2
task_start=7

instructions=15

prefixation=8
midfixation=9
postfixation=10

cue=16
heat=17

instruction_code=198

pain_binary=42
intensity_rating=43

valence_rating=39
trialIntensity_rating=40
comfort_rating=41

avoid_rating = 200
relax_rating = 201
taskattention_rating = 202
boredom_rating = 203
alertness_rating = 204
posthx_rating = 205
negthx_rating = 206
self_rating = 207
other_rating = 208
imagery_rating = 209
present_rating = 210
intensity_rating=211

# Hyperalignment movie
inscapes=214

between_run_msg=45
end_task = 197

# Medoc parameters _________________________________________________
# Set up a dictionary for all the configured Medoc programs for the main thermode
# Relevant Medoc commands:
#     Prepare a program: sendCommand('select_tp', thermode_temp2program[47])
#     Poll the Machine to know if it's ready for another command: poll_for_change("[RUNNING/IDLE]", poll_interval=0.5, poll_max = -1 (unlimited), verbose=False, server_lag=1)
#           Select "RUNNING" if you are using a "Manual Trigger" and a SELECT_TP has already been sent. Select "IDLE" if you are using an "Auto" Trigger design
#     Trigger a prepared program: sendCommand('trigger')
#     Pause a program: sendCommand('pause')
#     Stop a program: sendCommand('stop')
thermode_temp2program = {
    '45': 136,
    '45.5': 137,
    '46': 138,
    '46.5': 139,
    '47': 140,
    '47.5': 141,
    '48': 142,
    '48.5': 143,
    '44': 144,
    '44.5': 145
}

# Uncomment here if you would rather read-in a dictionary via a text-file. 
# with open("thermode_programs.txt") as f:
#     for line in f:
#        (key, val) = line.split()
#        thermode_temp2program[float(key)] = int(val)