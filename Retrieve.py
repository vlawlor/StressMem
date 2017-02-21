# Last updated: Feburary 21, 2017
# Authors: Victoria Lawlor, Elyssa Barrick, and Dan Dillon
# Runs retrieval for the StressMem experiment.

# User, you may need/want to edit the next several lines
import csv, getpass, os, random, sys, glob
userName = getpass.getuser()
monitorName = 'MLM Mac'

path2words = '/Users/' + userName + '/Work/Expts/StressMem/PsychoPy/Stimuli/'
path2data = '/Users/' + userName + '/Work/Expts/StressMem/Data/'

# Shouldn't need to edit below . . . 
import numpy as np
import pandas as pd
import random, sys
import os.path
from random import shuffle
from psychopy import prefs
from copy import deepcopy
prefs.general['audioLib'] = ['pygame']
from psychopy import sound
from psychopy import core, data, event, gui, misc, visual

print (pd.__version__)
print (sys.version)
print (sys.path)

# GUI for subject number and date
try:
    expInfo = misc.fromFile('StressTasklastParams.pickle')
except:
    expInfo = {'SubjectID':'999' }

expInfo['Date'] = data.getDateStr()
expInfo['Session'] = 0

dlg = gui.DlgFromDict(expInfo, title='StressMem', fixed=['Date'])
if dlg.OK:
    misc.toFile('StressMemlastParams.pickle', expInfo) 
else:
    core.quit()
subject = expInfo['SubjectID']
session = expInfo['Session']

if  session != 1 and session != 2: # needs a 1 or 2 for session to show the correct word lists, don't want them to go all the way
    myDlg = gui.Dlg(title="Invalid session number") # through the practice before we realize
    myDlg.addText('Invalid session number. Please enter 1 or 2.')
    ok_data = myDlg.show()
    if myDlg.OK:
        core.quit()
    else:
        core.quit()

# Refresh rate
refresh = 16.7
fps = int(np.ceil(1000/refresh)) # fps = flips per second; done this way in case refresh rate changes
half_sec = int(0.5*fps)

# Window
wintype='pyglet'
win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = monitorName, color = '#FFFFFA', winType=wintype, units = 'norm')

# Buttons
key_1 = 'c'
key_2 = 'v'
key_3 = 'b'
key_4 = 'n'
key_5 = 'm'
key_6 = 'comma'
pause_key = 'p' # Advance screen following EEG net placement and QC; we don't use this yet
quit_key = 'q' 

