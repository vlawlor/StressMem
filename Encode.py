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

path2words = '/Users/mlm2/Work/Expts/StressMem/Stimuli/'
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

if os.path.isfile(path2data + 'Encoded_words/encoded_words_' + subject + '.csv'): #presents a warning if there are already word files for this person
    myDlg = gui.Dlg(title="WARNING")
    myDlg.addText('A words list file already exists for this participant ID. Clicking ok will overwrite this file.')
    ok_data = myDlg.show()
    if myDlg.OK:
        print(ok_data)
    else:
        core.quit()

# Create and save the encoding lists

df = pd.read_csv(path2words + 'balanced_words_option8_WORKING.csv')
df = df[['Word', 'val']]

df_neg = df[df.val == 0] # getting the negative words that will be shown this session
df_neg_encode = df_neg.iloc[np.random.permutation(len(df_neg))] 
df_neg_encode = df_neg_encode.head(50) # shuffle the negatives, then get the first 50

df_pos = df[df.val == 1] # getting the positive words that will be shown this session
df_pos_encode = df_pos.iloc[np.random.permutation(len(df_pos))]
df_pos_encode = df_pos_encode.head(50) # shuffle the positives, then get the first 50 

df_encoded = df_neg_encode.append(df_pos_encode)
df_encoded = df_encoded.reset_index(drop = True)
df_encoded['Question'] = 'Describes you?'
df_encoded.ix[0:24, 'Question'] = 'Emotion'
df_encoded.ix[50:74, 'Question'] = 'Emotion' # add the questions so that there is a 50/50 ratio for neg and pos words

df_encoded.to_csv(path2data + 'Encoded_words/encoded_words_' + subject + '.csv') # saving the words and questions
enc_lists = df_encoded.T.to_dict().values() # turn them into lists of dicts
random.shuffle(enc_lists) # shuffles the list of dicts
random.shuffle(enc_lists) # extra shuffled

#print (enc_lists)
# Refresh rate
refresh = 16.7
fps = int(np.ceil(1000/refresh)) # fps = flips per second; done this way in case refresh rate changes
half_sec = int(0.5*fps)

# Window
# Switch to full, no GUI, and EEG_booth
wintype='pyglet' 
#win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = 'Elyssa Mac', color = 'Ivory', winType=wintype, units = 'cm')
#win = visual.Window([1920,1080], fullscr = True, allowGUI = False, monitor = 'Dan Mac', color = 'Ivory', winType=wintype, units = 'cm')
#win=visual.Window([1920, 1080],fullscr=True, allowGUI=False, monitor='MLMmonitor', units='pix')
win = visual.Window([1024,768], fullscr = False, allowGUI = False, monitor = 'testMonitor', color = '#fffff7', winType=wintype, units = 'norm')
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
word = visual.TextStim(win, text='XXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')
task = visual.TextStim(win, text = 'XX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#11A08E')
choice = visual.TextStim(win, text = '_____', font='Arial', height = 0.15, pos = (0,-.29), wrapWidth = 50, color = '#ff7a5b', bold=True)
instruct = visual.TextStim(win, text = 'XX', height = 0.10, wrapWidth = None, pos = (0,0), color = '#1B1C96')
fix = visual.TextStim(win, text = '+', height = 0.10, pos = (0,0), color = '#1B1C96')
instruct = visual.TextStim(win, text = 'XXXX', height = 0.10, wrapWidth = None, pos = (0,0), color = '#1B1C96')
options = visual.TextStim(win, text = 'XXXX', font='Arial', height = 0.15, pos = (0,-.27), wrapWidth = 50, color = '#ff7a5b', bold=True)

#key_sound = sound.SoundPygame('click_quiet.ogg')
#stim_sound = sound.SoundPygame('cards2.ogg')

# Clocks
RT = core.Clock()

#Functions
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
def show_enc_item(in_dict):
    '''Display encoding item and encoding task for 1 second'''
    question = in_dict['Question']
    curr_item = in_dict['Word']
    task.setText(text=question)

    task.setPos(newPos=(0,.3))
    task.setPos(newPos=(0,.3))
    word.setText(text=curr_item)
    word.setPos(newPos=(0,0))
    if question == 'Describes you?':
        curr_task = 'describes_you'
        options.setText('Yes (1)     No (5)')
    elif question == 'Emotion':
        curr_task = 'emotion'
        options.setText('Positive (1)     Negative (5)')

    for frame in range(2*fps):
        word.draw()
        task.draw()
        #options.draw()
        win.flip()

    return curr_item


def show_enc_full(in_dict):
    '''Display encoding item, encoding task, and options for 10 seconds or until response'''
    response = 'no_response'
    curr_RT = 999.0
    question = in_dict['Question']
    curr_item = in_dict['Word']
    curr_type = in_dict['val']
    word.setText(text=curr_item)
    choice.setColor('Salmon')
    advance = 'false'

    word.setPos(newPos=(0,0))

    event.clearEvents()
    RT.reset()
    allKeys = []
    frame = 0
#    stim_sound.play()

    while frame < (10*fps) and advance == 'false':
        allKeys = event.getKeys(keyList=[key_1, key_5, quit_key],timeStamped=RT)
        #arrow.draw()
        task.draw()
        word.draw()
        options.draw()
        win.flip()

        if allKeys:
            enc_resp = allKeys[0][0]
            curr_RT = allKeys[0][1]

            if enc_resp == key_1:
                advance = 'true'
