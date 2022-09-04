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

# The critical imports:
from CANLab_PsychoPy_Utilities import *
from CANlab_PsychoPy_Config import *

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

# If Preloading Movie, this is where it could go
movie=preloadMovie(win, "inscapes-movie", "path-to-movie.mov")

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

"""
6. Welcome Instructions
"""
showText(win, "Instructions", InstructionText, noRecord=True)

for runs in range(totalRuns):
    ## Here's an example of how you might delineate a multi-condition study.
    if runs in [0,1]:
        ConditionName="First-Half"
        temperature='48'
    if runs in [2,3]:
        ConditionName="Second-Half"
        temperature='45'
        
    thermodeCommand=thermode_temp2program[temperature]

    """
    7. Start Scanner
    """
    fmriStart=confirmRunStart(win)

    """
    8. Start Trial Loop
    """
    for r in range(totalTrials): # 16 repetitions
        """
        11. Show Heat Cue
        """
        # Try to s elect Medoc Thermal Program
        if thermode_exists == 1:
            sendCommand('select_tp', thermodeCommand)

        # Need a biopac code
        bids_data=bids_data.append(showImg(win, "Cue", imgPath=cueImg, time=2, biopacCode=cue, ignore_index=True))

        """ 
        9. Pre-Heat Fixation Cross
        """
        jitter1 = random.choice([4, 6, 8])
        if debug==1:
            jitter1=1

        bids_data=bids_data.append(showFixation(win, "Pre-Jitter", time=jitter1, biopacCode=prefixation), ignore_index=True)

        """ 
        10. Heat-Trial Fixation Cross
        """
        if thermode_exists == 1:
            sendCommand('trigger') # Trigger the thermode
        bids_data=bids_data.append(showFixation(win, "Heat "+temperature, time=stimtrialTime, biopacCode=heat), ignore_index=True)

        """
        11. Post-Heat Fixation Cross
        """
        if debug==1:
            jitter2=1
        else:
            jitter2 = random.choice([5,7,9])
        bids_data=bids_data.append(showFixation(win, "Mid-Jitter", time=jitter2, biopacCode=midfixation), ignore_index=True)

        """
        12. Begin post-trial self-report questions
        """        
        rating_sound.play() # Alert participants to make ratings.
        bids_data=bids_data.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
        bids_data=bids_data.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)

        """
        13. Post-Question jitter
        """
        if debug==1:
            jitter3=1
        else:
            jitter3 = random.choice([5,7,9])
        bids_data=bids_data.append(showFixation(win, "Post-Q-Jitter", time=jitter2, biopacCode=postfixation), ignore_index=True)

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

    """
    15. Save data into .TSV formats and Tying up Loose Ends
    """ 
    # Append any constants to the entire run
    bids_data['phase']=ConditionName
    bids_data['temperature']=temperature
    bids_data_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
    bids_data.to_csv(bids_data_filename, sep="\t")
    bids_data=pd.DataFrame(columns=varNames) # Clear it out for a new file.

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