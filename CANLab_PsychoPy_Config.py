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
eyetracker_exists = 0

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

if eyetracker_exists == 1:
    # Import Eyetracker library. 
    # Make sure EyeLinkCoreGraphicsPsychoPy.py is in the same directory 
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
    
    ## Step 1: Connect to the EyeLink Host PC
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

    el_tracker = pylink.EyeLink(None)

    def setupEyetrackerFile(el_tracker, source):
    
        ## Step 2: Open an EDF data file on the Host PC
        ################## THIS NEEDS TO BE EDITTED ##############################
        sourceEDF = source
        # We download EDF data file from the EyeLink Host PC to the local hard
        # drive at the end of each testing session, here we rename the EDF to
        # include session start date/time
        # session_identifier = expName + time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
        # create a folder for the current testing session in the "results" folder
        # session_folder = os.path.join(sub_dir, session_identifier)
        # if not os.path.exists(session_folder):
        #     os.makedirs(session_folder)

        try:
            el_tracker.openDataFile(sourceEDF)
        except RuntimeError as err:
            print('EYETRACKER ERROR:', err)
            # close the link if we have one open
            if el_tracker.isConnected():
                el_tracker.close()
            core.quit()
        
        # Add a header text to the EDF file to identify the current experiment name
        # This is OPTIONAL. If your text starts with "RECORDED BY " it will be
        # available in DataViewer's Inspector window by clicking
        # the EDF session node in the top panel and looking for the "Recorded By:"
        # field in the bottom panel of the Inspector.
        preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
        el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

        return sourceEDF

    ## Step 3: Configure the tracker

    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()

    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    eyelink_ver = 0  # set version to 0, in case running in Dummy mode
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

    # File and Link data control
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

    ## EDIT THESE PARAMETERS FOR YOUR STUDY -- reasonable defaults are provided below:
    # 1. Tracking Parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    if eyelink_ver > 2:
        el_tracker.sendCommand("sample_rate 250")
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV5")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

    # 2. Optional -- Shrink the spread of the calibration/validation targets
    # if the default outermost targets are not all visible in the bore.
    # The default <x, y display proportion> is 0.88, 0.83 (88% of the display
    # horizontally and 83% vertically)
    # el_tracker.sendCommand('calibration_area_proportion 0.88 0.83')
    # el_tracker.sendCommand('validation_area_proportion 0.88 0.83')

    # 3. Optional: online drift correction.
    # See the EyeLink 1000 / EyeLink 1000 Plus User Manual
    #
    # 4. Online drift correction to mouse-click position:
    # el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
    # el_tracker.sendCommand('normal_click_dcorr = ON')

    # 5. Online drift correction to a fixed location, e.g., screen center
    # el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
    # el_tracker.sendCommand('online_dcorr_refposn %d,%d' % (int(scn_width/2.0),
    #                                                        int(scn_height/2.0)))
    # el_tracker.sendCommand('online_dcorr_button = ON')
    # el_tracker.sendCommand('normal_click_dcorr = OFF')
    """
    Byeol Helper Functions for Eyelink
    """
    # Step 4: set up a graphics environment for calibration by calling calibrateEyeTracker()
    def calibrateEyeTracker(win, el_tracker, target='circle', stim=None, biopacCode=None):
        """
        Pass in stim with the full stimulus path if target is set to anything other than 'circle' or 'spiral'
        """
        # get the native screen resolution used by PsychoPy
        scn_width, scn_height = win.size

        # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
        # see the EyeLink Installation Guide, "Customizing Screen Settings"
        el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
        el_tracker.sendCommand(el_coords)

        # Write a DISPLAY_COORDS message to the EDF file
        # Data Viewer needs this piece of info for proper visualization, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
        el_tracker.sendMessage(dv_coords)

        # Configure a graphics environment (genv) for tracker calibration
        genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
        print(genv)  # print out the version number of the CoreGraphics library

        # Set background and foreground colors for the calibration target
        # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
        foreground_color = (1, 1, 1)
        background_color = win.color
        genv.setCalibrationColors(foreground_color, background_color)

        # Set up the calibration target
        #
        # The target could be a "circle" (default), a "picture", a "movie" clip,
        # or a rotating "spiral". To configure the type of calibration target, set
        # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
        if target=='circle':
            genv.setTargetType('circle')
            #
        elif target=='spiral':
            genv.setTargetType('spiral')
            #
        elif target=='picture':
            # Use gen.setPictureTarget() to set a "picture" target
            genv.setTargetType('picture')
            genv.setPictureTarget(stim)
            #
        elif target=='movie':
            # Use genv.setMovieTarget() to set a "movie" target
            genv.setTargetType('movie')
            genv.setMovieTarget(stim)

        # Configure the size of the calibration target (in pixels)
        # this option applies only to "circle" and "spiral" targets
        genv.setTargetSize(24)

        # Beeps to play during calibration, validation and drift correction
        # parameters: target, good, error
        #     target -- sound to play when target moves
        #     good -- sound to play on successful operation
        #     error -- sound to play on failure or interruption
        # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
        genv.setCalibrationSounds('', '', '')

        # Request Pylink to use the PsychoPy window we opened above for calibration
        pylink.openGraphicsEx(genv)

        if biopac_exists:
            biopac.setData(biopac, 0)
            biopac.setData(biopac, biopacCode) # Start demarcation of the T1 task in Biopac Acqknowledge
        el_tracker.doTrackerSetup()
        if biopac_exists:
            biopac.setData(biopac, 0)
    
    def startEyetracker(el_tracker, source, destination, biopacCode=None):
        ## This should go in there:
        # put tracker in idle/offline mode before recording
        el_tracker.setOfflineMode()

        # Start recording, at the beginning of a new run
        # arguments: sample_to_file, events_to_file, sample_over_link,
        # event_over_link (1-yes, 0-no)
        try:
            if biopac_exists==1:
                biopac.setData(biopac, 0)
                biopac.setData(biopac, biopacCode)
            el_tracker.startRecording(1, 1, 1, 1)

        except RuntimeError as error:
            print("ERROR:", error)
            terminate_eyelink(pylink, el_tracker, source, destination)

        # Allocate some time for the tracker to cache some samples
        pylink.pumpDelay(100)
        el_tracker.sendMessage('Run Starts')
        if biopac_exists==1:
            biopac.setData(biopac, 0)

    def stopEyeTracker(el_tracker, source, destination, biopacCode=None):
        
        el_tracker.sendMessage('run ends')
        
        # stop recording; add 100 msec to catch final events before stopping
        pylink.pumpDelay(100)
        el_tracker.stopRecording()
        if biopac_exists==1:
            biopac.setData(biopac, 0)
            biopac.setData(biopac, biopacCode)

        # Disconnect, download the EDF file, then terminate the task
        terminate_eyelink(pylink, el_tracker, source, destination)

    def retrieve_eyelink_EDF(pylink, el_tracker, source, destination):
        el_tracker = pylink.getEYELINK()

        if el_tracker.isConnected():
            # Close the edf data file on the Host
            el_tracker.closeDataFile()

            #### SHOULD I WAIT HERE? ####

            # Download the EDF data file from the Host PC to a local data folder
            # parameters: source_file_on_the_host, destination_file_on_local_drive
            # local_edf = os.path.join(sub_dir, '%s.EDF' % expInfo['run'])
            try:
                # source: edf_file
                el_tracker.receiveDataFile(source, destination)
            except RuntimeError as error:
                print('ERROR:', error)

            # Close the link to the tracker.
            el_tracker.close()

    def terminate_eyelink(pylink, el_tracker, source, destination):
        """ Terminate the task gracefully and retrieve the EDF data file

        file_to_retrieve: The EDF on the Host that we would like to download
        win: the current window used by the experimental script
        """
        if el_tracker.isConnected():
            # Terminate the current trial first if the task terminated prematurely
            error = el_tracker.isRecording()
            if error == pylink.TRIAL_OK:
                abort_trial()

            # Put tracker in Offline mode
            el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            retrieve_eyelink_EDF(pylink, el_tracker, source, destination)
        
    def abort_trial(pylink):
        """Ends recording """

        el_tracker = pylink.getEYELINK()

        # Stop recording
        if el_tracker.isRecording():
            # add 100 ms to catch final trial events
            pylink.pumpDelay(100)
            el_tracker.stopRecording()

        # clear the screen
        # clear_screen(win)
        # Send a message to clear the Data Viewer screen
        bgcolor_RGB = (116, 116, 116)
        el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

        # send a message to mark trial end
        el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)

        return pylink.TRIAL_ERROR


"""
5. Prepare Experimental Dictionaries for Devices

EDIT BELOW FOR YOUR STUDY (if you use the Biopac or Medoc Thermode)
"""
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.getFeedback(u3.PortStateWrite(State = [15, 0, 0]))
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)
#     Another command that may work: biopac.setData(byte)

task_ID=2
task_start=7

eyetrackerCalibration=52
eyetrackerCode=53

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