# WORDS--this section needs some work.. 
if session == 1:
    # read in ALL of the words, and turn into a dict of dicts
    df_all = pd.read_csv(path2words + 'balanced_words.csv')
    df_all = df_all.reset_index(drop = True)
    all_d = df_all.T.to_dict()

    # read in the encoding data, then turn it into a dict of dicts
    encoded = glob.glob(path2data + subject + '*_StressMem_enc.csv')
    df_encoded = pd.read_csv(encoded[0])
    df_encoded = df_encoded.loc[df_encoded['block'] == 1]
    df_encoded = df_encoded.reset_index(drop = True)
    encoded_d = df_encoded.T.to_dict()

    # iterate through the full list and remove the word if it was shown at encoding, leaving us with the set of new words.
    copy_all_item = deepcopy(all_d)
    for key, enc_item in encoded_d.iteritems():
        for key, all_item in copy_all_item.iteritems():
            if all_item['word'] == enc_item['word']:
                print(all_item['word']) #just a check 
                all_d.pop(key)

    # assigning old/new status
    for item in all_d.iteritems():
        item[1]['status'] = 'new'
    for item in encoded_d.iteritems():
        item[1]['status'] = 'old'

    # setting the values for the new items
    list = ['RT', 'block', 'iti_duration', 'options_duration', 'options_onset', 'response', 'options_onset', 'subject', 'task', 'task_duration', 
           'task_onset', 'trial', 'word_duration', 'word_onset']
    for item in all_d.iteritems():
        for value in list:
            item[1][value] = np.nan
        
    # shuffling the new dictionaries and splitting the new words into the two blocks
    keys = all_d.keys()
    random.shuffle(keys)
    pos_ct = 0
    new_b1 = {}
    neg_ct = 0
    new_b2 = {}
    for key in keys:
        if all_d[key]['valence'] == 1:
            if pos_ct < 25:
                new_b1[pos_ct] = all_d[key]
                pos_ct = pos_ct + 1 
            else:
                new_b2[pos_ct] = all_d[key]
                pos_ct = pos_ct + 1
        else:
            if neg_ct < 25:
                new_b1[neg_ct] = all_d[key]
                neg_ct = neg_ct + 1
            else:
                new_b2[neg_ct] = all_d[key]
                neg_ct = neg_ct + 1

    # splitting the encoded words into the two blocks based on valence and task
    dist = random.random()
    if random.random() > .05:
        pos_disc = 13
        neg_disc = 12
    else:
        pos_disc = 12
        neg_disc = 13    
    pos_describes_ct = 0
    pos_emotion_ct = 0
    pos_ct = 0
    pos_enc_b1 = {}
    pos_enc_b2 = {}
    neg_describes_ct = 0
    neg_emotion_ct = 0
    neg_ct = 0
    neg_enc_b1 = {}
    neg_enc_b2 = {}

    keys = encoded_d.keys()
    random.shuffle(keys)
    for key in keys:
        if encoded_d[key]['valence'] == 0:
            if pos_describes_ct < pos_disc and encoded_d[key]['task'] == 'Describes':
                pos_enc_b1[pos_ct] = encoded_d[key]
                pos_describes_ct = pos_describes_ct + 1
                pos_ct = pos_ct + 1
            elif pos_emotion_ct < neg_disc and encoded_d[key]['task'] == 'Positive':
                pos_enc_b1[pos_ct] = encoded_d[key]
                pos_emotion_ct = pos_emotion_ct + 1
                pos_ct = pos_ct + 1     
            else:
                pos_enc_b2[pos_ct] = encoded_d[key]
                pos_ct = pos_ct + 1
        else:
            if neg_describes_ct < neg_disc and encoded_d[key]['task'] == 'Describes':
                neg_enc_b1[neg_ct] = encoded_d[key]
                neg_describes_ct = neg_describes_ct + 1
                neg_ct = neg_ct + 1
            elif neg_emotion_ct < pos_disc and encoded_d[key]['task'] == 'Positive':
                neg_enc_b1[neg_ct] = encoded_d[key]
                neg_emotion_ct = neg_emotion_ct + 1
                neg_ct = neg_ct + 1     
            else:
                neg_enc_b2[neg_ct] = encoded_d[key]
                neg_ct = neg_ct + 1

    # combine these
    session_1_lists = neg_enc_b1.values() + pos_enc_b1.values() + new_b1.values()
    random.shuffle(session_1_lists)
    random.shuffle(session_1_lists)
    random.shuffle(session_1_lists)
    random.shuffle(session_1_lists)
    random.shuffle(session_1_lists)
    random.shuffle(session_1_lists)
    session_2_lists = neg_enc_b2.values() + pos_enc_b2.values() + new_b2.values()
    random.shuffle(session_2_lists)
    random.shuffle(session_2_lists)
    random.shuffle(session_2_lists)
    random.shuffle(session_2_lists)
    random.shuffle(session_2_lists)
    np.save(subject + '_session_2_list.npy',session_2_lists)

elif session == 2:
    session_2_lists = np.load(subject + '_session_2_list.npy')
    #df_session_2 = pd.read_csv(path2words + 'Session_2_Words/' + subject + '_session_2_words.csv')
    #session_2_lists = df_session_2.T.to_dict().values() # turn them into lists of dicts
    #random.shuffle(session_2_lists)

# Recurring stimuli
word = visual.TextStim(win, text='XXXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')
choice = visual.TextStim(win, text = '__', font='Arial', height = 0.10, pos = (0,0), wrapWidth = 50, color = '#ff7a5b', bold=True)
no_resp = visual.TextStim(win, text='NO RESPONSE', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = 'black')

fix = visual.TextStim(win, text = '+', height = 0.10, pos = (0,.15), color = 'black')
instruct = visual.TextStim(win, text = 'XXXX', height = 0.10, wrapWidth = 80, pos = (0,0), color = '#1B1C96')

old_new_prompt = visual.TextStim(win, text='Old or New?', font='Arial', height = 0.20, pos = (0,0.3), wrapWidth = 50, color = '#ff7a5b')
task_prompt = visual.TextStim(win, text='Question?', font='Arial', height = 0.20, pos = (0,0.3), wrapWidth = 50, color = 'MediumTurquoise')
#respond = visual.TextStim(win, text='RESPOND', font='Arial', height = 0.20, pos = (0,0.2), wrapWidth = 50, color = '#ff7a5b')

