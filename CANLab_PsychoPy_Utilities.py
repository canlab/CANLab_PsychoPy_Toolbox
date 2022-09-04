#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CANLab PsychoPy Utilities 1.0.0
Michael Sun, Ph.D.

"""

# Import Libraries
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

from WASABI_config import *

def subjectInfoBox(name, expInfo=None):
    """Show a dialog box asking for subject information with [OK] and [Cancel] buttons.

    Args:
        name (str): String name of the dialog box being shown. e.g., "Input Brain Study Information".
        expInfo (dict): A dictionary list of keys, indicating the information you want to collect in order. Gives some reasonable defaults if none is supplied.

    Returns:
        dict: The resulting expInfo key-value dictionary for use in the rest of your study, along with a 'date' key and value recording the day in which data is collected.
    """

    if expInfo is None:
        # Some handy defaults
        expInfo = {
            'DBIC Number': '',
            'gender': '',
            'session': '',
            'handedness': '', 
            'scanner': ''
        }
    dlg = gui.DlgFromDict(title=name, dictionary=expInfo, sortKeys=False)

    if dlg.OK == False:
        core.quit()  # user pressed cancel

    expInfo['date'] = data.getDateStr()  # add a simple timestamp

    return expInfo


def setupWindow(res=[1920, 1080], bg=[-1,-1,-1], showMouse=False):
    """Sets up the window object that you will use to flip and display stimuli to your subject.

    Troubleshooting Tips:
        If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
        pip uninstall pyglet
        pip install pyglet==1.4.1

    Args:
        res (list, optional): Input a [width, height] list of one's display resolution. Defaults to [1920, 1080] for full high-definition (FHD), but if debugging, will be [1280, 720] in windowed mode.
        bg (list or keyword string, optional): An [r,g,b] list of the background color. Psychopy keywords for color can also work. Defaults to [-1,-1,-1] for a black screen.
        showMouse (bool, optional): Choose whether or not to keep the mouse visible during the duration of the study. Defaults to False.

    Returns:
        visual.Window object: This is the window object that other scripts will draw stimuli onto.
    """

    if debug == 1: 
        win = visual.Window(
                size=[1280, 720], fullscr=False, 
                screen=0,   # Change this to the appropriate display 
                winType='pyglet', allowGUI=True, allowStencil=False,
                monitor='testMonitor', color=bg, colorSpace='rgb',
                blendMode='avg', useFBO=True, 
                units='height')
    else: 
        win = visual.Window(
                size=res, fullscr=True, 
                screen=-1,   # Change this to the appropriate fMRI projector 
                winType='pyglet', allowGUI=True, allowStencil=False,
                monitor='testMonitor', color=bg, colorSpace='rgb',
                blendMode='avg', useFBO=True, 
                units='height')

    win.mouseVisible = showMouse # Make the mouse invisible for the remainder of the experiment
    return win

def confirmRunStart(win, text=start_msg, TR=0.46):
    """Show a run start message, listen for TRs and return the time the run starts. Sets the global fmriStart time.

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        text (str, optional): The message to display in win. Defaults to whatever is assigned to start_msg in your config.py.
        TR (float, optional): Length of the repetition time for neuroimage acquisition. Defaults to 0.46 seconds.
    """
    
    start = visual.TextStim(win, text=text, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    global fmriStart
    fmriStart=globalClock.getTime()   # Start the clock
    if autorespond != 1:   
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if 's' in event.getKeys(keyList = 's'):         # experimenter start key - safe key before fMRI trigger
                s_confirm = visual.TextStim(win, text=s_text, height =.05, color="green", pos=(0.0, -.3))
                start.draw()
                s_confirm.draw()
                win.flip()
                event.clearEvents()
                while continueRoutine == True:
                    if '5' in event.getKeys(keyList = '5'): # fMRI trigger
                        fmriStart = globalClock.getTime()   # Start the clock
                        timer = core.CountdownTimer()       # Wait 6 TRs, Dummy Scans
                        timer.add(TR*6)
                        while timer.getTime() > 0:
                            continue
                        continueRoutine = False
    return fmriStart


def nextRun(win, advanceKey='e', text=in_between_run_msg, biopacCode=between_run_msg):
    """Show a message prior to beginning the next run.

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        advanceKey (str, optional): Keypress required to end the display of text and advance. Defaults to 'e'. 
        text (str, optional): The message to display in win. Defaults to whatever is assigned to start_msg in your config.py.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.
    """

    message = visual.TextStim(win, text=in_between_run_msg, height=0.05, units='height')
    message.draw()
    win.callOnFlip(print, text)
    if biopac_exists:
        win.callOnFlip(biopac.setData, biopac,0)
        win.callOnFlip(biopac.setData, biopac,biopacCode)
    win.flip()
    # Autoresponder
    if autorespond != 1:
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if advanceKey in event.getKeys(keyList = advanceKey):
                continueRoutine = False
    return

def endScan(win, advanceKey='e', text=end_msg, biopacCode=end_task):
    """Wrapper function for ending the scan.

    Args:
        win (visual.Window): Pass in the Window to draw text to.
        advanceKey (str, optional): Keypress required to end the display of text and advance. Defaults to 'e'. 
        text (str, optional): Text string to display as your end scan message. Defaults to whatever is assigned to end_msg in your config.py.
    """
    showText(win, "EndScan", text, advanceKey=advanceKey, noRecord=True. biopacCode=biopacCode)
    if biopac_exists == 1:
        biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150
    win.close()  # close the window
    core.quit()
    return

def showText(win, name, text, strColor='white', fontSize=.05, strPos=(0, 0), time=None, advanceKey='space', biopacCode=None, noRecord=False):
    """Show some text, press a key to advance or wait a certain amount of time. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional. 
        You're responsible for your own word-wrapping! Use \n or something.

        Warning: Either 'time' or 'advanceKey' should be initialized, or you will be stuck and you need to press ['esc'].

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        name (str): String name of the textblock being shown. e.g., "Instructions".
        text (str): Text string to display to the Window. 
        strColor (list or str, optional): [r,g,b] color list or PsychoPy color keyword string. Defaults to 'white'.
        fontSize (float, optional): Size of the text in PsychoPy height. Defaults to .05% of the screen.
        strPos (tuple, optional): Tuple of (x, y) coordinates of where on the screen the text should appear. Defaults to the middle of the screen at (0, 0).
        time (int, optional): Time to display the stimuli on screen. Defaults to None.
        advanceKey (str, optional): Keypress required to end the display of text and advance. Defaults to 'space'.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Returns:
        dict: The dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """
    ## Intialize the Objects
    TextClock = core.Clock()
    TextKB = keyboard.Keyboard()
    Text = visual.TextStim(win, name='Text', 
        text=text,
        font = 'Arial',
        pos=strPos, height=fontSize, wrapWidth=1.6, ori=0, 
        color=strColor, colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0, 
        anchorHoriz='center')
    
    # ------Prepare to start Routine "Text"-------
    routineTimer.reset()

    if time is not None:
        routineTimer.add(time)

    continueRoutine = True
    # update component parameters for each repeat
    TextKB.keys = []
    TextKB.rt = []
    _TextKB_allKeys = []
    # Update instructions and cues based on current run's body-sites:
  
    # keep track of which components have finished
    TextComponents = [Text, TextKB]

    for thisComponent in TextComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    TextClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Text"-------
    # Record onset time
    if noRecord==False:
        global fmriStart
        onset = globalClock.getTime() - fmriStart 

    while continueRoutine:
        # get current time
        t = TextClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=TextClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *Text* updates
        if Text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Text.frameNStart = frameN  # exact frame index
            Text.tStart = t  # local t and not account for scr refresh
            Text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Text, 'tStartRefresh')  # time at next scr refresh
            Text.setAutoDraw(True)
        if Text.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > Text.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                Text.tStop = t  # not accounting for scr refresh
                Text.frameNStop = frameN  # exact frame index
                win.timeOnFlip(TextKB, 'tStopRefresh')  # time at next scr refresh
                Text.setAutoDraw(False)
        
        # *TextKB* updates
        waitOnFlip = False
        if TextKB.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            TextKB.frameNStart = frameN  # exact frame index
            TextKB.tStart = t  # local t and not account for scr refresh
            TextKB.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(TextKB, 'tStartRefresh')  # time at next scr refresh
            TextKB.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing "+name)
            if biopac_exists == 1 and biopacCode is not None:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            win.callOnFlip(TextKB.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(TextKB.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if TextKB.status == STARTED and not waitOnFlip:
            if advanceKey is not None:
                theseKeys = TextKB.getKeys(keyList=advanceKey, waitRelease=False)
                _TextKB_allKeys.extend(theseKeys)
                if len(_TextKB_allKeys):
                    TextKB.keys = _TextKB_allKeys[-1].name  # just the last key pressed
                    TextKB.rt = _TextKB_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > TextKB.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                TextKB.tStop = t  # not accounting for scr refresh
                TextKB.frameNStop = frameN  # exact frame index
                win.timeOnFlip(TextKB, 'tStopRefresh')  # time at next scr refresh
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _TextKB_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in TextComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Text"-------
    print("Offset " + name)
    if biopac_exists == 1 and biopacCode is not None:
        print("CueOff Channel: " + str(biopacCode))
        biopac.setData(biopac, 0)
    for thisComponent in TextComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "Text" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
        
    # check responses
    if TextKB.keys in ['', [], None]:  # No response was made
        TextKB.keys = None
    
    if noRecord==False:
        bids_trial={'onset': onset,'duration': t,'condition': name, 'biopac_channel': biopacCode}    
        if TextKB.keys != None:  # we had a response
            bids_trial['keys'] = TextKB.keys
            bids_trial['rt']=TextKB.rt
        return bids_trial
    else:
        return

def showImg(win, name, imgPath, imgPos=[0,0], imgSize=(.05, .05), time=None, advanceKey=None, biopacCode=None, noRecord=False):
    """Show an image, press a key to advance or wait a certain amount of time. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional. 
        
       Warning: Either 'time' or 'advanceKey' should be initialized, or you will be stuck and you need to press ['esc'].

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        name (str): String name of the image being shown. e.g., "Instructional Image".
        imgPath (str): String path to the image file.
        imgPos (list, optional): List of [x, y] coordinates of where on the screen the image should appear. Defaults to the middle of the screen, [0,0].
        imgSize (tuple, optional): Tuple (x, y) in Psychopy height for how large the image should be. Defaults to a (.05%, .05%) of the screen image.
        time (int, optional): Time to display the stimuli on screen. Defaults to None.
        advanceKey (str, optional): Keypress required to end the display of text and advance. Defaults to 'space'.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Returns:
        Dict: The Dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """
    ## Intialize the Objects
    ImageClock = core.Clock()
    ImageKB = keyboard.Keyboard()
    Img = visual.ImageStim(
        win=win,
        name=name,
        image=imgPath,
        mask=None,
        ori=0, 
        pos=imgPos, 
        size=imgSize,
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)

    # ------Prepare to start Routine "Image"-------
    routineTimer.reset()
    
    if time is not None:
        routineTimer.add(time)

    continueRoutine = True
    # update component parameters for each repeat
    ImageKB.keys = []
    ImageKB.rt = []
    _ImageKB_allKeys = []
    # Update instructions and cues based on current run's body-sites:
  
    # keep track of which components have finished
    ImageComponents = [Img, ImageKB]

    for thisComponent in ImageComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ImageClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "ImageClock"-------
    # Record onset time
    if noRecord==False:
        global fmriStart
        onset = globalClock.getTime() - fmriStart

    while continueRoutine:
        # get current time
        t = ImageClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ImageClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *Img* updates
        if Img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Img.frameNStart = frameN  # exact frame index
            Img.tStart = t  # local t and not account for scr refresh
            Img.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Img, 'tStartRefresh')  # time at next scr refresh
            Img.setAutoDraw(True)
        
        if Img.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > Img.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                Img.tStop = t  # not accounting for scr refresh
                Img.frameNStop = frameN  # exact frame index
                win.timeOnFlip(Img, 'tStopRefresh')  # time at next scr refresh
                Img.setAutoDraw(False)
        
        # *ImageKB* updates
        waitOnFlip = False
        if ImageKB.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ImageKB.frameNStart = frameN  # exact frame index
            ImageKB.tStart = t  # local t and not account for scr refresh
            ImageKB.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ImageKB, 'tStartRefresh')  # time at next scr refresh
            ImageKB.status == STARTED
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > ImageKB.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                ImageKB.tStop = t  # not accounting for scr refresh
                ImageKB.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ImageKB, 'tStopRefresh')  # time at next scr refresh
                continueRoutine = False
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing "+name)
            if biopac_exists == 1 and biopacCode is not None:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            win.callOnFlip(ImageKB.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(ImageKB.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if ImageKB.status == STARTED and not waitOnFlip:
            if advanceKey is not None:            
                theseKeys = ImageKB.getKeys(keyList=advanceKey, waitRelease=False)
                _ImageKB_allKeys.extend(theseKeys)
                if len(_ImageKB_allKeys):
                    ImageKB.keys = _ImageKB_allKeys[-1].name  # just the last key pressed
                    ImageKB.rt = _ImageKB_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > ImageKB.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                ImageKB.tStop = t  # not accounting for scr refresh
                ImageKB.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ImageKB, 'tStopRefresh')  # time at next scr refresh
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _ImageKB_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in ImageComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Image"-------
    print("Offset " + name)
    if biopac_exists == 1 and biopacCode is not None:
        print("CueOff Channel: " + str(biopacCode))
        biopac.setData(biopac, 0)
    for thisComponent in ImageComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "Image" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()           
    
    # check responses
    if ImageKB.keys in ['', [], None]:  # No response was made
        ImageKB.keys = None
 
    if noRecord==False:
        bids_trial={'onset': onset,'duration': t,'condition': name, 'biopac_channel': biopacCode}    
        if ImageKB.keys != None:  # we had a response
            bids_trial['keys'] = ImageKB.keys
            bids_trial['rt']=ImageKB.rt
        return bids_trial
    else:
        return

def preloadMovie(win, name, movPath):
    """It's recommended that you preload Movies prior to playing them because Initializes and returns the visual.MovieStim3 file. Prepares the movie to be played a single time, in the middle of the screen.

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        name (str): String name of the movie being shown. e.g., "Inscapes".
        movPath (str): String path to the image file.

    Returns:
        visual.MovieStim3: The resulting movie file.
    """
    movie = visual.MovieStim3(
        win=win, name=name,
        noAudio = False,
        filename=movPath,
        ori=0, pos=(0, 0), opacity=1,
        loop=False,
        depth=-1.0
    )
    return movie

def showMovie(win, movie, name=None, biopacCode=None, noRecord=False):
    """Play the movie. It will only play for 10 seconds in debug mode. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional.

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        movie (visual.MovieStim3): Play a preloaded movie.
        name (str): String name of the movie being shown. e.g., "Inscapes".
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Returns:
        dict: The Dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """

    if debug==1:
        movie_duration=10

    if name==None:
        name = movie.name

    MovieClock = core.Clock()
    # ------Prepare to start Routine "Movie"-------
    continueRoutine = True

    movie_duration = movie.duration

    if debug==1:
        movie_duration = 10     # debugging
    routineTimer.reset()
    routineTimer.add(movie_duration)

    # keep track of which components have finished
    MovieComponents = [movie]
    for thisComponent in MovieComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    MovieClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "Movie"-------
    # Record onset time
    if noRecord==False:
        global fmriStart
        onset = globalClock.getTime() - fmriStart
    
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = MovieClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=MovieClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *movie* updates
        if movie.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            movie.frameNStart = frameN  # exact frame index
            movie.tStart = t  # local t and not account for scr refresh
            movie.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
            movie.setAutoDraw(True)
            
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing "+name)
            if biopac_exists == 1 and biopacCode is not None:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
                win.callOnFlip(biopac.setData, biopac, biopacCode)
        # if movie.status == STARTED:  # one frame should pass before updating params and completing
            # updating other components during *movie*
            # movie.setMovie(movieOrder[0]['runseq'][runLoop.thisTrialN+1]['moviefile'])
            if tThisFlipGlobal > movie.tStartRefresh + movie_duration-frameTolerance:
                # keep track of stop time/frame for later
                movie.tStop = t  # not accounting for scr refresh
                movie.frameNStop = frameN  # exact frame index
                win.timeOnFlip(movie, 'tStopRefresh')  # time at next scr refresh
                movie.setAutoDraw(False)
        if movie.status == FINISHED:  # force-end the routine
            continueRoutine = False
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in MovieComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Movie"-------
    movie.stop()
    
    print("Offset " + name)
    if biopac_exists == 1 and biopacCode is not None:
        print("CueOff Channel: " + str(biopacCode))
        biopac.setData(biopac, 0)
    for thisComponent in MovieComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # the Routine "Movie" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    if noRecord==False:
        bids_trial={'onset': onset,'duration': t,'condition': name, 'biopac_channel': biopacCode}    
        return bids_trial
    else:
        return


def showFixation(win, name, type='big', size=None, pos=(0, 0), col='white', time=5, biopacCode=None, noRecord=False):
    """Wrapper function for creating a fixation cross for a a set period. Set the position, size, color, and time to offset. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional.

    Args:
        win (visual.Window): Pass in the Window to draw the fixation cross on to. 
        name (str): name of the fixation cross condition, e.g., "pre-stimulus jitter"
        type (str, optional): 'big' which is size=.05 or 'small' which is size=.01. Defaults to 'big'.
        size (float, optional): Size of the fixation cross in PsychoPy height. Defaults to None.
        pos (tuple, optional): Tuple of (x, y) coordinates of where on the screen the image should appear. Defaults to the middle of the screen, (0,0).
        col (str or list, optional): [r,g,b] color list or PsychoPy color keyword string. Defaults to 'white'.
        time (int, optional): Time to offset. Defaults to 5 seconds.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Returns:
        dict: The Dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """
    
    if size is not None:
        return showText(win, name, '+', strColor=col, fontSize=size, strPos=pos, time=time, advanceKey=None, biopacCode=biopacCode, noRecord=noRecord)
    if type == 'big':
        size = .1
    elif type == 'small':
        size = .05
    return showText(win, name, '+', strColor=col, fontSize=size, strPos=pos, time=time, advanceKey=None, biopacCode=biopacCode, noRecord=noRecord)


def showTextAndImg(win, name, text, imgPath, strColor='white', fontSize=.05, strPos=(0, -.25), imgSize=(.40,.40), imgPos=(0, .2), time=None, advanceKey='space', biopacCode=None, noRecord=False):
    """Show an image with text together, press a key to advance or wait a certain amount of time. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional. 
       You are responsible for your own word-wrapping! Use \n judiciously. 
       Warning: Either 'time' or 'advanceKey' should be initialized, or you will be stuck and you need to press ['esc'].

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        name (str): String name of the condition being shown. e.g., "Image with Instructions".
        text (str): String text to be displayed onscreen.
        imgPath (str): String path to the image file.
        strColor (str, optional): _description_. Defaults to 'white'.
        fontSize (float, optional): _description_. Defaults to .05.
        strPos (tuple, optional): Tuple of (x, y) coordinates of where on the screen the text should appear. Defaults to (0, .5).
        imgSize (tuple, optional): _description_. Defaults to (.40,.40).
        imgPos (tuple, optional): Tuple of (x, y) coordinates of where on the screen the image should appear. Defaults to the middle of the screen, (0,0).
        time (int, optional): Time to display the stimuli on screen in seconds. Defaults to None.
        advanceKey (str, optional): Keypress required to end the display of text and advance. Defaults to 'space'.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Returns:
        dict: The Dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """
    ## Intialize the Objects
    TextImageClock = core.Clock()
    TextImageKB = keyboard.Keyboard()
    Text = visual.TextStim(win, name='Text', 
        text=text,
        font = 'Arial',
        pos=strPos, height=fontSize, wrapWidth=1.6, ori=0, 
        color=strColor, colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0, 
        anchorHoriz='center')
    Img = visual.ImageStim(
        win=win,
        name='Image',
        image=imgPath,
        mask=None,
        ori=0, 
        pos=imgPos, 
        size=imgSize,
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)
    
    # ------Prepare to start Routine "TextImage"-------
    routineTimer.reset()

    if time is not None:
        routineTimer.add(time)

    continueRoutine = True
    # update component parameters for each repeat
    TextImageKB.keys = []
    TextImageKB.rt = []
    _TextImageKB_allKeys = []
    # Update instructions and cues based on current run's body-sites:
  
    # keep track of which components have finished
    TextImageComponents = [Text, Img, TextImageKB]

    for thisComponent in TextImageComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    TextImageClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "TextImage"-------
    # Record onset time
    if noRecord==False:
        global fmriStart
        onset = globalClock.getTime() - fmriStart

    while continueRoutine:
        # get current time
        t = TextImageClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=TextImageClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *Text* updates
        if Text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Text.frameNStart = frameN  # exact frame index
            Text.tStart = t  # local t and not account for scr refresh
            Text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Text, 'tStartRefresh')  # time at next scr refresh
            Text.setAutoDraw(True)
        if Text.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > Text.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                Text.tStop = t  # not accounting for scr refresh
                Text.frameNStop = frameN  # exact frame index
                win.timeOnFlip(TextImageKB, 'tStopRefresh')  # time at next scr refresh
                Text.setAutoDraw(False)

        # *Img* updates
        if Img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Img.frameNStart = frameN  # exact frame index
            Img.tStart = t  # local t and not account for scr refresh
            Img.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Img, 'tStartRefresh')  # time at next scr refresh
            Img.setAutoDraw(True)
        if Img.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > Img.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                Img.tStop = t  # not accounting for scr refresh
                Img.frameNStop = frameN  # exact frame index
                win.timeOnFlip(TextImageKB, 'tStopRefresh')  # time at next scr refresh
                Img.setAutoDraw(False)
        
        # *TextImageKB* updates
        waitOnFlip = False
        if TextImageKB.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            TextImageKB.frameNStart = frameN  # exact frame index
            TextImageKB.tStart = t  # local t and not account for scr refresh
            TextImageKB.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(TextImageKB, 'tStartRefresh')  # time at next scr refresh
            TextImageKB.status = STARTED

            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing "+name)
            if biopac_exists == 1 and biopacCode is not None:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            win.callOnFlip(TextImageKB.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(TextImageKB.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if TextImageKB.status == STARTED and not waitOnFlip:
            if advanceKey is not None:
                theseKeys = TextImageKB.getKeys(keyList=advanceKey, waitRelease=False)
                _TextImageKB_allKeys.extend(theseKeys)
                if len(_TextImageKB_allKeys):
                    TextImageKB.keys = _TextImageKB_allKeys[-1].name  # just the last key pressed
                    TextImageKB.rt = _TextImageKB_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False
            # is it time to stop? (based on global clock, using actual start)
            if time is not None and tThisFlipGlobal > TextImageKB.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                TextImageKB.tStop = t  # not accounting for scr refresh
                TextImageKB.frameNStop = frameN  # exact frame index
                win.timeOnFlip(TextImageKB, 'tStopRefresh')  # time at next scr refresh
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _TextImageKB_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in TextImageComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "TextImage"-------
    print("Offset " + name)
    if biopac_exists == 1 and biopacCode is not None:
        print("CueOff Channel: " + str(biopacCode))
        biopac.setData(biopac, 0)
    for thisComponent in TextImageComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)

    if noRecord==False:
        bids_trial={'onset': onset,'duration': t,'condition': name}        
    
    # check responses
    if TextImageKB.keys in ['', [], None]:  # No response was made
        TextImageKB.keys = None
    
    if noRecord==False:
        bids_trial={'onset': onset,'duration': t,'condition': name, 'biopac_channel': biopacCode}    
        if TextImageKB.keys != None:  # we had a response
            bids_trial['keys'] = TextImageKB.keys
            bids_trial['rt']=TextImageKB.rt
        return bids_trial
    else:
        return

# Initialize components for each Rating
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
ratingScaleWidth=1.5
ratingScaleHeight=.4
sliderMin = -.75
sliderMax = .75
bipolar_verts = [(sliderMin, .2),    # left point
                        (sliderMax, .2),    # right point
                        (0, -.2)]           # bottom-point
unipolar_verts = [(sliderMin, .2), # left point
            (sliderMax, .2),     # right point
            (sliderMin, -.2)]   # bottom-point, # bottom-point

def showRatingScale(win, name, questionText, imgPath, type="bipolar", time=5, biopacCode=None, noRecord=False):
    """Show a binary, unipolar, or bipolar rating scale, mouseclick to submit response or wait a certain amount of time. By default returns the onset and timings as a dictionary to be concatenated to your BIDS datafile, but this is optional. 
       You are responsible for your own word-wrapping! Use \n judiciously. 
       Warning: Either 'time' or 'advanceKey' should be initialized, or you will be stuck and you need to press ['esc'].

    Args:
        win (visual.Window): Pass in the Window to draw text to. 
        name (str): String name of the condition being shown. e.g., "Heat Intensity Rating".
        questionText (str): String text to be displayed onscreen.
        imgPath (str): String path to the image file.
        type (str, optional): Select type of of rating scale: 'binary', 'unipolar', or 'bipolar'. Defaults to "bipolar".
        time (int, optional): Time to display the rating scale on screen in seconds. Defaults to 5 seconds.
        biopacCode (int, optional): Integer representing the 8-bit digital channel to toggle for biopac Acqknowledge Software. Defaults to None.
        noRecord (bool, optional): Don't return the Dictionary of onset and duration. Defaults to False.

    Raises:
        Exception: Type exception if string type specified is not 'binary', 'unipolar', or 'bipolar'.

    Returns:
        dict: The Dictionary of onset, duration, and condition to be concatenated into your BIDS datafile.
    """
    if type not in ["binary", "unipolar", "bipolar"]:
        raise Exception("Specified an invalid rating type. Please specify type = 'binary', 'unipolar', or 'bipolar' as a string")

    # Initialize components for Routine "Rating"
    RatingClock = core.Clock()
    RatingMouse = event.Mouse(win=win)
    RatingMouse.mouseClock = core.Clock()
    Rating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
    
    if type is not "binary":
        BlackTriangle = visual.ShapeStim(
            win,
            fillColor='black', lineColor='black')
        if type=="unipolar":
            BlackTriangle.vertices=unipolar_verts
        if type=="bipolar":
            BlackTriangle.vertices=bipolar_verts

    RatingAnchors = visual.ImageStim(
        win=win,
        image= imgPath,
        name=name+'Anchors', 
        mask=None,
        ori=0, pos=(0, -0.09), size=(1.5, .4),
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)
    if type=='binary':
        RatingAnchors.size=(1, .25)

    RatingPrompt = visual.TextStim(win, name=name, 
        text=questionText,
        font = 'Arial',
        pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
        color='white', colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0,
        anchorHoriz='center')

    # ------Prepare to start Routine "Rating"-------
    continueRoutine = True
    routineTimer.add(time)
    # update component parameters for each repeat
    # keep track of which components have finished
    RatingMouse = event.Mouse(win=win, visible=False) # Re-initialize RatingMouse
    RatingMouse.setPos((0,0))
    timeAtLastInterval = 0
    mouseX = 0
    oldMouseX = 0

    if type in ["binary", "bipolar"]:
        Rating.width = 0
        Rating.pos = (0,0)
    if type=="unipolar":
        Rating.width = abs(sliderMin)
        Rating.pos = [sliderMin/2, -.1]

    if type is not 'binary':
        RatingComponents = [RatingMouse, BlackTriangle, Rating, RatingAnchors, RatingPrompt]
    else:
        RatingComponents = [RatingMouse, Rating, RatingAnchors, RatingPrompt]
    
    for thisComponent in RatingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    RatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Rating"-------
    # Record onset time
    if noRecord==False:
        global fmriStart
        onset = globalClock.getTime() - fmriStart

    while continueRoutine:

        timeNow = globalClock.getTime()
        if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
            mouseRel=RatingMouse.getRel()
            mouseX=oldMouseX + mouseRel[0]

        if type == "binary":
            if mouseX==0:
                sliderValue=0
                Rating.width = 0
            else:
                if mouseX>0:
                    Rating.pos = (.28,0)
                    sliderValue=1
                elif mouseX<0:
                    Rating.pos = (-.4,0)
                    sliderValue=-1
                Rating.width = .5
        if type == "unipolar":
            Rating.pos = ((sliderMin + mouseX)/2,0)
            Rating.width = abs((mouseX-sliderMin))
        if type == "bipolar":
            Rating.pos = (mouseX/2,0)
            Rating.width = abs(mouseX)
        if type in ["unipolar", "bipolar"]:
            if mouseX > sliderMax:
                mouseX = sliderMax
            if mouseX < sliderMin:
                mouseX = sliderMin

        timeAtLastInterval = timeNow
        oldMouseX=mouseX

        if type=="unipolar":
            sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100
        if type=="bipolar":
            sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

        # get current time
        t = RatingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=RatingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *RatingMouse* updates
        if RatingMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            RatingMouse.frameNStart = frameN  # exact frame index
            RatingMouse.tStart = t  # local t and not account for scr refresh
            RatingMouse.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(RatingMouse, 'tStartRefresh')  # time at next scr refresh
            RatingMouse.status = STARTED
            RatingMouse.mouseClock.reset()
            prevButtonState = RatingMouse.getPressed()  # if button is down already this ISN'T a new click
        if RatingMouse.status == STARTED:  # only update if started and not finished!
            if tThisFlipGlobal > RatingMouse.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                RatingMouse.tStop = t  # not accounting for scr refresh
                RatingMouse.frameNStop = frameN  # exact frame index
                RatingMouse.status = FINISHED
            buttons = RatingMouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:  # state changed to a new click
                    # abort routine on response
                    continueRoutine = False
        
        # *Rating* updates
        if Rating.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Rating.frameNStart = frameN  # exact frame index
            Rating.tStart = t  # local t and not account for scr refresh
            Rating.tStartRefresh = tThisFlipGlobal  # on global time
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing "+name)
            if biopac_exists == 1 and biopacCode is not None:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            win.timeOnFlip(Rating, 'tStartRefresh')  # time at next scr refresh
            Rating.setAutoDraw(True)
        if Rating.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > Rating.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                Rating.tStop = t  # not accounting for scr refresh
                Rating.frameNStop = frameN  # exact frame index
                win.timeOnFlip(Rating, 'tStopRefresh')  # time at next scr refresh
                Rating.setAutoDraw(False)
        
        if type is not 'binary':
            # *BlackTriangle* updates
            if BlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                BlackTriangle.frameNStart = frameN  # exact frame index
                BlackTriangle.tStart = t  # local t and not account for scr refresh
                BlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(BlackTriangle, 'tStartRefresh')  # time at next scr refresh
                BlackTriangle.setAutoDraw(True)
            if BlackTriangle.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > BlackTriangle.tStartRefresh + time-frameTolerance:
                    # keep track of stop time/frame for later
                    BlackTriangle.tStop = t  # not accounting for scr refresh
                    BlackTriangle.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(BlackTriangle, 'tStopRefresh')  # time at next scr refresh
                    BlackTriangle.setAutoDraw(False)
        
        # *RatingAnchors* updates
        if RatingAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            RatingAnchors.frameNStart = frameN  # exact frame index
            RatingAnchors.tStart = t  # local t and not account for scr refresh
            RatingAnchors.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(RatingAnchors, 'tStartRefresh')  # time at next scr refresh
            RatingAnchors.setAutoDraw(True)
        if RatingAnchors.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > RatingAnchors.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                RatingAnchors.tStop = t  # not accounting for scr refresh
                RatingAnchors.frameNStop = frameN  # exact frame index
                win.timeOnFlip(RatingAnchors, 'tStopRefresh')  # time at next scr refresh
                RatingAnchors.setAutoDraw(False)
        
        # *RatingPrompt* updates
        if RatingPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            RatingPrompt.frameNStart = frameN  # exact frame index
            RatingPrompt.tStart = t  # local t and not account for scr refresh
            RatingPrompt.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(RatingPrompt, 'tStartRefresh')  # time at next scr refresh
            RatingPrompt.setAutoDraw(True)
        if RatingPrompt.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > RatingPrompt.tStartRefresh + time-frameTolerance:
                # keep track of stop time/frame for later
                RatingPrompt.tStop = t  # not accounting for scr refresh
                RatingPrompt.frameNStop = frameN  # exact frame index
                win.timeOnFlip(RatingPrompt, 'tStopRefresh')  # time at next scr refresh
                RatingPrompt.setAutoDraw(False)

        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            if type=='binary':
                sliderValue = random.randint(-1,1)
            if type=='unipolar':
                sliderValue = random.randint(0,100)
            if type=='bipolar':
                sliderValue = random.randint(-100,100)
            continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in RatingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:
            win.flip()

    # -------Ending Routine "Rating"-------
    print("Offset " + name)
    if biopac_exists == 1 and biopacCode is not None:
        print("CueOff Channel: " + str(biopacCode))
        biopac.setData(biopac, 0)

    for thisComponent in RatingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)

    # the Routine "Rating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    if noRecord==False:
        bids_trial={'onset': onset,'duration': globalClock.getTime(),'condition': name, 'value': sliderValue, 'rt': timeNow - Rating.tStart} 
        return bids_trial
    else:
        return