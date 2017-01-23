import numpy as np
import pandas as pd
import random, sys
import os.path
from random import shuffle
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import sound
from psychopy import core, data, event, gui, misc, visual

print (pd.__version__)
print (sys.version)
print (sys.path)

canquit = 'true'

path2data = '/Users/mlm2/Work/Expts/StressMem/Data/'

# GUI for subject number and date
try:
    expInfo = misc.fromFile('StressMemlastParams.pickle')
except:
    expInfo = {'SubjectID':'999' }

expInfo['Date'] = data.getDateStr()

dlg = gui.DlgFromDict(expInfo, title='StressMem', fixed=['Date'])
if dlg.OK:
    misc.toFile('StressMemlastParams.pickle', expInfo) 
else:
    core.quit()
subject = expInfo['SubjectID']

#WORDS

# making the word lists
df_encoded = pd.read_csv(path2data + subject + '_StressMem_enc.csv')
df_encoded['status'] = 'old'
df_encoded = df_encoded[df_encoded.block == 1]
df_encoded_neg = df_encoded[df_encoded.val == 0]
df_encoded_pos = df_encoded[df_encoded.val == 1]

# handling the positive lists
df_encoded_pos = df_encoded_pos.iloc[np.random.permutation(len(df_encoded_pos))]
df_encoded_pos = df_encoded_pos.reset_index(drop = True)
df_encoded_pos_1 = df_encoded_pos.head(25)
df_encoded_pos_2 = df_encoded_pos.tail(25)

# handling the negative lists
df_encoded_neg = df_encoded_neg.iloc[np.random.permutation(len(df_encoded_neg))]
df_encoded_neg = df_encoded_neg.reset_index(drop = True)
df_encoded_neg_1 = df_encoded_neg.head(25)
df_encoded_neg_2 = df_encoded_neg.tail(25)

# combining and saving
df_retrieve_old_1 = df_encoded_neg_1.append(df_encoded_pos_1)
# TODO: ADD IN 25 POS AND 25 NEG NEW WORDS
old_lists = df_retrieve_old_1.T.to_dict().values() # turn them into lists of dicts
random.shuffle(old_lists) # shuffles the list of dicts

df_retrieve_old_2 = df_encoded_neg_2.append(df_encoded_pos_2)

# need to read in the old data file to give this one the full info (like which question)

# Refresh rate
refresh = 16.7
fps = int(np.ceil(1000/refresh)) # fps = flips per second; done this way in case refresh rate changes
half_sec = int(0.5*fps)

# Window
# Switch to full, no GUI, and EEG_booth
wintype='pyglet' 
#win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = 'Elyssa Mac', color = 'Ivory', winType=wintype, units = 'cm')
#win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = 'Dan Mac', color = 'Ivory', winType=wintype, units = 'cm')
win=visual.Window([1920, 1080],fullscr=True, allowGUI=False, monitor='MLMmonitor', color = 'Ivory', units='norm')
#win = visual.Window([1024,768], fullscr = False, allowGUI = False, monitor = 'testMonitor', color = '#fffff7', winType=wintype, units = 'norm')
#win = visual.Window([1024,768], fullscr = True, allowGUI = False, monitor = 'EEG_booth', color = 'Ivory', winType=wintype, units = 'norm') 

# Buttons
key_1 = 'c'
key_2 = 'v'
key_3 = 'b'
key_4 = 'n'
key_5 = 'm'
pause_key = 'p' # Advance screen following EEG net placement and QC
quit_key = 'q'