scale = visual.TextStim(win, text='  1           2           3           4           5           6  ', height = 0.10, pos = (0,-0.25), wrapWidth = 50, color = 'black')
scale_labels = visual.TextStim(win, text='Sure   Probably  Maybe   Maybe  Probably   Sure', height = 0.10, pos = (0,-0.4), wrapWidth = 50, color = '#1B1C96')

old_new_scale = visual.TextStim(win, text='Old                             New', height = 0.17, pos = (0,-0.62), wrapWidth = 50, color = '#ff7a5b')
task_scale = visual.TextStim(win, text='Describes                            Positive', height = 0.17, pos = (0,-0.62), wrapWidth = 50, color = '#1B1C96')

key_sound = sound.SoundPygame('resp.wav')
stim_sound = sound.SoundPygame('stim.wav')
no_resp_sound = sound.SoundPygame('C')

# Clocks
RT = core.Clock()
exp_clock = core.Clock()

# Functions
def show_instruct(instruct_list, adv_key=key_1, quit=quit_key):
    '''Print instructions onscreen and wait for key press'''
    event.clearEvents()
    allKeys = []
    advance = 'false'

    for instructions in instruct_list:
        advance = 'false'
        instruct.setText(text=instructions)
        while advance == 'false':
            instruct.draw()
            win.flip()
            allKeys = event.getKeys(keyList=[adv_key,quit])

            if allKeys:
                    resp = allKeys[0][0]
                    if resp == adv_key:
                        advance = 'true'
                    elif resp == quit_key:
                        core.quit()

def show_ITI():
    '''Display fixation ITI for 500, 1000, or 2000 ms, with 500 ms over-represented'''
    iti_durs = [half_sec, half_sec, fps, 2*fps]
    duration = random.choice(iti_durs)

    for frames in range(duration):
        fix.draw()
        win.flip()

    return duration*refresh

def show_no_resp():
    '''Show the text "no response"'''
    for frames in range(3*fps):
        no_resp.draw()
        win.flip()

def show_respond(r_dict,phase='experiment'):
    '''Elicit response during retrieval'''
    response = np.nan
    curr_RT = np.nan
    advance='false'
    event.clearEvents()
    curr_item = r_dict['word']
    status = r_dict['status']
    task = r_dict['task']
    frame = 0
    if phase == 'practice':
        mean_valence = mean_arousal = valence = letters = frequency = concreteness = part_of_speech = imageability = enc_response = enc_RT = task = np.nan
    else:
        mean_valence = r_dict['mean_valence']
        mean_arousal = r_dict['mean_arousal']
        valence = r_dict['valence']
        letters = r_dict['letters']
        frequency = r_dict['frequency']
        concreteness = r_dict['concreteness']
        part_of_speech = r_dict['part_of_speech']
        imageability = r_dict['imageability']
        enc_response = r_dict['response']
        enc_RT = r_dict['RT']
    word.setColor(color = '#1B1C96')
    word.setText(text = curr_item)
    
    old_new_onset = exp_clock.getTime()
    for frames in range(fps): # show the prompt for one second
        fix.draw()
        old_new_prompt.draw()
        win.flip()
    old_new_offset = exp_clock.getTime()
    old_new_duration = old_new_offset - old_new_onset
    
    ret_stim_onset = exp_clock.getTime()
    for frames in range(3*fps): # show the prompt & word for three seconds
        fix.draw()
        old_new_prompt.draw()
        word.draw()
        win.flip()
    ret_stim_offset = exp_clock.getTime()
    ret_stim_duration = ret_stim_offset - ret_stim_onset

    ret_options_onset = exp_clock.getTime()
    RT.reset()
    retKeys = []
    event.clearEvents()
    while frame < (10*fps) and advance == 'false':
        retKeys = event.getKeys(keyList=[key_1,key_2,key_3,key_4,key_5,key_6,quit_key],timeStamped=RT)
        fix.draw()
        word.draw()
        old_new_prompt.draw()
        scale.draw()
        scale_labels.draw()
        old_new_scale.draw()
        win.flip()
        frame = frame + 1

        if retKeys:
            ret_resp = retKeys[0][0]
            curr_RT = retKeys[0][1]
            choice.setText(text = '__')
            choice.setColor('#11A08E')

            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.72,-0.2))
                response = 1
            elif ret_resp == key_2:
                choice.setPos(newPos=(-0.425,-0.2))
                response = 2
            elif ret_resp == key_3:
                choice.setPos(newPos=(-0.14,-0.2))
                response = 3
            elif ret_resp == key_4:
                choice.setPos(newPos=(0.14,-0.2))
                response = 4
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.425,-0.2))
                response = 5
            elif ret_resp == key_6:
                choice.setPos(newPos=(0.72, -.2))
                response = 6
            for frame in range(half_sec): # Show the choice onscreen for 500 ms
                fix.draw()
                word.draw()
                scale.draw()
                old_new_prompt.draw()
                scale_labels.draw()
                old_new_scale.draw()
                choice.draw()
                win.flip()

            for frame in range(fps): # Add 1000 ms fixation before the ITI, to regain fixation between trials.
                fix.draw()
                win.flip()
            advance = 'true'
    ret_options_offset = exp_clock.getTime()
    ret_options_duration = ret_options_offset - ret_options_onset
    return (phase, curr_item, task, enc_response, enc_RT, valence, letters, frequency, concreteness, part_of_speech, imageability, status, response, curr_RT, 
            old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration)

