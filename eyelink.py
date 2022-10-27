from __future__ import division
from __future__ import print_function

import psychopy
from psychopy import prefs
prefs.general["audioLib"] = ["PTB"]

from psychopy import sound, visual, event, core, gui, logging, data, monitors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard

import os, sys, csv, platform, time, random, math

from PIL import Image
from string import ascii_letters, digits

import numpy as np
import pandas as pd

# eyelink-byeol
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

"""
In this experiment, participants listen and respond to an audio story. The runs
go as follows:
Run 1: 1st listen, rate characters, open response
Run 2: 2nd listen, rate characters, open response

Args:
    Subject ID: (int) subject id
    Run number: (int) run number 1, 2
    Scanner: (bool) scanning or testing? space is trigger for testing
Returns:
    Onsets file: csv file with stimuli onset and offset; e.g. s01_onsets.csv


For the microphone to work, might need to start app from terminal each time with this address...
/Applications/PsychoPy.app/Contents/MacOS/PsychoPy
"""

### PATHS ###
base_dir = "/Users/f004ycz/Documents/dark-end-fmri-psychopy"  # Clare's personal laptop
data_dir = os.path.join(base_dir, "data")  # Where data goes to

### DIALOGUE SCREENS AND DATA FILE SETUP ###

# Basic info for dialogue screen
config_dialog = gui.Dlg(title="Dark End fMRI")
config_dialog.addField("Subject ID: ")
config_dialog.addField("Run Number: ")
config_dialog.addField("Scanner?: ", choices=[True, False])

# File overwrite
exists_dialog = gui.Dlg(
    title="File Already Exists",
    labelButtonOK="Yes, Overwrite",
    labelButtonCancel="Quit Program",
)
exists_dialog.addText("File name already exists. Are you sure you want to overwrite?")

# Get info to generate data file and setup devices
config_dialog.show()

if config_dialog.OK:
    print(config_dialog.data)
    subID = config_dialog.data[0]
    run_num = str(config_dialog.data[1])
    scanner = config_dialog.data[2]
else:
    core.quit()

# Generate datafile and check for overwrite
# Disable file buffering on open; instead write to it immediately
if int(subID) < 10:
    subID = "s0" + str(subID)
else:
    subID = "s" + str(subID)

# Initialize data file and write into
fName = "%s_run%s_data.csv" % (subID, run_num)
fPath = os.path.join(data_dir, fName)
if os.path.exists(fPath):
    exists_dialog.show()
    if exists_dialog.OK:
        data_file = open(fPath, "w")
    else:
        sys.exit("Program ending!")
else:
    data_file = open(fPath, "w")

data_writer = csv.writer(data_file, delimiter=",", lineterminator="\n")

# eyelink-byeol ~166
### EYELINK FILE SETUP ###

## Switch to the script folder
#script_path = os.path.dirname(sys.argv[0])
#if len(script_path) != 0:
#    os.chdir(script_path)

# Set this variable to True if you use the built-in retina screen as your
# primary display device on macOS. If have an external monitor, set this
# variable True if you choose to "Optimize for Built-in Retina Display"
# in the Displays preference settings.
use_retina = False

# Set this variable to True to run the script in "Dummy Mode"
dummy_mode = True

# Set this variable to True to run the task in full screen mode
# It is easier to debug the script in non-fullscreen mode
full_screen = True

# Set up EDF data file name and local data folder
#
# The EDF data filename should not exceed 8 alphanumeric characters
# use ONLY number 0-9, letters, & _ (underscore) in the filename
edf_fname = '%s_de'% (subID)

# Prompt user to specify an EDF data filename
# before we open a fullscreen window
dlg_title = 'Enter EDF File Name'
dlg_prompt = 'Please enter a file name with 8 or fewer characters\n' + \
             '[letters, numbers, and underscore].'

# loop until we get a valid filename
while True:
    dlg = gui.Dlg(dlg_title)
    dlg.addText(dlg_prompt)
    dlg.addField('File Name:', edf_fname)
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:  # if ok_data is not None
        print('EDF data filename: {}'.format(ok_data[0]))
    else:
        print('user cancelled')
        core.quit()
        sys.exit()

    # get the string entered by the experimenter
    tmp_str = dlg.data[0]
    # strip trailing characters, ignore the ".edf" extension
    edf_fname = tmp_str.rstrip().split('.')[0]

    # check if the filename is valid (length <= 8 & no special char)
    allowed_char = ascii_letters + digits + '_'
    if not all([c in allowed_char for c in edf_fname]):
        print('ERROR: Invalid EDF filename')
    elif len(edf_fname) > 8:
        print('ERROR: EDF filename should not exceed 8 characters')
    else:
        break

# Set up a folder to store the EDF data files and the associated resources
# e.g., files defining the interest areas used in each trial
results_folder = 'eyelink'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# We download EDF data file from the EyeLink Host PC to the local hard
# drive at the end of each testing session, here we rename the EDF to
# include session start date/time
time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
session_identifier = edf_fname + time_str

