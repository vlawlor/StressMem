# Last updated: Feburary 22, 2017
# Authors: Victoria Lawlor, Elyssa Barrick, and Dan Dillon
# Runs retrieval for the StressMem experiment.

# User, you may need/want to edit the next several lines
import csv, getpass, os, random, sys, glob
userName = getpass.getuser()
monitorName = 'Elyssa Mac'
path2words = '/Users/' + userName + '/Work/Expts/StressMem/PsychoPy/Stimuli/'
path2data = '/Users/' + userName + '/Work/Expts/StressMem/Data/'

# Shouldn't need to edit below . . . 
import os.path, random, sys
import numpy as np
import pandas as pd
from copy import deepcopy # Best not to copy things in python if you can avoid it, having multiple copies of objects can get hairy . . . 
from random import shuffle
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, data, event, gui, misc, sound, visual

print (pd.__version__)
print (sys.version)
print (sys.path)

# GUI for subject number and date
try:
    expInfo = misc.fromFile('StressTaskLastParams.pickle')
except:
    expInfo = {'SubjectID':'999' }

expInfo['Date'] = data.getDateStr()
expInfo['Session'] = 0

dlg = gui.DlgFromDict(expInfo, title='StressMem', fixed=['Date'])
if dlg.OK:
    misc.toFile('StressTaskLastParams.pickle', expInfo) 
else:
    core.quit()
subject = expInfo['SubjectID']
session = expInfo['Session']

if  session != 1 and session != 2: # needs a 1 or 2 for session to show the correct word lists, don't want them to go all the way through the practice before we realize
    myDlg = gui.Dlg(title="Invalid session number") 
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

# WORDS
if session == 1:
    # Read all words and the encoding words into dicts, then remove any encoded words from the "new words" dict
    enc_words = {}
    new_words = {}

    encoded = glob.glob(path2data + subject + '*_StressMem_enc.csv')
    with open(encoded, 'rU') as x:
    with open('balanced_words.csv', 'rU') as y:
        enc_data = csv.DictReader(x)
        all_data = csv.DictReader(y)
        for row in all_data:
            new_words[row['word']] = row
            new_words[row['word']]['status'] = 'new'
            del new_words[row['word']]['word']
        for row in enc_data:
            if row['word'] in new_words.keys():
                del new_words[row['word']]
            enc_words[row['word']] = row
            enc_words[row['word']]['status'] = 'old'
            del enc_words[row['word']]['word']
        for new_key in ['RT', 'block', 'iti_duration', 'options_duration', 'options_onset', 'response', 'options_onset', 'subject', 'task', 'task_duration', # setting the values for the new items
           'task_onset', 'trial', 'word_duration', 'word_onset']:
            for key in new_words.keys():
                new_words[key][new_key] = np.nan

    # Splitting the new and old words into the two blocks, with even division between positive and negative and also with even division b/w tasks for the old words

    new_neg = []
    new_pos = []
    old_neg_emo = []
    old_neg_des = []
    old_pos_emo = []
    old_pos_des = []

    for key in new_words.keys():
        if new_words[key]['valence'] == '0':
            new_neg.append(new_words[key])
        else:
            new_pos.append(new_words[key])

    for key in enc_words.keys():
        if enc_words[key]['valence'] == '0' and enc_words[key]['task'] == 'Positive':
            old_neg_emo.append(enc_words[key])
        elif enc_words[key]['valence'] == '0' and enc_words[key]['task'] == 'Describe':
            old_neg_des.append(enc_words[key])
        elif enc_words[key]['valence'] == '1' and enc_words[key]['task'] == 'Positive':
            old_pos_emo.append(enc_words[key])
        elif enc_words[key]['valence'] == '1' and enc_words[key]['task'] == 'Describe':
            old_pos_des.append(enc_words[key])

    for word_list in [new_neg, new_pos, old_neg_emo, old_neg_des, old_pos_emo, old_pos_des]:
        random.shuffle(word_list)

    session_1_list = []
    session_2_list = []

    for block in [1,2]:
        if block == 1:
            emo_ct = random.choice([12,13])
            des_ct = 25 - emo_ct
            session_1_list.append(new_neg[:25])
            session_1_list.append(new_pos[:25])
            session_1_list.append(old_neg_emo[:emo_ct])
            session_1_list.append(old_neg_des[:des_ct])
            session_1_list.append(old_pos_emo[:emo_ct])
            session_1_list.append(old_pos_des[:des_ct])
        else:
            emo_ct = des_ct
            des_ct = 25 - emo_ct
            session_2_list.append(new_neg[25:50])
            session_2_list.append(new_pos[25:50])
            session_2_list.append(old_neg_emo[emo_ct:25])
            session_2_list.append(old_neg_des[des_ct:25])
            session_2_list.append(old_pos_emo[emo_ct:25])
            session_2_list.append(old_pos_des[des_ct:25])

    for sess_list in [session_1_list,session_2_list]:
        random.shuffle(sess_list)

    np.save(path2data + subject + '_session_2_list.npy', session_2_list) #save the session 2 list of dicts for later