def show_task_respond(r_dict, phase = 'experiment'):
    '''Elicit response for task'''
    curr_item = r_dict['word']
    status = r_dict['status']
    task = r_dict['task']
    response = np.nan
    curr_RT = np.nan
    advance='false'
    frame = 0
    if phase == 'practice':
        mean_valence = mean_arousal = valence = letters = frequency = concreteness = part_of_speech = imageability = enc_response = enc_RT = np.nan
    else:
        mean_valence = r_dict['mean_valence']
        mean_arousal = r_dict['mean_arousal']
        valence = r_dict['valence']
        letters = r_dict['letters']
        frequency = r_dict['frequency']
        concreteness = r_dict['concreteness']
        part_of_speech = r_dict['part_of_speech']
        imageability = r_dict['imageability']
        enc_response = r_dict['response']
        enc_RT = r_dict['RT']

    word.setColor(color = 'DarkSlateGrey')
    word.setText(text = curr_item)
    
    task_onset = exp_clock.getTime()
    for frames in range(fps): # show the prompt for one second
        fix.draw()
        task_prompt.draw()
        win.flip()
    task_offset = exp_clock.getTime()
    task_duration = task_offset - task_onset
    
    task_prompt_onset = exp_clock.getTime()
    for frames in range(3*fps): # show the prompt & word for three seconds
        fix.draw()
        task_prompt.draw()
        word.draw()
        win.flip()
    task_prompt_offset = exp_clock.getTime()
    task_prompt_duration = task_prompt_offset - task_prompt_onset
    
    task_options_onset = exp_clock.getTime()
    event.clearEvents()
    RT.reset()
    retKeys = []
    while frame < (10*fps) and advance == 'false':
        retKeys = event.getKeys(keyList=[key_1,key_2,key_3,key_4,key_5,key_6,quit_key],timeStamped=RT)
        fix.draw()
        word.draw()
        scale.draw()
        scale_labels.draw()
        task_scale.draw()
        task_prompt.draw()
        win.flip()
        frame = frame + 1

        if retKeys:
            ret_resp = retKeys[0][0]
            curr_RT = retKeys[0][1]
            choice.setText(text = '__')
            choice.setColor('#11A08E')

            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.72,-0.2))
                response = 1
            elif ret_resp == key_2:
                choice.setPos(newPos=(-0.425,-0.2))
                response = 2
            elif ret_resp == key_3:
                choice.setPos(newPos=(-0.14,-0.2))
                response = 3
            elif ret_resp == key_4:
                choice.setPos(newPos=(0.14,-0.2))
                response = 4
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.425,-0.2))
                response = 5
            elif ret_resp == key_6:
                choice.setPos(newPos=(0.72, -.2))
                response = 6
            for frame in range(half_sec): # Show the choice onscreen for 500 ms
                fix.draw()
                word.draw()
                task_prompt.draw()
                scale.draw()
                scale_labels.draw()
                task_scale.draw()
                choice.draw()
                win.flip()
            for frame in range(fps): # Add 1000 ms fixation before the ITI, to regain fixation between trials.
                fix.draw()
                win.flip()
            advance = 'true'
    task_options_offset = exp_clock.getTime()
    task_options_duration = task_options_offset - task_options_onset
    return (response, curr_RT, task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration)