# create a folder for the current testing session in the "results" folder
session_folder = os.path.join(results_folder, session_identifier)
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

### MORE EYELINK
# eyelink-byeol ~273
#
# The Host IP address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the Pylink
# Set the Host PC address to "None" (without quotes) to run the script
# in "Dummy Mode"
if dummy_mode:
    el_tracker = pylink.EyeLink(None)
else:
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

# Step 2: Open an EDF data file on the Host PC
edf_file = edf_fname + ".EDF"
try:
    el_tracker.openDataFile(edf_file)
except RuntimeError as err:
    print('ERROR:', err)
    # close the link if we have one open
    if el_tracker.isConnected():
        el_tracker.close()
    core.quit()
    sys.exit()

# Add a header text to the EDF file to identify the current experiment name
# This is OPTIONAL. If your text starts with "RECORDED BY " it will be
# available in DataViewer's Inspector window by clicking
# the EDF session node in the top panel and looking for the "Recorded By:"
# field in the bottom panel of the Inspector.
preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# Step 3: Configure the tracker
#
# Put the tracker in offline mode before we change tracking parameters
el_tracker.setOfflineMode()

# Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
# 5-EyeLink 1000 Plus, 6-Portable DUO
eyelink_ver = 0  # set version to 0, in case running in Dummy mode
if not dummy_mode:
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

# File and Link data control
# what eye events to save in the EDF file, include everything by default
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
# what eye events to make available over the link, include everything by default
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
# what sample data to save in the EDF data file and to make available
# over the link, include the 'HTARGET' flag to save head target sticker
# data for supported eye trackers
if eyelink_ver > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Optional tracking parameters
# Sample rate, 250, 500, 1000, or 2000, check your tracker specification
# if eyelink_ver > 2:
#     el_tracker.sendCommand("sample_rate 1000")
# Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
el_tracker.sendCommand("calibration_type = HV9")
# Set a gamepad button to accept calibration/drift check target
# You need a supported gamepad/button box that is connected to the Host PC
el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

# Optional -- Shrink the spread of the calibration/validation targets
# if the default outermost targets are not all visible in the bore.
# The default <x, y display proportion> is 0.88, 0.83 (88% of the display
# horizontally and 83% vertically)
el_tracker.sendCommand('calibration_area_proportion 0.88 0.83')
el_tracker.sendCommand('validation_area_proportion 0.88 0.83')

# Optional: online drift correction.
# See the EyeLink 1000 / EyeLink 1000 Plus User Manual
#
# Online drift correction to mouse-click position:
# el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
# el_tracker.sendCommand('normal_click_dcorr = ON')

# Online drift correction to a fixed location, e.g., screen center
# el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
# el_tracker.sendCommand('online_dcorr_refposn %d,%d' % (int(scn_width/2.0),
#                                                        int(scn_height/2.0)))
# el_tracker.sendCommand('online_dcorr_button = ON')
# el_tracker.sendCommand('normal_click_dcorr = OFF')



### FMRI PROTOCOL DEVICES AND VARIABLES ###

# Inputs for proceeding on trial
proceedTrigger = "space"

# Visuals
textColor = "white"
textFont = "Arial"
textHeight = 0.10
testWinSize = (1920, 1080) #(2560, 1600)  # (960, 540)
expWinSize = (1920, 1080) # What's the best projector size?
alignText = "center"

# Show only critical warnings
logging.console.setLevel(logging.CRITICAL)

# Set experiment clocks and keyboard
globalClock = core.Clock()
crmClock = core.Clock()
defaultKeyboard = keyboard.Keyboard()

# Apply settings based on testing or real experiment
if scanner:
    winSize = expWinSize
    fullScr = True
    screen = 1
    allowGUI = False # CHECK THIS LATER
else:
    winSize = testWinSize
    fullScr = False
    screen = 0
    allowGUI = True

# Set window (THESE PARAMS ARE A MIX FROM EYELINK TO THE PROTOCOL SCRIPT
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
win = visual.Window(size=winSize, fullscr=fullScr, screen=screen, allowGUI=allowGUI, color="black",
                    monitor=mon, winType = 'pyglet',
                    units='pix'
                    )
# DO I NEED PIX AS UNITS?

# Define a cleanup function to handle device closures
def clean_up(scanner=scanner):
    """Because pyo audio backend tends to cause experiment crashes on close.
    add some print messages to assure we at least get to the end."""
    print("CLOSING WINDOW...")
    print("Overall, %i frames were dropped." % win.nDroppedFrames)
    
    ## RESPONSE FROM MJ
    ## Added this to get the EDF from the Host PC and shut down the connection
    terminate_task()
    
    win.close()
    print("QUITTING...")
    core.quit()
