#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CANLAB Psychopy Builder Template

This template is based on PsychoPy Builder Scripts.
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y
        
As a consequence, in one day, correct running of these paradigms will generate [number]x files of the names:
sub-SIDXXXXX_ses-XX_task-[name]_run-X_events.tsv

Each file will consist of the following headers:
onset   duration    intensity   ...

0a. Import Libraries
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

import pylink

# The critical imports:
from CANLab_PsychoPy_Utilities import *
from CANLab_PsychoPy_Config import *

__author__ = "Your Name"
__version__ = "1.0.0"
__email__ = "Your Email"
__status__ = "Specify 'Production' or 'Development'"


"""
0b. Helper functions for your study
"""
def functionName(**kwargs):
    return

"""
1. Experimental Parameters
Clocks, folder paths, etc.
"""
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"

"""
2. Start Experimental Dialog Boxes
"""
if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'first(1) or second(2) day': '1',
    'gender': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS',
    'run': 1,
    'body sites': ''
    }
else:
    expInfo = {
    'DBIC Number': '',
    'first(1) or second(2) day': '', 
    'gender': '',
    'session': '',
    'handedness': '', 
    'scanner': '',
    'run': '',
    'body sites': '' 
    }

# Load the subject's calibration file and ensure that it is valid
# Upload participant file: Browse for file
# Store info about the experiment session
subjectInfoBox("CANLab Study Scan", expInfo)
expName = 'CANLab-Study'
psychopyVersion = '2020.2.10'
expInfo['psychopyVersion'] = psychopyVersion
expInfo['expName'] = expName

""" 
4. Setup the Window
"""
win=setupWindow()
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

# EDIT THIS FOR YOUR STUDY
varNames = ['onset', 'duration', 'value', 'bodySite', 'temperature', 'condition', 'keys', 'rt', 'phase', 'biopacCode']
bids_data=pd.DataFrame(columns=varNames)

"""
5. Initialize Run-level Components
"""
# Configure the number of runs in your study
totalRuns=4

# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
s_text='[s]-press confirmed.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

## Instruction Parameters
InstructionText = "Welcome to the scan, please wait for the experimenter to press [Space]."

# Rating question text
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"

totalTrials = 6 # Figure out how many trials would be equated to 5 minutes
stimtrialTime = 20 # This becomes very unreliable with the use of poll_for_change().

ratingTime = 5 # Rating Time limit in seconds during the inter-stimulus-interval

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 1

# Pre-rating audio ding to wake participants up.
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5, sampleRate=44100)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

IntensityText = 'HOW INTENSE was the WORST heat you experienced?'
ComfortText = "How comfortable do you feel right now?" # (Bipolar)
ValenceText = "HOW UNPLEASANT was the WORST heat you experienced?"  # 0 -- Most Unpleasant (Unipolar)
AvoidText = "Please rate HOW MUCH you want to avoid this experience in the future?" # Not at all -- Most(Unipolar)
RelaxText = "How relaxed are you feeling right now?" # Least relaxed -- Most Relaxed (Unipolar)
TaskAttentionText = "During the last scan, how well could you keep your attention on the task?" # Not at all -- Best (Unipolar)
BoredomText = "During the last scan, how bored were you?" # Not bored at all -- Extremely Bored (Unipolar)
AlertnessText = "During the last scan how sleepy vs. alert were you?" # Extremely Sleepy - Neutral - Extremely Alert (Bipolar)
PosThxText = "The thoughts I experienced during the last scan were POSITIVE" # Strongly disagree - Neither - Strongly Agree (Bipolar)
NegThxText = "The thoughts I experienced during the last scan were NEGATIVE" # Strongly disagree - Neither - Strongly agree (bipolar)
SelfText = "The thoughts I experienced during the last scan were related to myself" # Strongly disagree -- Neither -- Strongly Agree (Bipolar)
OtherText = "The thoughts I experienced during the last scan concerned other people." # Strongly disagree - Neither - Strongly agree (Bipolar)
ImageryText = "The thoughts I experienced during the last scan were experienced with clear and vivid mental imagery" # Strongly disagree - Neither - Strongly agree (bipolar)
PresentText = "The thoughts I experienced during the last scan pertained to the immediate PRESENT (the here and now)" # Strongly disagree - Neither - Strongly agree (bipolar)

cueImg="path-to-cue-img.png"


if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

"""
6. Welcome Instructions
"""
# showText(win, "Instructions", InstructionText, noRecord=True)

# if eyetracker_exists==1:
#     sourceEDF_filename = "S%dR%s.EDF" % (int(expInfo['DBIC Number']), 'test')
#     # Sourcename can only be 8 characters, alphanumeric or underscore
#     sourceEDF = setupEyetrackerFile(el_tracker, sourceEDF_filename)
#     calibrateEyeTracker(win, el_tracker, eyetrackerCalibration)
#     # This allows you to control the eyetracker software!