# INSTRUCTIONS
r_instructions = ['Welcome! Today we will be testing your memory. \n\nPress 1 to advance.',
'We will show you all of the words \nyou saw yesterday. \n\nSince you have seen them before, \nthey are considered "OLD."\n\nPress 1 to advance.',
'We will mix them up with words \nyou have not seen before. \n\nSince you have not seen them before,\nthey are considered "NEW".\n\nPress 1 to advance.',
'When you see the "Old or New" prompt, try\nto remember:\n\nDid you see the word yesterday?\n\nPress 1 to advance.',
'The prompts will appear above a cross,\nand the words will appear below the cross.\n\nTry to keep your eyes on the cross, to\nlimit extra eye movement.'
'\n\nPress 1 to advance.',
'After 3.5 seconds, another screen \nwill come up that says "RESPOND." \n\nThis is where you will choose \n"OLD" or "NEW." \n\nPress 1 to advance.',
'If you select "OLD," a new screen will come up \
\nwith the prompt "QUESTION" above a cross,\nand the word shown again below the cross.\
\n\nWhen you see this prompt, try to remember: \n\nWhich question was asked about this word yesterday?\n\nPress 1 to advance.',
'After 3.5 seconds, another screen \nwill come up that says "RESPOND." \n\nThis is where you will choose \nwhich question you answered\nfor that word yesterday:\n\n"Emotion?" or "Describes you?" \
\n\nPress 1 to advance.',
'Does this make sense to you?\n\nIf you have any questions, please ask now.\n\nOtherwise, press 1 to advance.',
'Please try your best.\n\nWe will record your brain activity\nas you try to remember.\n\nThe ideal time to blink is when\nyou are responding.\
\n\nPress 1 to advance.',
'Any questions? If so, please ask now.\n\nWe are going to do practice trials\nbefore we start the experiment.\n\nWhen you are ready, press 1 to start.']

post_prac_instructions = ['You have finished the practice trials.\n\nDo you have any questions?\nIf so, please ask now.\n\nWhen you are ready,\npress 1 to advance.',
'We are ready to begin the 1st block.\n\nIt will be identical to the practice study,\nbut you will see 50 words rather than 4.\n\nWhen you are ready to begin, press 1.']

time2_instructions = ['We are ready to begin the second block of trials.\n\nDo you have any questions? If so, please ask now.\n\nWhen you are ready, press 1 to advance.',
'The second block will be identical to the first block.\n\nWhen you are ready to begin press 1.']

end_instruct = ['Great job! You have finished this portion of the task.\n\nPlease wait for the experimenter.']

if session == 1:
    show_instruct(r_instructions)
    # Start with 5 seconds of fixation to let the person settle in
    for frame in range(10*half_sec):
        fix.draw()
        win.flip()
    ret_file = path2data + subject + '_StressMem_Retrieval_Session1_' + expInfo['Date']
    ret_file = open(ret_file + '.csv', 'w')
    ret_file.write('subject,phase,session,trial,item,enc_task,enc_response,enc_RT,valence,letters,frequency,concreteness,part_of_speech,imageability,status,recog_resp,recog_rt,old_new_onset,old_new_duration,ret_stim_onset,ret_stim_duration,ret_options_onset,ret_options_duration,task_resp,task_rt,task_onset,task_duration,task_prompt_onset,task_prompt_duration,task_options_onset,task_options_duration,iti_durs\n') 
    
    # Practice trials
    r_prac = [{'word': 'faker', 'status':'old', 'task':'emotion', 'prompt' :'Old or New?', 'valence': 'prac'}, {'word' : 'grateful', 'status':'new','task':'','prompt' : 'Old or New?', 'valence': 'prac'}, {'word' : 'generous', 'status': 'old', 'valence': 'prac', 'task':'emotion','prompt' : 'Old or New?'}, 
    {'word' : 'clingy', 'status':'new', 'task':'','prompt' : 'Old or New?', 'valence': 'prac'}]
    
    for frame in range(2*fps): # Warm-up fixation
        fix.draw()
        win.flip()

    for r_dict in r_prac:
        #print (show_respond(r_dict, phase = 'practice'))
        phase, item, enc_task, enc_response, enc_RT, valence, letters, frequency, concreteness, part_of_speech, imageability, status, recog_resp, recog_rt, old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration = show_respond(r_dict, phase = 'practice')
        if recog_resp == 1 or recog_resp == 2:
            task_resp, task_rt, task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration = show_task_respond(r_dict, phase = 'practice')
            if np.isnan(task_resp):
                show_no_resp()
        elif np.isnan(recog_resp):
            show_no_resp()
        else:
            task_resp = np.nan
            task_rt = np.nan
            task_onset = np.nan
            task_duration = np.nan
            task_prompt_onset = np.nan
            task_prompt_duration = np.nan
            task_options_onset = np.nan
            task_options_duration = np.nan
        iti_durs = show_ITI()
        trial = 0
        enc_RT = np.nan
        ret_file.write('%s,%s,%i,%i,%s,%s,%s,%.3f,%s,%s,%s,%s,%s,%s,%s,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n' %(subject,phase,session,trial,item,enc_task,enc_response,enc_RT,valence,letters,frequency,concreteness,part_of_speech,imageability,status,recog_resp,recog_rt,old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration, task_resp,task_rt,task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration,iti_durs))
    else:
        task_resp = np.nan
        task_rt = np.nan
    iti_durs = show_ITI()

    show_instruct(post_prac_instructions)
    # Start with 5 seconds of fixation to let the person settle in
    for frame in range(10*half_sec):
        fix.draw()
        win.flip()

    # open output file for writing the retrieval data
    trial = 1
    for r_dict in session_1_lists:
        print(r_dict)
        phase, item, enc_task, enc_response, enc_RT, valence, letters, frequency, concreteness, part_of_speech, imageability, status, recog_resp, recog_rt, old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration = show_respond(r_dict)
        if recog_resp == 1 or recog_resp == 2: # if they say the word is old, ask which question they answered about it
            task_resp, task_rt, task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration = show_task_respond(r_dict)
            if np.isnan(task_resp):
                show_no_resp()
        elif np.isnan(recog_resp):
            show_no_resp()
        else:
            task_resp = np.nan
            task_rt = np.nan
            task_onset = np.nan
            task_duration = np.nan
            task_prompt_onset = np.nan
            task_prompt_duration = np.nan
            task_options_onset = np.nan
            task_options_duration = np.nan
        iti_durs = show_ITI()

        ret_file.write('%s,%s,%i,%i,%s,%s,%s,%.3f,%s,%s,%s,%s,%s,%s,%s,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n' %(subject,phase,session,trial,item,enc_task,enc_response,enc_RT,valence,letters,frequency,concreteness,part_of_speech,imageability,status,recog_resp,recog_rt,old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration, task_resp,task_rt,task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration,iti_durs))
        trial = trial + 1
    ret_file.close()
    show_instruct(end_instruct)
    