# For close outs, associated with clean_up function
event.globalKeys.add(key="escape", func=clean_up, name="shutdown")

### BACK TO EYELINK ###
# eyelink-byeol ~413

# Step 4: set up a graphics environment for calibration
#
# Open a window, be sure to specify monitor parameters
#mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
#win = visual.Window(fullscr=full_screen,
#                    monitor=mon,
#                    winType='pyglet',
#                    units='pix')
# ^^ THIS IS DONE ABOVE
# get the native screen resolution used by PsychoPy
scn_width, scn_height = win.size
# resolution fix for Mac retina displays
if 'Darwin' in platform.system():
    if use_retina:
        scn_width = int(scn_width/2.0)
        scn_height = int(scn_height/2.0)
print(scn_width)
print(scn_height)

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
foreground_color = (-1, -1, -1)
background_color = win.color
genv.setCalibrationColors(foreground_color, background_color)

# Set up the calibration target
#
# The target could be a "circle" (default), a "picture", a "movie" clip,
# or a rotating "spiral". To configure the type of calibration target, set
# genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
# genv.setTargetType('picture')
#
# Use gen.setPictureTarget() to set a "picture" target
# genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
#
# Use genv.setMovieTarget() to set a "movie" target
# genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

# Use a picture as the calibration target
genv.setTargetType('picture')
genv.setPictureTarget(os.path.join('stimuli', 'fixTarget.bmp'))

# Configure the size of the calibration target (in pixels)
# this option applies only to "circle" and "spiral" targets
# genv.setTargetSize(24)

# Beeps to play during calibration, validation and drift correction
# parameters: target, good, error
#     target -- sound to play when target moves
#     good -- sound to play on successful operation
#     error -- sound to play on failure or interruption
# Each parameter could be ''--default sound, 'off'--no sound, or a wav file
#genv.setCalibrationSounds('', '', '')

# resolution fix for macOS retina display issues
if use_retina:
    genv.fixMacRetinaDisplay()

# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)

### DARK END SCREENS AND STIMULI ###

# Fixation
fixation = visual.TextStim(win=win, name="fixation", text="+", color=textColor, font=textFont, height=0.20, anchorHoriz=alignText,)

# Scales
testScale = visual.RatingScale(win=win, name='test', marker='slider', markerColor="Gray", stretch=1.5, leftKeys='1', rightKeys = '2', acceptKeys='return', lineColor='White',noMouse = True,acceptPreText='left       right',
                           textColor='White', size=1, pos=[0.0, 0.0], low=1, high=9, labels=['\n\nIndex Finger\n"1"\nLEFT','\n\nMiddle Finger\n"2"\nRIGHT',], scale='', textSize=.7,
                           markerStart='5', showAccept=False)

volumeScale = visual.RatingScale(win=win, name='volume', marker='slider', markerColor="Gray", stretch=1.5, leftKeys='1', rightKeys = '2', acceptKeys='return', lineColor='White',noMouse = True,acceptPreText='left       right',
                           textColor='White', size=1, pos=[0.0, -0.6], low=1, high=9, labels=['Turn it Down','Good!','Turn it Up'], scale='', textSize=.7,
                           markerStart='5', showAccept=False)

crmScale = visual.RatingScale(win=win, name='rate', marker='slider', markerColor="Gray", stretch=1.5, leftKeys='1', rightKeys = '2', acceptKeys='return', lineColor='White',noMouse = True,acceptPreText='left       right',
                           textColor='White', size=1, pos=[0.0, -300], low=1, high=9, labels=['Negative','Neutral','Positive'], scale='', textSize=.7,
                           markerStart='5', showAccept=False)

charScale = visual.RatingScale(win=win, low=(1), high=7, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=4, tickMarks = [1,2,3,4,5,6,7],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'], disappear=False,
    labels = ["\nDislike\nStrongly", "\nDislike", "\nSlightly\nDislike", "\nNeutral", "\nSlightly\nLike", "\nLike", "\nLike\nstrongly"],
    textSize = 0.85, stretch = 2.2)