# Recurring stimuli
word = visual.TextStim(win, text='XXXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = 'SteelBlue')
task = visual.TextStim(win, text = 'XXXX', font='Arial', height = 0.10, pos = (0,0), wrapWidth = 50, color = 'SeaGreen')
choice = visual.TextStim(win, text = '__', font='Arial', height = 0.10, pos = (0,0), wrapWidth = 50, color = 'Salmon', bold=True)

arrow = visual.TextStim(win, text='XXXX', font='Arial', height = 0.20, pos = (0,0), color = 'Salmon')
fix = visual.TextStim(win, text = '+', height = 0.10, pos = (0,0), color = 'SteelBlue')
instruct = visual.TextStim(win, text = 'XXXX', height = 0.10, wrapWidth = 80, pos = (0,0), color = 'SteelBlue')
#key_sound = sound.SoundPygame(value='Stimuli/click_quiet.ogg')
#stim_sound = sound.SoundPygame(value='Stimuli/cards2.ogg')

prompt = visual.TextStim(win, text='XXXX', font='Arial', height = 0.20, pos = (0,0.3), wrapWidth = 50, color = 'Salmon')
respond = visual.TextStim(win, text='RESPOND', font='Arial', height = 0.20, pos = (0,0.15), wrapWidth = 50, color = 'Salmon')
scale = visual.TextStim(win, text='  1          2          3          4          5  ', height = 0.10, pos = (0,-0.15), wrapWidth = 50, color = 'SteelBlue')
scale_labels = visual.TextStim(win, text='sure               guess                sure', height = 0.10, pos = (0,-0.275), wrapWidth = 50, color = 'SteelBlue')
scale_choices = visual.TextStim(win, text='XXXX', height = 0.10, pos = (0,-0.425), wrapWidth = 50, color = 'SteelBlue')

# Clocks
RT = core.Clock()

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

def show_prompt(r_dict):
    '''Display retrieval prompt for 1000 ms'''
    prompt.setText(text='Old or New?')
    
#NETSTATION HERE

    for frames in range(fps):
        fix.draw()
        prompt.draw()
        win.flip()


def show_respond(r_dict,stage='expt'):
    '''Elicit response during retrieval'''

    response = 999 
    curr_RT = 999.0
    advance='false'
    event.clearEvents()
    RT.reset()
    retKeys = []
    frame = 0

    scale_choices.setText(text='Old                                           New')

    while advance == 'false':
        retKeys = event.getKeys(keyList=[key_1,key_2,key_3,key_4,key_5,quit_key],timeStamped=RT)
        fix.draw()
        respond.draw()
        scale.draw()
        scale_labels.draw()
        scale_choices.draw()
        win.flip()

        if retKeys:
            ret_resp = retKeys[0][0]
            curr_RT = retKeys[0][1]
            choice.setText(text = '__')
            choice.setColor('SeaGreen')

            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.375,-0.148))
                response = 1
            elif ret_resp == key_2:
                choice.setPos(newPos=(-0.19,-0.148))
                response = 2
            elif ret_resp == key_3:
                choice.setPos(newPos=(0,-0.148))
                response = 3
            elif ret_resp == key_4:
                choice.setPos(newPos=(0.19,-0.148))
                response = 4
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.375,-0.148))
                response = 5

            for frame in range(half_sec): # Show the choice onscreen for 500 ms
                fix.draw()
                respond.draw()
                scale.draw()
                scale_labels.draw()
                scale_choices.draw()
                choice.draw()
                win.flip()

            for frame in range(fps): # Add 1000 ms fixation before the ITI, to regain fixation between trials.
                fix.draw()
                win.flip()

            advance = 'true'

    return (response, curr_RT)
    
def show_task_respond(r_dict):
    '''Elicit response for task'''

    response = 999 
    curr_RT = 999.0
    advance='false'
    event.clearEvents()
    RT.reset()
    retKeys = []
    frame = 0

    scale_choices.setText(text='Emotion? (1)                                           Describes you? (5)')

    while advance == 'false':
        retKeys = event.getKeys(keyList=[key_1,key_5,quit_key],timeStamped=RT)
        fix.draw()
        respond.draw()
        #scale.draw()
        #scale_labels.draw()
        scale_choices.draw()
        win.flip()

        if retKeys:
            ret_resp = retKeys[0][0]
            curr_RT = retKeys[0][1]
            choice.setColor('SeaGreen')

            if ret_resp == quit_key:
                core.quit()
            elif ret_resp == key_1:
                choice.setPos(newPos=(-0.575,-0.425))
                choice.setText(text = '__________')
                response = 'emotion'
            elif ret_resp == key_5:
                choice.setPos(newPos=(0.48,-0.43))
                choice.setText(text = '_______________')
                response = 'describes_you'

            for frame in range(half_sec): # Show the choice onscreen for 500 ms
                fix.draw()
                respond.draw()
                scale_choices.draw()
                choice.draw()
                win.flip()

            for frame in range(fps): # Add 1000 ms fixation before the ITI, to regain fixation between trials.
                fix.draw()
                win.flip()

            advance = 'true'

    return (response, curr_RT)
    
