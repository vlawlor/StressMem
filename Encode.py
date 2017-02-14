# Last updated: Feburary 14, 2017
# Authors: Victoria Lawlor, Elyssa Barrick, and Dan Dillon
# Runs encoding for the StressMem experiment.

# User, you may need/want to edit the next several lines
import csv, getpass, os, random, sys
refresh = 16.7
userName = getpass.getuser()
monitorName = 'Dan Mac'
path2words = '/Users/' + userName + '/Work/Expts/StressMem/PsychoPy/Stimuli/'
path2data = '/Users/' + userName + '/Work/Expts/StressMem/Data/'

# Shouldn't need to edit below . . . 
import numpy as np
import pandas as pd
from random import shuffle, randint
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, data, event, gui, misc, sound, visual

#print (pd.__version__)
#print (sys.version)
#print (sys.path)

# GUI for subject number and date. I loved the check for existing encoding word lists here but we don't need to save those separately b/c we can just rely on the encoding logfile.
try:
    expInfo = misc.fromFile('StressTaskLastParams.pickle') # Call it "StressTask" so we don't draw attention to the upcoming tasks . . . 
except:
    expInfo = {'SubjectID':'999' }
expInfo['Date'] = data.getDateStr()

dlg = gui.DlgFromDict(expInfo, title='StressTask', fixed=['Date'])
if dlg.OK:
    misc.toFile('StressTaskLastParams.pickle', expInfo) 
else:
    core.quit()
subject = expInfo['SubjectID']

# Flips per second; will be updated in case of refresh rate changes
fps = int(np.ceil(1000/refresh))
half_sec = int(0.5*fps)

# Clocks
exp_clock = core.Clock()
RT = core.Clock()

# Window
wintype='pyglet' 
win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = monitorName, color = '#FFFFFA', winType=wintype, units = 'norm')

# Buttons
key_1 = 'c'
key_5 = 'm'
pause_key = 'p' # Advance screen following EEG net placement and QC
quit_key = 'q'