## Memory question scales
memoryS1 = visual.RatingScale(win=win, low=1, high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nA sales\nclerk", "\nA robot", "\nA security\nguard", "\nA bride", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)
memoryS2 = visual.RatingScale(win=win, low=(1), high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nA man", "\nA dog", "\nA car", "\nMall\nsecurity", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)
memoryS3 = visual.RatingScale(win=win, low=(1), high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nRoyal\nBridal", "\nBridal\nElegance", "\nBridal\nInnovations", "\nElegant\nBridal", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)
memoryS4 = visual.RatingScale(win=win, low=(1), high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nZombies", "\nNuclear\nexplosion", "\nGlobal\npandemic", "\nNanotechnology", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)
memoryS5 = visual.RatingScale(win=win, low=(1), high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nCalzone", "\nFritos\nnachos", "\nChicken\nTeriyaki", "\nPizza", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)
memoryS6 = visual.RatingScale(win=win, low=(1), high=5, precision = 1, marker = 'triangle', markerColor = 'blue', markerStart=5, tickMarks = [1,2,3,4,5],
    showAccept = False, leftKeys='1', rightKeys = '2', acceptKeys=['3','4'],disappear=False,
    labels = ["\nHer\nboss", "\nA client", "\nHer\nboyfriend", "\nMall\nsecurity", "\nI don't\nknow"],
    textSize = 0.85, stretch = 2.2)

memoryQ1 = "What is Lucy?"
memoryQ2 = "What does Lucy hear running in the mall throughout the story?"
memoryQ3 = "What is the name of the shop where this story takes place?"
memoryQ4 = "What caused the destruction of humankind?"
memoryQ5 = "What dish does Lucy recommend Steve buy at the food court?"
memoryQ6 = "Who does Lucy think she is talking to at the beginning of the story?"

imgInstructScaleX = 1.7
imgInstructScaleY = 1.7

# Instruciton Images (we use images because of some potential bugs with TextStim, so we minimize that use)
taskCRM = visual.ImageStim(win, image='stimuli/task-crm.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskCRM2 = visual.ImageStim(win, image='stimuli/task-instruct-run2.jpg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskRater = visual.ImageStim(win, image='stimuli/task-rater.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
memQInstruct = visual.ImageStim(win, image='stimuli/comp-questions.jpg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskMicInstruct1 = visual.ImageStim(win, image='stimuli/task-mic-1.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskMicInstruct2 = visual.ImageStim(win, image='stimuli/task-mic-2.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskMicLive1 = visual.ImageStim(win, image='stimuli/task-mic-live-1.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
taskMicLive2 = visual.ImageStim(win, image='stimuli/task-mic-live-2.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])
trialMicLive = visual.ImageStim(win, image='stimuli/pretask-mic-1.jpeg', units = 'norm', size = (imgInstructScaleX,imgInstructScaleY), pos=[0, 0])

#crmRaterPixSizeX = 

imgStimulusScaleX = 0.9
imgStimulusScaleY = 0.9

# Image during story listening
bridalshopimg = visual.ImageStim(win, image='stimuli/bridalshop.jpeg', units = 'norm', size = (imgStimulusScaleX,imgStimulusScaleY), pos=[0, 0])

# Audio story variables
if scanner:
    storyDur = 40 #1105.0
    storyFile = os.path.join(base_dir, "audiofiles/dark-end-of-the-mall_edited_smaller.wav")
else:
    storyDur = 6.0
    storyFile = os.path.join(base_dir, "audiofiles/short-audio-sample.wav")

### EYELINK HELPER FUNCTIONS ###
# eyelink-byeol ~591
def clear_screen(win):
    """ clear up the PsychoPy window"""

    win.fillColor = genv.getBackgroundColor()
    win.flip()

def show_msg(win, text, wait_for_keypress=True):
    """ Show task instructions on screen"""

    msg = visual.TextStim(win, text,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    clear_screen(win)
    msg.draw()
    win.flip()

    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        event.waitKeys()
        clear_screen(win)

def terminate_task():
    """ Terminate the task gracefully and retrieve the EDF data file

    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """

    el_tracker = pylink.getEYELINK()

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

        # Close the edf data file on the Host
        el_tracker.closeDataFile()

        # Show a file transfer message on the screen
        msg = 'EDF data is transferring from EyeLink Host PC...'
        show_msg(win, msg, wait_for_keypress=False)

        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(session_folder, session_identifier + '.EDF')
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        el_tracker.close()

    # close the PsychoPy window
    win.close()

    # quit PsychoPy
    core.quit()
    sys.exit()

def abort_trial():
    """Ends recording """

    el_tracker = pylink.getEYELINK()

    # Stop recording
    if el_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        el_tracker.stopRecording()

    # clear the screen
    clear_screen(win)
    # Send a message to clear the Data Viewer screen
    bgcolor_RGB = (116, 116, 116)
    el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

    # send a message to mark trial end
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)

    return pylink.TRIAL_ERROR



### DARK END FUNCTIONS/SUBROUTINES ###

# Draw fixation cross to direct participant eye gaze
def draw_fixation():
    fixation.draw()
    win.flip()
    ## RESPONSE FROM MARCUS
    ## Added the message below to send a message to the EDF
    ## when the fixation cross onsets
    el_tracker.sendMessage('Fixation_onset')

def instructions(instructImage, duration):
    instructTimer = core.Clock()
    instructCountDown = core.CountdownTimer(duration)
    while instructTimer.getTime() < duration:
       instructImage.draw()
       timeleft = visual.TextStim(win = win, ori = 0, text = str(instructCountDown.getTime())[:str(instructCountDown.getTime()).find('.')], font = textFont, units = 'norm', pos = [0,-0.85], color = 'Gray', height=.07)
       timeleft.draw()
       win.flip()
    instructCountDown.reset()
    instructTimer.reset()

def CRM(screenimage, audioFile, scale):
    story = sound.Sound(storyFile)
    routineTimer = core.CountdownTimer()
    routineTimer.reset()
    crmClock.reset()  # clock
    routineTimer.add(storyDur)
    scale.reset()
    storyStart = crmClock.getTime()
    print(f'Start Story: {storyStart}')
    data_writer.writerow(['startTime', storyStart])
    
    ##RESPONSE FROM MARCUS
    # eyelink-byeol
    ## ADDED the following to get a reference to the currently active EyeLink connection
    el_tracker = pylink.getEYELINK()
    
    ##RESPONSE FROM MARCUS
    ## ADDED the following variable to specify whether we've started drawing or not
    ## so that we don't send message on every screen update after image/scale onset
    initialDrawingCompleted = 0
    
    story.play()
    
    ## RESPONSE FROM MARCUS
    ## Added the message below to send a message to the EDF
    ## when the story starts playing
    el_tracker.sendMessage('story_onset')
    
    while routineTimer.getTime() > 0:
        screenimage.setAutoDraw(True)
        scale.setAutoDraw(True)
        win.flip()
        if initialDrawingCompleted == 0:
            
            ## RESPONSE FROM MARCUS
            ## Added the message below to send a message to the EDF
            ## when the image/scale initially onset
            el_tracker.sendMessage('Image_Scale_onset')
            initialDrawingCompleted == 1
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
    storyStop = crmClock.getTime()
    print(f'Stop Story: {storyStop}')
    story.stop()  # ensure sound has stopped at end of routine
    el_tracker.sendMessage('story_offset')
    screenimage.setAutoDraw(False)
    scale.setAutoDraw(False)
    data_writer.writerow(['storyStopped', storyStop])
    data_writer.writerow(['crmScaleHistory', scale.getHistory()])
    routineTimer.reset()

def GetMemRatings(memQ, memScale):
    memTimer = core.Clock()
    memRateStart = globalClock.getTime()
    memTimer.reset()
    data_writer.writerow([memQ+"Time", globalClock.getTime()])
    memQuestion = visual.TextStim(win=win, text=memQ, pos=(0,.1), color=textColor, anchorHoriz=alignText, font = textFont, units = 'norm', name="charQuestion")
    memCountDown = core.CountdownTimer(10)
    while memScale.noResponse:
        memtimeleft = visual.TextStim(win = win, ori = 0, text = str(memCountDown.getTime())[:str(memCountDown.getTime()).find('.')], font = textFont, pos = [0,-0.8], color = 'Gray', units = 'norm', height=.07)
        memtimeleft.draw()
        memQuestion.draw()
        memScale.draw()
        win.flip()
        if memTimer.getTime() > 10.0:
            data_writer.writerow([memQ+"LastPosition",memScale.getRating()])
            break
    for key in event.getKeys():
        if key in ['escape', 'q']:
            # End the experiment.
            win.close()
            core.quit()
    if memScale.noResponse == False:
            data_writer.writerow([memQ+"Rating", memScale.getRating()])
            data_writer.writerow([memQ+"RT",memScale.getRT()])
    while memScale.noResponse == False:
        for key in event.getKeys():
            if key in ['escape', 'q']:
                # End the experiment.
                win.close()
                core.quit()
        while memCountDown.getTime() > 0.0:
            memtimeleft = visual.TextStim(win = win, ori = 0, text = str(memCountDown.getTime())[:str(memCountDown.getTime()).find('.')], font = textFont, units = 'norm', pos = [0,-0.8], color = 'Gray', height=.07)
            memtimeleft.draw()
            memQuestion.draw()
            memScale.draw()
            nextPrompt = visual.TextStim(win = win, ori = 0, text = 'Please wait for next prompt', font = textFont, units = 'norm', pos = [0.0,0.65], color = 'Gray')
            nextPrompt.draw()
            win.flip()
            for key in event.getKeys():
                if key in ['escape', 'q']:
                    # End the experiment.
                    win.close()
                    core.quit()
        break
    memQEnd = globalClock.getTime()
    data_writer.writerow([memQ+"RateEnd",globalClock.getTime()])
    memTimer.reset()

# Function for getting character ratings, includes timer
charList = ['Lucy','Steve']
def GetCharRatings():
    charTimer = core.Clock()
    charRateStart = globalClock.getTime()
    for person in charList:
        charTimer.reset()
        charScale.reset()
        data_writer.writerow([person+"RateBegin", globalClock.getTime()])
        prompt = "Overall, how much do you like "+person+"?"
        charQuestion = visual.TextStim(win=win, text=prompt, pos=(0,.1), color=textColor, anchorHoriz=alignText, font = textFont, units = 'norm', name="charQuestion")
        countDown = core.CountdownTimer(10)
        while charScale.noResponse:
            timeleft = visual.TextStim(win = win, ori = 0, text = str(countDown.getTime())[:str(countDown.getTime()).find('.')], font = textFont, pos = [0,-0.8], color = 'Gray', units = 'norm', height=.07)
            timeleft.draw()
            charQuestion.draw()
            charScale.draw()
            win.flip()
            if charTimer.getTime() > 10.0:
                data_writer.writerow([person+"NoLikesPosition",+charScale.getRating()])
                data_writer.writerow([person+"Rating","nan"])
                data_writer.writerow([person+"LikesRespTime","nan"])
                break
        for key in event.getKeys():
            if key in ['escape', 'q']:
                # End the experiment.
                win.close()
                core.quit()
        if charScale.noResponse == False:
                data_writer.writerow([person+"Rating",charScale.getRating()])
                data_writer.writerow([person+"LikesRespTime",+charScale.getRT()])
        while charScale.noResponse == False:
            for key in event.getKeys():
                if key in ['escape', 'q']:
                    # End the experiment.
                    win.close()
                    core.quit()
            while countDown.getTime() > 0.0:
                timeleft = visual.TextStim(win = win, ori = 0, text = str(countDown.getTime())[:str(countDown.getTime()).find('.')], font = textFont, units = 'norm', pos = [0,-0.8], color = 'Gray', height=.07)
                timeleft.draw()
                charQuestion.draw()
                charScale.draw()
                nextPrompt = visual.TextStim(win = win, ori = 0, text = 'Please wait for next prompt', font = textFont, units = 'norm', pos = [0.0,0.65], color = 'Gray')
                nextPrompt.draw()
                win.flip()
                for key in event.getKeys():
                    if key in ['escape', 'q']:
                        # End the experiment.
                        win.close()
                        core.quit()
            break
        charRateEnd = globalClock.getTime()
        data_writer.writerow([person+"RateEnd",globalClock.getTime()])
    charTimer.reset()

# Function for recording free responses, including a timer
def GetFreeRecall(recallTime, image):
    responseStart = globalClock.getTime()
    outFile = 'data/%s_%s.wav' % (subID, run_num)
    recallTimer = core.Clock()
    recallCountDown = core.CountdownTimer(recallTime)
    mic.start()  # start recording
    
    ## RESPONSE FROM MARCUS
    ## Added the message below to send a message to the EDF
    ## when the audio recording starts
    el_tracker.sendMessage('Audio_Recording_Start')
    
    while recallTimer.getTime() < recallTime:
        timeleft = visual.TextStim(win = win, ori = 0, text = str(recallCountDown.getTime())[:str(recallCountDown.getTime()).find('.')], font = textFont, units = 'norm', pos = [0,-0.8], color = 'Gray', height=.06)
        image.draw()
        timeleft.draw()
        win.flip()
    mic.stop()  # stop recording
    audioClip = mic.getRecording()
    audioClip.save(outFile)
    responseEnd = globalClock.getTime()



### EXPERIMENT ###

# eyelink-byeol
# EYETRACK SETUP
# Show the task instructions
if not dummy_mode:
    task_msg = 'Press ENTER to calibrate tracker'
    show_msg(win, task_msg)

# Set up the camera and calibrate the tracker, if not running in dummy mode
if not dummy_mode:
    try:
        el_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        el_tracker.exitCalibration()

# send a message to mark the start of the run
#el_tracker.sendMessage('RUNSTART')

## DO I NEED THIS?
############################ FROM MARCUS #######################################
##RESPONSE FROM MARCUS
## No, you don't need this, but it can help to have landmarks on the Host PC 
## so that you can monitor the accuracy of the eye tracker
## during recording 


## RESPONSE FROM MARCUS these are the image definitions taken from above -- copied here so that scaling
## and image paths can be used if you use the bitmaptobackrop function as
## described below

#taskCRM ='stimuli/task-crm.jpeg', units = 'norm', size = (1.7,1.7), pos=[0, 0])
#taskRater = visual.ImageStim(win, image='stimuli/task-rater.jpeg', units = 'norm', size = (1.7,1.7), pos=[0, 0])
#bridalshopimg = visual.ImageStim(win, image='stimuli/bridalshop.jpeg', units = 'norm', size = (.9,.9), pos=[0, 0])

## RESPONSE FROM MARCUS
## you can use the section of code below to send a copy of the stimuli to the
## Host PC so that you can see the gaze cursor in relation to the stimuli
## while recording data during the session
##NOTE: the values for the bitmaptobackdrop (width, height, pixel, crop_x, crop_y,
## crop_width, crop_height, x, y should be provided in pixels
## So, some conversion would need to be done to convert the norm values you are
## using to pixel values

# put the tracker in the offline mode first
#el_tracker.setOfflineMode()

# If you need to scale the backdrop image on the Host, use the old Pylink
# bitmapBackdrop(), which requires an additional step of converting the
# image pixels into a recognizable format by the Host PC.
# pixels = [line1, ...lineH], line = [pix1,...pixW], pix=(R,G,B)
#
# the bitmapBackdrop() command takes time to return, not recommended
# for tasks where the ITI matters, e.g., in an event-related fMRI task
# parameters: width, height, pixel, crop_x, crop_y,
#             crop_width, crop_height, x, y on the Host, drawing options
#
# Use the code commented below to convert the image and send the backdrop
#im = Image.open('images' + os.sep + pic)  # read image with PIL
#im = im.resize((scn_width, scn_height))
#img_pixels = im.load()  # access the pixel data of the image
#pixels = [[img_pixels[i, j] for i in range(scn_width)]
#          for j in range(scn_height)]
#el_tracker.bitmapBackdrop(scn_width, scn_height, pixels,
#                          0, 0, scn_width, scn_height,
#                          0, 0, pylink.BX_MAXCONTRAST)

## RESPONSE FROM MARCUS
## Alternatively (or additionally), you could draw simple shapes on the Host PC
## so that you can compare gaze position to stimulus position during recording
## on the Host PC

#el_tracker.sendCommand('clear_screen 0')

### CLARE WORK ON THIS HERE
# For illustration purpose, we draw a rectangle on the Host screen
# For a list of supported draw commands, see the "COMMANDS.INI" file on the
# Host PC (under /elcl/exe)
# Host PC (under /elcl/exe)
#left = int(scn_width/2.0) - 60
#top = int(scn_height/2.0) - 60
#right = int(scn_width/2.0) + 60
#bottom = int(scn_height/2.0) + 60
#draw_cmd_img = 'draw_filled_box %d %d %d %d 1' % (left, top, right, bottom)
#el_tracker.sendCommand(draw_cmd_img)

#left = int(scn_width/2.0) - 60
#top = int(scn_height/2.0) - 60
#right = int(scn_width/2.0) + 60
#bottom = int(scn_height/2.0) + 60
#draw_cmd_scale = 'draw_filled_box %d %d %d %d 1' % (left, top, right, bottom)
#el_tracker.sendCommand(draw_cmd_scale)

######################### END FROM MARCUS ######################################

## NON EYETRACK SETUP
# Set up microphone
recordingDevicesList = sound.Microphone.getDevices()
print(recordingDevicesList[0])
recordingDevice = recordingDevicesList[0]
mic = sound.Microphone(streamBufferSecs=90.0, device=recordingDevice, channels=1)


data_writer.writerows([["subID",subID],['runNum',run_num]])

## EYELINK
# eyelink-byeol~946
# set up a global timer for eyetracker
scan_clock = core.Clock()

# we recommend drift-check at the beginning of each trial, in an MRI
# setup, however, this is not possible and one can do online drift-
# correction if needed
# the doDriftCorrect() function requires target position in integers
# the last two arguments:
# draw_target (1-default, 0-draw the target then call doDriftCorrect)
# allow_setup (1-press ESCAPE to recalibrate, 0-not allowed)
#
# Skip drift-check if running the script in Dummy Mode
while not dummy_mode:
    # terminate the task if no longer connected to the tracker or
    # user pressed Ctrl-C to terminate the task
    if (not el_tracker.isConnected()) or el_tracker.breakPressed():
        terminate_task()

    # drift-check and re-do camera setup if ESCAPE is pressed
    try:
        error = el_tracker.doDriftCorrect(int(scn_width/2.0),
                                        int(scn_height/2.0), 1, 1)
        # break following a success drift-check
        if error is not pylink.ESC_KEY:
            break
    except:
        pass

# put tracker in idle/offline mode before recording
el_tracker.setOfflineMode()

# Start recording, at the beginning of a new run
# arguments: sample_to_file, events_to_file, sample_over_link,
# event_over_link (1-yes, 0-no)
try:
    el_tracker.startRecording(1, 1, 1, 1)
except RuntimeError as error:
    print("ERROR:", error)
    terminate_task()

# Allocate some time for the tracker to cache some samples
pylink.pumpDelay(100)


# WAIT FOR TRIGGER HERE
# Borrowed & adapted from Michael Sun from Wager (CAN) Lab [Oct, 2021]
if scanner:
    start_msg = "The story is about to begin.\nRelax, and remember to keep your \nhead still and eyes open." # \n Experimenter press [space] to continue."
    start = visual.TextStim(win, text=start_msg, units = 'norm', height=0.05, color=textColor)
    start.draw()  # Automatically draw every frame
    win.flip()
    continueRoutine = True
    event.clearEvents()

#    # Wait for experimenter to press space before waiting to receive trigger from scanner
#    trigger = ""
#    while trigger != proceedTrigger:
#        trigger = event.getKeys(keyList=["space"])
#        if trigger:
#            trigger = trigger[0]

    while continueRoutine == True:
        if "5" in event.getKeys(keyList="5"):  # <-- GET YOUR FMRI TRIGGER THIS WAY
            fmriStart = globalClock.getTime()  # Start the clock
            
            ## RESPONSE FROM MARCUS
            ## Added the message below to send a message to the EDF
            ## when the trigger signal is received
            el_tracker.sendMessage('FMRI_START_TRIGGER_RECEIVED')
            
            
            # [10.29.21] Currently comment out the wait time
            # as Terry said dummy scans are taken _before_ trigger is received
            # timer = core.CountdownTimer()  # Wait 6 TRs, Dummy Scans
            # timer.add(TR * 6)

            # while timer.getTime() > 0:
            #     continue
            start_msg = "The story is about to begin.\nRelax, and remember to keep your \nhead still and eyes open."
            start = visual.TextStim(win, text=start_msg, units = 'norm', height=0.05, color=textColor)
            start.draw()  # Automatically draw every frame
            win.flip()

            continueRoutine = False
else:
    # Wait for experimenter to press space
    start_msg = "Please wait. \nThe scan will begin shortly. \n Experimenter press [space] to continue."
    start = visual.TextStim(win, text=start_msg, units = 'norm', height=0.05, color=textColor)
    start.draw()  # Automatically draw every frame
    win.flip()
    
    trigger = ""
    while trigger != proceedTrigger:
        trigger = event.getKeys(keyList=["space"])
        if trigger:
            
            trigger = trigger[0]
            fmriStart = globalClock.getTime()
            
            ## RESPONSE FROM MARCUS
            ## Added the message below to send a message to the EDF
            ## when the trigger signal is received
            el_tracker.sendMessage('FMRI_START_TRIGGER_RECEIVED')

# Record start
data_writer.writerow(["fmriStart",fmriStart])

# START EYELINK

# record a message to mark the start of scanning
el_tracker.sendMessage('Scan_start_Run_%s' % (run_num))

# reset the global clock to compare stimulus timing
# to time 0 to make sure each trial is 6-sec long
# this is known as "non-slip timing"
scan_clock.reset()

### TASK VARIABLES

el_tracker.sendMessage('CRMinstructions_onset')

# Instructions
if int(run_num) == 1:
    instructions(taskCRM, 15.0)
elif int(run_num) == 2:
    instructions(taskCRM2, 15.0)

# Story listen & rate
crm_onset = globalClock.getTime() - fmriStart

CRM(bridalshopimg, storyFile, crmScale)

el_tracker.sendMessage('CRM_offset')

crm_offset = globalClock.getTime() - fmriStart
crm_dur = crm_onset-crm_offset

data_writer.writerows([["crmOnset",crm_onset],["crmOffset",crm_offset],["crmDur",crm_dur]])

# Rater instructions
instructions(taskRater, 15.0)

# Get ratings
ratingsOnset = globalClock.getTime() - fmriStart
el_tracker.sendMessage('ratings_onset')

GetCharRatings()

ratingsOffset = globalClock.getTime() - fmriStart
el_tracker.sendMessage('ratings_offset')
data_writer.writerows([["ratingsOnset",ratingsOnset],["ratingsOffset",ratingsOffset]])

# Memory test
instructions(memQInstruct, 15)

memOnset = globalClock.getTime() - fmriStart
el_tracker.sendMessage('memory_onset')

if int(run_num) == 1:
    GetMemRatings(memoryQ1, memoryS1)
    GetMemRatings(memoryQ2, memoryS2)
    GetMemRatings(memoryQ3, memoryS3)
elif int(run_num) == 2:
    GetMemRatings(memoryQ4, memoryS4)
    GetMemRatings(memoryQ5, memoryS5)
    GetMemRatings(memoryQ6, memoryS6)
    
memOffset = globalClock.getTime() - fmriStart
el_tracker.sendMessage('mem_offset')

data_writer.writerows([["memOnset",memOnset],["memOffset",memOffset]])

if scanner:
    if int(run_num) == 1:
        instructions(taskMicInstruct1, 15.0)
        GetFreeRecall(60, taskMicLive1)
    elif int(run_num) == 2:
        instructions(taskMicInstruct2, 15.0)
        GetFreeRecall(60, taskMicLive2)
else:
    instructions(taskMicInstruct1, 10.0)
    GetFreeRecall(10, taskMicLive1)
el_tracker.sendMessage('mic_offset')

draw_fixation()
core.wait(2)

# send a message to mark the end of a run
el_tracker.sendMessage('Scan_end_Run_%d' % (int(run_num)))

# clear the screen
clear_screen(win)

# eyelink-byeol
# stop recording; add 100 msec to catch final events before stopping
pylink.pumpDelay(100)
el_tracker.stopRecording()

# Step 7: disconnect, download the EDF file, then terminate the task
terminate_task()

# Close out
win.close()
core.quit()

# total time 1-14-22 = 1230 seconds