def show_ret_item(r_dict):
    '''Display item at retrieval for 3000 ms'''
    allKeys = []
    curr_item = r_dict['word']
    status = r_dict['status']
    task = r_dict['task']
    word.setText(text=curr_item)

    for frames in range(3*fps):
#        fix.draw()
        prompt.draw()
        word.draw()
        win.flip()
    allKeys = event.getKeys(keyList=[key_1, key_5, quit_key])
    if allKeys: # allow user to quit on this screen
        this = allKeys[0][0]
        if this == quit_key:
            core.quit()
    return (curr_item, status, task)
    
def show_ret_task(r_dict):
    '''Display item at retrieval for 3000 ms'''
    allKeys = []
    curr_item = r_dict['word']
    status = r_dict['status']
    task = r_dict['task']
    prompt.setText(text = 'Question?')
    word.setText(text=curr_item)

    for frames in range(3*fps):
#        fix.draw()
        prompt.draw()
        word.draw()
        win.flip()
    allKeys = event.getKeys(keyList=[key_1, key_5, quit_key])
    if allKeys: # allow user to quit on this screen
        this = allKeys[0][0]
        if this == quit_key:
            core.quit()
    return ()
    
# Instructions
r_instructions = ['FILLER Now we will complete the practice TEST trials.\n\nWe will show you words one at a time.\n\nEach word will appear below a prompt,\neither \
"Side" or "Question".\n\nPress 1 to advance.',

'When you see the "Side" prompt, try\nto remember:\n\nWas the word on the left or right\nside of the screen?\n\nPress 1 to advance.',

'When you see the "Question" prompt, try to\nremember which question you answered\nfor that word:\n\n"Living/Non-living?" or "Mobile/Immobile?"\n\nPress 1 to \
advance.',

'The prompts will appear above a cross,\nand the words will appear below the cross.\n\nTry to keep your eyes on the cross, to\nlimit extra eye movement.\n\n\
Press 1 to advance.',

'Does this make sense to you?\n\nIf you have any questions, please ask now.\n\nOtherwise, press 1 to advance.',

'Please try your best.\n\nWe will record your brain activity\nas you try to remember.\n\nThe ideal time to blink is when\nyou are responding.\n\nPress 1 to \
advance.',

'Any questions? If so, please ask now.\n\nWhen you are ready, press 1 to start.']

show_instruct(r_instructions)

#open output file for writing the retrieval data
ret_file = subject + '_StressMem_Retrieval' + expInfo['Date']
ret_file = open(ret_file + '.csv', 'w')
ret_file.write('subject,trial,word,status,recog_resp,recog_rt,task,task_resp,task_rt,iti_dur\n') 

trial = 1

for r_dict in old_lists:
    show_prompt(r_dict)
    item, status, task = show_ret_item(r_dict)
    recog_resp, recog_rt = show_respond(r_dict)
    if recog_resp == 1 or recog_resp == 2:
        show_ret_task(r_dict)
        task_resp, task_rt = show_task_respond(r_dict)
        #task_resp = 'x'
        #task_rt = 888
    else:
        task_resp = ''
        task_rt = 999
    iti_durs = show_ITI()

    ret_file.write('%s,%i,%s,%s,%i,%.3f,%s,%s,%.3f,%i\n' %(subject,trial,item,status,recog_resp,recog_rt,task,task_resp,task_rt,iti_durs))
    trial = trial + 1

ret_file.close()