#               key_sound.play()
                if question == 'emotion':
                    response = 'positive'
                    choice.setText('________')
                    choice.setPos(newPos=(-.33, .27))
                    advance = 'true'
                if question == 'describes you?':
                    response = 'yes'
                    choice.setText('____')
                    choice.setPos(newPos=(-.29, .27))
                    advance = 'true'
                while frame < (fps) and advance =='false':
                    #arrow.draw()
                    task.draw()
                    word.draw()
                    options.draw()
                    choice.draw()
                    win.flip()
                    frame = frame + 1
                    
            elif enc_resp == key_5:
                advance = 'true'
#                key_sound.play()
                if question == 'emotion':
                    response = 'negative'
                    choice.setText('________')
                    choice.setPos(newPos=(.31, .27))
                if question == 'describes you?':
                    response = 'no'
                    choice.setText('____')
                    choice.setPos(newPos=(.31, .27))
                while frame < (7*half_sec):
                    #arrow.draw()
                    task.draw()
                    word.draw()
                    options.draw()
                    choice.draw()
                    win.flip()
                    frame = frame + 1
            elif enc_resp == quit_key:
                core.quit()
            
        frame = frame + 1
    return (curr_type, response, curr_RT)


def show_task(in_dict):
    '''Present arrow and encoding task for 500 ms'''

    question = in_dict['Question']
    task.setText(text=question)

    task.setPos(newPos=(0,.3))
    task.setPos(newPos=(0,.3))

    if question == 'Describes you?':
        curr_task = 'describes_you'
        options.setText('Yes (1)     No (5)')
    elif question == 'Emotion':
        curr_task = 'emotion'
        options.setText('Positive (1)     Negative (5)')

    for frame in range(half_sec):
        #arrow.draw()
        task.draw()
        #options.draw()
        win.flip()

    return curr_task


def show_ITI():
    '''Display fixation ITI for 500, 1000, or 2000 ms, with 500 ms over-represented'''

    iti_durs = [half_sec, half_sec, fps, 2*fps]
    duration = random.choice(iti_durs)

    for frames in range(duration):
        fix.draw()
        win.flip()

    return duration*refresh

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



# Instructions
enc_instructions = ['Welcome!\n\nIn this task, words will appear on the screen in front of you. \
\n\nAfter each word is presented, you will be asked one of two questions about the word,\nand you will respond by pressing a button.\
\n\nPress button 1 to advance.',  
'If you are asked about emotion, select whether you think the word is positive or negative. \
\n\nPress button 1 to advance.',
'If you are asked if a word describes you, answer yes or no based on whether or not you think the word describes \
or relates to you. \
\n\nPress button 1 to advance.',
'\n\nThere are 2 blocks of trials, with a short break between the blocks. \
\n\nPress button 1 to begin the practice trials.']
final_enc_instructions = ['Do you have any final questions?\n\nIf not, press 1 to begin the task']

break_instructions = 'Good job! You are halfway through this task. The next part of the task is exactly the same as before. Take a minute or two to stretch your \
legs if you would like, and press 1 to move on to the second half of the task when you are ready.\n\nThis screen will advance automatically in 30 seconds, and then you \
will be able to advance to the second half of the task when you are ready.'

break_instructions_2 = ['Press 1 to begin the second half of the task']

# Practice Stimuli
pract1 = {'Word': 'faker', 'val' : '1', 'Question': 'Emotion'}
pract2 = {'Word': 'generous', 'val' : '1', 'Question': 'Describes you?'}
pract3 = {'Word': 'loner', 'val' : '1', 'Question': 'Describes you?'}
pract4 = {'Word': 'thoughtful', 'val' : '1', 'Question': 'Emotion'}
pract_trials = [pract1, pract2, pract3, pract4]

# Begin practice trials
show_instruct(enc_instructions)

for dict in pract_trials:
    show_task(dict)
    show_enc_item(dict)
    show_enc_full(dict)
    show_ITI()
show_instruct(final_enc_instructions)

# RUN EXPERIMENTAL TRIALS

# Open output file for writing the encoding data
enc_file = expInfo['SubjectID'] + '_' + expInfo['Date']
enc_file = open(path2data + enc_file+'_StressMem_enc' +'.csv', 'w')
enc_file.write('subject,trial,block,word,val,task,response,RT,iti_dur(ms)\n')
trial = 1

for dict in enc_lists:
    block = 1
    curr_task = show_task(dict)
    curr_item = show_enc_item(dict)
    curr_type, response, curr_RT = show_enc_full(dict)
    fix_duration = show_ITI() 

    # Record trial data
    enc_file.write('%s,%i,%i,%s,%i,%s,%s,%.3f,%i\n' %(subject,trial,block,curr_item,curr_type,curr_task,response,curr_RT,fix_duration))

    # Update trial number
    trial = trial + 1
show_break()
show_instruct(break_instructions_2) #take a break
random.shuffle(enc_lists) #shuffle the list

for dict in enc_lists: #repeat the procedure
    block = 2
    curr_task = show_task(dict)
    curr_item, curr_type, response, curr_RT = show_enc_item(dict)
    fix_duration = show_ITI() 

    # Record trial data
    enc_file.write('%s,%i,%i,%s,%i,%s,%s,%.3f,%i\n' %(subject,trial,block,curr_item,curr_type,curr_task,response,curr_RT,fix_duration))

    # Update trial number
    trial = trial + 1
enc_file.close()

for frames in range(fps):
    fix.draw()
    win.flip()