else:
    show_instruct(time2_instructions)
    
    # Start with 5 seconds of fixation to let the person settle in
    for frame in range(10*half_sec):
        fix.draw()
        win.flip()

    #open output file for writing the retrieval data
    ret_file = path2data + subject + '_StressMem_Retrieval_Session2_' + expInfo['Date']
    ret_file = open(ret_file + '.csv', 'w')
    ret_file.write('subject,phase,session,trial,item,enc_task,enc_response,enc_RT,valence,letters,frequency,concreteness,part_of_speech,imageability,status,recog_resp,recog_rt,old_new_onset,old_new_duration,ret_stim_onset,ret_stim_duration,ret_options_onset,ret_options_duration,task_resp,task_rt,task_onset,task_duration,task_prompt_onset,task_prompt_duration,task_options_onset,task_options_duration,iti_durs\n')
    trial = 1
    for r_dict in session_2_lists:
        phase,item, enc_task, enc_response, enc_RT, valence, letters, frequency, concreteness, part_of_speech, imageability, status, recog_resp, recog_rt, old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration = show_respond(r_dict)
        if recog_resp == 1 or recog_resp == 2:
            task_resp, task_rt, task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration = show_task_respond(r_dict)
            if np.isnan(task_resp):
                show_no_resp()
        elif np.isnan(recog_resp):
            show_no_resp()
        else:
            task_resp = np.nan
            task_rt = np.nan
            task_onset = np.nan
            task_duration = np.nan
            task_prompt_onset = np.nan
            task_prompt_duration = np.nan
            task_options_onset = np.nan
            task_options_duration = np.nan
        iti_durs = show_ITI()

        ret_file.write('%s,%s,%i,%i,%s,%s,%s,%.3f,%s,%s,%s,%s,%s,%s,%s,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n' %(subject,phase,session,trial,item,enc_task,enc_response,enc_RT,valence,letters,frequency,concreteness,part_of_speech,imageability,status,recog_resp,recog_rt,old_new_onset, old_new_duration, ret_stim_onset, ret_stim_duration, ret_options_onset, ret_options_duration, task_resp,task_rt,task_onset, task_duration, task_prompt_onset, task_prompt_duration, task_options_onset, task_options_duration,iti_durs))
        trial = trial + 1
    ret_file.close()
    show_instruct(end_instruct)