# Recurring stimuli
fix = visual.TextStim(win, text = '+', height = 0.10, pos = (0.0,0.15), color = '#1B1C96')
instruct = visual.TextStim(win, text = 'XXXX', height = 0.10, wrapWidth = None, pos = (0,0), color = '#1B1C96')
task_prompt = visual.TextStim(win, text = 'XX', font='Arial', height = 0.20, pos = (0.0,0.30), wrapWidth = 50, color = '#129066') # just a darker shade of #1bce92
word = visual.TextStim(win, text='XXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')
options = visual.TextStim(win, text = 'Yes     No', font='Arial', height = 0.15, pos = (0.0,-0.27), wrapWidth = 50, color = '#ff6542', bold=True)
reply_no = visual.TextStim(win, text = '___', font='Arial', height = 0.15, pos = (0.13,-0.29), wrapWidth = 50, color = '#ff6542', bold=True)
reply_yes = visual.TextStim(win, text = '___', font='Arial', height = 0.15, pos = (-0.11,-0.29), wrapWidth = 50, color = '#ff6542', bold=True)
no_resp = visual.TextStim(win, text='NO RESPONSE!', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = 'black')
begin_typing = visual.TextStim(win, text='Begin Typing', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')

key_sound = sound.SoundPygame('resp.wav')
stim_sound = sound.SoundPygame('stim.wav')
no_resp_sound = sound.SoundPygame('C')

# CREATE THE ENCODING LIST. No need to save separately here because all the same information will be saved in the encoding logfile

d = {} # Create a dictionary and read in all the information about each word. Will save data on valence, arousal, frequency, etc for possible use as covariates in analysis.
with open(path2words + 'balanced_words.csv', mode='r') as infile:
    next(infile) # skip the header
    reader = csv.reader(infile)
    for i, rows in enumerate(reader):
        d[i] = {'word':rows[0], 'mean_valence':rows[1], 'mean_arousal':rows[2], 'valence':rows[3], 'letters':rows[4], 'frequency':rows[5], 'concreteness':rows[6], 'part_of_speech':rows[7], 'imageability':rows[8]}

# Now split that into positive and negative dictionaries.
pos_ct = 0
neg_ct = 0
pos_d = {}
neg_d = {}
for k in range(len(d)):
    if d[k]['valence'] == '1':
        pos_d[pos_ct] = d[k]
        pos_ct = pos_ct + 1
    else:
        neg_d[neg_ct] = d[k]
        neg_ct = neg_ct + 1

# Now select 50 words, at random, from each list for use at encoding.
# Assign half the words in each list to one of two tasks--either "Describes?" (you) or "Positive?".
enc_list = []
for i in range(50):
    if i % 2: # Test to see if i is an even number.
        task = 'Describes?'
    else:
        task = 'Positive?'
    pos_word = pos_d.popitem()[1] # Tricky: when you pop the item off, it comes as a (k,v) tuple, and here k = the count integer, while v = the dict with word info. So this selects v for us . . . 
    pos_word['task'] = task
    neg_word = neg_d.popitem()[1]
    neg_word['task'] = task
    enc_list.append(pos_word)
    enc_list.append(neg_word)

# Now shuffle the list and we're good to go!
random.shuffle(enc_list)

# FUNCTIONS
def show_instruct(instruct_list, adv_key=key_1, quit=quit_key):
    '''Print instructions and wait for key press'''

    for instructions in instruct_list:
        event.clearEvents()
        allKeys = []
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

def show_enc_full(in_dict, phase = 'experiment'):
    '''Display task for 1000 ms, then task plus word for 3000 ms, then task plus word plus options for 10 seconds or until response'''

    curr_task = in_dict['task']
    curr_word = in_dict['word']
    if phase == 'practice':
        mean_valence = mean_arousal = valence = letters = frequency = concreteness = part_of_speech = imageability = 'none'
    else:
        mean_valence = in_dict['mean_valence']
        mean_arousal = in_dict['mean_arousal']
        valence = in_dict['valence']
        letters = in_dict['letters']
        frequency = in_dict['frequency']
        concreteness = in_dict['concreteness']
        part_of_speech = in_dict['part_of_speech']
        imageability = in_dict['imageability']

    task_prompt.text = curr_task
    word.text = curr_word
    curr_task = curr_task.strip('?')

    task_onset = exp_clock.getTime()
    for i in range(fps):
        task_prompt.draw()
        fix.draw()
        win.flip()
    task_offset = exp_clock.getTime()
    task_duration = task_offset - task_onset

    stim_onset = exp_clock.getTime()
    stim_sound.play()
    for i in range(3*fps):
        task_prompt.draw()
        fix.draw()
        word.draw()
        win.flip()
    stim_offset = exp_clock.getTime()
    stim_duration = stim_offset - stim_onset

    event.clearEvents()
    RT.reset()
    advance = 'false'
    response = 'no_response'
    curr_RT = 999.0
    allKeys = []
    frame = 0
    options_onset = exp_clock.getTime()
    while frame < (10*fps) and advance == 'false':
        allKeys = event.getKeys(keyList=[key_1, key_5, quit_key],timeStamped=RT)
        task_prompt.draw()
        word.draw()
        fix.draw()
        options.draw()
        win.flip()

        if allKeys:
            options_offset = exp_clock.getTime()
            enc_resp = allKeys[0][0]
            curr_RT = allKeys[0][1]
            key_sound.play()
            advance = 'true'
            frame = 0

            if enc_resp == key_1:
                response = 'yes'
                while frame < (4*half_sec):
                    task_prompt.draw()
                    word.draw()
                    fix.draw()
                    options.draw()
                    reply_yes.draw()
                    win.flip()
                    frame = frame + 1
                options_offset = exp_clock.getTime()
                options_duration = options_offset - options_onset

            elif enc_resp == key_5:
                response = 'no'
                while frame < (4*half_sec):
                    task_prompt.draw()
                    word.draw()
                    fix.draw()
                    options.draw()
                    reply_no.draw()
                    win.flip()
                    frame = frame + 1
                options_offset = exp_clock.getTime()
                options_duration = options_offset - options_onset

            elif enc_resp == quit_key:
                core.quit()
        frame = frame + 1
    options_offset = exp_clock.getTime()
    options_duration = options_offset - options_onset

    return (curr_task, task_onset, task_duration, curr_word, stim_onset, stim_duration, mean_valence, mean_arousal, valence, letters, frequency, concreteness, part_of_speech, imageability, options_onset,\
    options_duration, response, curr_RT)

def show_ITI():
    '''Display fixation ITI for 500, 1000, or 2000 ms, with 500 ms over-represented'''

    iti_durs = [half_sec, half_sec, fps, 2*fps]
    duration = random.choice(iti_durs)

    iti_onset = exp_clock.getTime()
    for frames in range(duration):
        fix.draw()
        win.flip()
    iti_offset = exp_clock.getTime()
    iti_duration = iti_offset - iti_onset

    return iti_duration

def show_break():
    '''Display break text for 30 seconds'''
    event.clearEvents()
    allKeys = []
    advance = 'false'

    duration = 30*fps

    for frames in range(duration):
        instruct.setText(break_instructions)
        instruct.draw()
        win.flip()
        if allKeys:
            resp = allKeys[0][0]
            if resp == quit_key:
                   core.quit()

    return duration*refresh

def show_no_resp():
    '''Show the text "no response"'''
    no_resp_sound.play()
    for frames in range(2*fps):
        no_resp.draw()
        win.flip()

def free_recall():
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    text = visual.TextStim(win, height=(.10), wrapWidth=(.9),color='#1B1C96',text='')
    file_text = visual.TextStim(win, height=(.10), wrapWidth=(.9),color='#1B1C96',text='')

#   Loop until return is pressed
    endTrial = False
    while not endTrial:
    # Wait for response...
        writing = event.getKeys() #used to be event.waitKeys
        if writing:
            print writing
        # If backspace, delete last character
            if writing[0] == 'backspace':
                text.setText(text.text[:-1])
                file_text.setText(file_text.text[:-1])
        # If return, end trial
            elif writing[0] == 'return':
                text.setText(text.text + '\n')
                file_text.setText(file_text.text + '\n')
        # Insert space
            elif writing[0] == 'space':
                text.setText(text.text + ' ')
                file_text.setText(file_text.text + '\n')
        # Else if a letter, append to text:
            elif writing[0] in chars:
                text.setText(text.text + writing[0])
                file_text.setText(file_text.text + writing[0])
        # If escape, abort the experiment
            elif writing[0]=='escape':
                endTrial = True
        elif text.text == '':
            begin_typing.draw()
    # Display updated text
        text.draw()
        win.flip()
    recall_file.write(file_text.text)

# INSTRUCTIONS
enc_instructions = ['Welcome!\n\nIn this task, words will appear on the screen.\
\n\nAfter each word is presented, you will be asked one of two questions about \nthe word, and you will respond by pressing a button.\
\n\nPress button 1 to advance.',  
'If you see "Positive?", press yes or no to indicate whether you think the word is positive or negative. \
\n\nPress button 1 to advance.',
'If you see "Describes?", answer yes or no based on whether or not you think the word describes \
or relates to you. \
\n\nPress button 1 to advance.',
'There are 2 blocks of trials, with a short break between the blocks. \
\n\nPress button 1 to begin the practice.']
final_enc_instructions = ['Do you have any final questions?\n\nIf not, press 1 to begin the task.']

break_instructions = 'Good job! You are halfway done. \
\n\nThis screen will advance after a short break, and then you will be able to advance to the second half of the task when you are ready.'

break_instructions_2 = ['Press 1 to begin the second half.']

recall_instructions = ['Great job! You are finished with that portion of the task. \n\n\
On the next screen, please type all of the words that you can remember seeing from the previous part of \
the task. You may hit space to start a new word, and enter when you have reached the end of the line.\n\n\
Press the "escape" key when you have finished typing all of the words that you can remember. \n\n \
Press 1 to begin.']

end_instructions = ['Great job! You are all done.\n\nThe experimenter will be in shortly.']

# Practice Stimuli
pract1 = {'word': 'faker', 'valence' : '1', 'task': 'Positive?'}
pract2 = {'word': 'generous', 'valence' : '1', 'task': 'Describes?'}
pract3 = {'word': 'loner', 'valence' : '1', 'task': 'Describes?'}
pract4 = {'word': 'thoughtful', 'valence' : '1', 'task': 'Positive?'}
pract_trials = [pract1, pract2, pract3, pract4]

# RUN PRACTICE TRIALS
show_instruct(enc_instructions)

# Start with 5 seconds of fixation to let the person settle in
for frame in range(10*half_sec):
    fix.draw()
    win.flip()

exp_clock.reset()
for dict in pract_trials:
    curr_task, task_onset, task_duration, curr_word, stim_onset, stim_duration, mean_valence, mean_arousal, valence, letters, frequency, concreteness, part_of_speech, imageability, options_onset,\
options_duration, response, curr_RT = show_enc_full(dict, phase='practice')
    if curr_RT == 999.0:
        show_no_resp()
    fix_duration = show_ITI() 
show_instruct(final_enc_instructions)

# RUN EXPERIMENTAL TRIALS

# Open output file for writing the encoding data
enc_file = expInfo['SubjectID'] + '_' + expInfo['Date']
enc_file = open(path2data + enc_file+'_StressMem_enc' +'.csv', 'w')
enc_file.write('subject,trial,block,task,task_onset,task_duration,word,word_onset,word_duration,mean_valence,mean_arousal,valence,letters,frequency,concreteness,part_of_speech,imageability,\
options_onset,options_duration,response,RT,iti_duration\n')

# Start with 5 seconds of fixation to let the person settle in
for frame in range(10*half_sec):
    fix.draw()
    win.flip()

# Run the trials
exp_clock.reset()
trial = 1
for block in [1,2]:
    for dict in enc_list:
        curr_task, task_onset, task_duration, curr_word, stim_onset, stim_duration, mean_valence, mean_arousal, valence, letters, frequency, concreteness, part_of_speech, imageability, options_onset,\
options_duration, response, curr_RT = show_enc_full(dict)
        if curr_RT == 999.0:
            show_no_resp()
        fix_duration = show_ITI() 

        # Record trial data
        enc_file.write('%s,%i,%i,%s,%0.3f,%0.3f,%s,%0.3f,%0.3f,%s,%s,%s,%s,%s,%s,%s,%s,%0.3f,%0.3f,%s,%0.3f,%0.3f\n' %(subject,trial,block,curr_task,task_onset,task_duration,curr_word,stim_onset,stim_duration,\
mean_valence,mean_arousal,valence,letters,frequency,concreteness,part_of_speech,imageability,options_onset,options_duration,response,curr_RT,fix_duration))

        # Update trial number
        trial = trial + 1

    # Take a break between blocks
    if block == 1:
        show_break()
        show_instruct(break_instructions_2)

enc_file.close()

# FREE RECALL

# Set up a file to hold the free recall data.
recall_file = expInfo['SubjectID'] + '_' + expInfo['Date']
recall_file = open(path2data + recall_file+'_StressMem_recall' +'.csv', 'w')
recall_file.write('')

# Run the recall phase . . . 
show_instruct(recall_instructions)
free_recall()
recall_file.close()
show_instruct(end_instructions)