elif session == 2:
    session_2_list = np.load(path2data + subject + '_session_2_list.npy')

# Recurring stimuli
word = visual.TextStim(win, text='XXXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')
choice = visual.TextStim(win, text = '__', font='Arial', height = 0.10, pos = (0,-.2), wrapWidth = 50, color = '#1B1C96', bold=True)
no_resp = visual.TextStim(win, text='NO RESPONSE', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = 'black')
fix = visual.TextStim(win, text = '+', height = 0.10, pos = (0,.15), color = '#1B1C96')
instruct = visual.TextStim(win, text = 'XXXX', height = 0.10, wrapWidth = 80, pos = (0,0), color = '#1B1C96')
old_new_prompt = visual.TextStim(win, text='Old or New?', font='Arial', height = 0.20, pos = (0,0.3), wrapWidth = 50, color = '#ff7a5b')
task_prompt = visual.TextStim(win, text='Question?', font='Arial', height = 0.20, pos = (0,0.3), wrapWidth = 50, color = '#e569CE')
scale = visual.TextStim(win, text='  1           2           3           4           5           6  ', height = 0.10, pos = (0,-0.25), wrapWidth = 50, color = '#1B1C96')
scale_labels = visual.TextStim(win, text='Sure  Probably  Maybe  Maybe  Probably  Sure', height = 0.10, pos = (0,-0.4), wrapWidth = 50, color = '#1B1C96')
old_new_scale = visual.TextStim(win, text='Old                 New', height = 0.17, pos = (0,-0.62), wrapWidth = 50, color = '#ff7a5b')
task_scale = visual.TextStim(win, text='Describes          Positive', height = 0.17, pos = (0,-0.62), wrapWidth = 50, color = '#e569CE')

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
            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.51,-0.25))
                response = 1
            elif ret_resp == key_2:
                choice.setPos(newPos=(-0.3,-0.25))
                response = 2
            elif ret_resp == key_3:
                choice.setPos(newPos=(-0.1,-0.25))
                response = 3
            elif ret_resp == key_4:
                choice.setPos(newPos=(0.1,-0.25))
                response = 4
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.3,-0.25))
                response = 5
            elif ret_resp == key_6:
                choice.setPos(newPos=(0.51, -.25))
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

    word.setColor(color = '#2F1E6E')
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
            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.51,-0.25))
                response = 1
            elif ret_resp == key_2:
                choice.setPos(newPos=(-0.3,-0.25))
                response = 2
            elif ret_resp == key_3:
                choice.setPos(newPos=(-0.1,-0.25))
                response = 3
            elif ret_resp == key_4:
                choice.setPos(newPos=(0.1,-0.25))
                response = 4
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.3,-0.25))
                response = 5
            elif ret_resp == key_6:
                choice.setPos(newPos=(0.51, -.25))
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
'After 3.5 seconds, a scale will appear \nat the bottom of the screen. \n\nThis is where you will choose \n"OLD" or "NEW." \n\nPress 1 to advance.',
'If you select "OLD," a new screen will \ncome up with the prompt "QUESTION" \nabove a cross, and the word shown again \nbelow the cross.\
\n\nWhen you see this prompt, try to remember: \n\nWhich question was asked about \nthis word yesterday?\n\nPress 1 to advance.',
'After 3.5 seconds, a scale will appear at the \nbottom of the screen. \n\nThis is where you will choose which question \nyou answered for that word yesterday:\n\n"Emotion?" or "Describes?" \
\n\nPress 1 to advance.',
'Does this make sense to you?\n\nIf you have any questions, please ask now.\n\nOtherwise, press 1 to advance.',
'Please try your best.\n\nWe will record your brain activity\nas you try to remember.\n\nThe ideal time to blink is when\nyou are responding.\
\n\nPress 1 to advance.',
'Any questions? If so, please ask now.\n\nWe are going to do some practice trials\nbefore we start the experiment.\n\nWhen you are ready, press 1 to start.']

post_prac_instructions = ['You have finished the practice trials.\n\nDo you have any questions? If so, \nplease ask now.\n\nWhen you are ready,press 1 to advance.',
'We are ready to begin the 1st block.\n\nIt will be identical to the practice trials,\nbut you will see 50 words rather than 4.\n\nWhen you are ready to begin, press 1.']

time2_instructions = ['We are ready to begin the second block of trials.\n\nDo you have any questions? If so, please ask now.\n\nWhen you are ready, press 1 to advance.',
'The second block will be identical to the first block.\n\nWhen you are ready to begin press 1.']

end_instruct = ['Great job! You have finished this portion of the task.\n\nPlease wait for the experimenter.']

if session == 1:
    show_instruct(r_instructions)
    # Start with 5 seconds of fixation to let the person settle in
    for frame in range(10*half_sec):
        fix.draw()
        win.flip()
    ret_file = path2data + subject + '_StressMem_Retrieval_' + expInfo['Date']
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
    for r_dict in session_1_list:
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
    ret_file = open(glob.glob(path2data + subject + '*_StressMem_Retrieval*.csv')[0], 'a')
    
    trial = 101
    for r_dict in session_2_list:
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