for runs in range(totalRuns):
    el_tracker = pylink.EyeLink("100.1.1.1")
    if eyetracker_exists==1:
        # filename can't be more than 8 characters long
        # sourceEDF_filename = "S%dR%d.EDF" % (int(expInfo['DBIC Number']), runs+1)
        sourceEDF_filename = "test.EDF"
        sourceEDF = "1.EDF"
        # sourceEDF = setupEyetrackerFile(el_tracker, sourceEDF_filename)

        try:
            el_tracker.openDataFile(sourceEDF)
        except RuntimeError as err:
            print('EYETRACKER ERROR:', err)
            # close the link if we have one open
            if el_tracker.isConnected():
                el_tracker.close()
            core.quit()


        destinationEDF = os.path.join(sub_dir, "S%dR%d.EDF" % (int(expInfo['DBIC Number']), runs+1))
        startEyetracker(el_tracker, sourceEDF, destinationEDF, eyetrackerCode)
        


    """
    7. Start Scanner
    """
    fmriStart=confirmRunStart(win)

    """
    14. Begin post-run self-report questions
    """        
    rating_sound.stop() # A stop needs to be introduced in order to hear playback again.
    rating_sound.play() # Alert participants to make ratings.
    bids_data=bids_data.append(showRatingScale(win, "ComfortRating", ComfortText, os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]), type="bipolar", time=ratingTime, biopacCode=comfort_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "ValenceRating", ValenceText, os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]), type="bipolar", time=ratingTime, biopacCode=valence_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "IntensityRating", IntensityText, os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=comfort_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "AvoidanceRating", AvoidText, os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]), type="bipolar", time=ratingTime, biopacCode=avoid_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "RelaxationRating", RelaxText, os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]), type="bipolar", time=ratingTime, biopacCode=relax_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "AttentionRating", TaskAttentionText, os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]), type="bipolar", time=ratingTime, biopacCode=taskattention_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "BoredomRating", BoredomText, os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]), type="bipolar", time=ratingTime, biopacCode=boredom_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "AlertnessRating", AlertnessText, os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]), type="bipolar", time=ratingTime, biopacCode=alertness_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "PosThxRating", PosThxText, os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]), type="bipolar", time=ratingTime, biopacCode=posthx_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "NegThxRating", NegThxText, os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]), type="bipolar", time=ratingTime, biopacCode=negthx_rating), ignore_index=True)  
    bids_data=bids_data.append(showRatingScale(win, "SelfRating", SelfText, os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]), type="bipolar", time=ratingTime, biopacCode=self_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "OtherRating", OtherText, os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]), type="bipolar", time=ratingTime, biopacCode=other_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "ImageryRating", ImageryText, os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]), type="bipolar", time=ratingTime, biopacCode=posthx_rating), ignore_index=True)
    bids_data=bids_data.append(showRatingScale(win, "PresentRating", PresentText, os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]), type="bipolar", time=ratingTime, biopacCode=present_rating), ignore_index=True)
    rating_sound.stop() # Stop the sound so it can be played again.

    if eyetracker_exists==1:
        # stopEyeTracker(el_tracker, sourceEDF, destinationEDF, biopacCode=eyetrackerCode)

        if el_tracker.isConnected():
            # Terminate the current trial first if the task terminated prematurely
            error = el_tracker.isRecording()
            # if error == pylink.TRIAL_OK:
            #     abort_trial()

            # Put tracker in Offline mode
            el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            # el_tracker = pylink.getEYELINK()

            if el_tracker.isConnected():
                # Close the edf data file on the Host
                el_tracker.closeDataFile()

                #### SHOULD I WAIT HERE? ####

                # Download the EDF data file from the Host PC to a local data folder
                # parameters: source_file_on_the_host, destination_file_on_local_drive
                # local_edf = os.path.join(sub_dir, '%s.EDF' % expInfo['run'])
                try:
                    # source: edf_file
                    el_tracker.receiveDataFile(sourceEDF, destinationEDF)
                except RuntimeError as error:
                    print('ERROR:', error)


    """
    15. Save data into .TSV formats and Tying up Loose Ends
    """ 
    # Append any constants to the entire run
    bids_data_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, str(runs+1))
    bids_data.to_csv(bids_data_filename, sep="\t")
    bids_data=pd.DataFrame(columns=varNames) # Clear it out for a new file.

    el_tracker.close()


    """
    18. End of Run, Wait for Experimenter instructions to begin next run
    """   
    nextRun(win)
    
"""
19. Wrap up
"""
endScan(win)

"""
End of Experiment
"""