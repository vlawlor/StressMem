# Last updated: Feburary 13, 2017
# Authors: Victoria Lawlor, Elyssa Barrick, and Dan Dillon
# Runs encoding for the StressMem experiment.

# User, you may need/want to edit the next several lines
import getpass, os, random, sys
refresh = 16.7
userName = getpass.getuser()
monitorName = 'Dan Mac'
path2words = '/Users/' + userName + '/Work/Expts/StressMem/PsychoPy/Stimuli/'
path2data = '/Users/' + userName + '/Work/Expts/StressMem/Data/'

# Shouldn't need to edit below . . . 
import numpy as np
import pandas as pd
from random import shuffle
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, data, event, gui, misc, sound, visual

#print (pd.__version__)
#print (sys.version)
#print (sys.path)

# GUI for subject number and date
try:
    expInfo = misc.fromFile('StressMemlastParams.pickle')
except:
    expInfo = {'SubjectID':'999' }
expInfo['Date'] = data.getDateStr()

dlg = gui.DlgFromDict(expInfo, title='StressMem', fixed=['Date'])
if dlg.OK:
    misc.toFile('StressMemLastParams.pickle', expInfo) 
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
task = visual.TextStim(win, text = 'XX', font='Arial', height = 0.20, pos = (0.0,0.3), wrapWidth = 50, color = '#129066') # just a darker shade of #1bce92
word = visual.TextStim(win, text='XXX', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')
choice = visual.TextStim(win, text = '_______', font='Arial', height = 0.15, pos = (0.0,-0.29), wrapWidth = 50, color = '#ff6542', bold=True)
options = visual.TextStim(win, text = 'XXXX', font='Arial', height = 0.15, pos = (0.0,-0.27), wrapWidth = 50, color = '#ff6542', bold=True)
no_resp = visual.TextStim(win, text='NO RESPONSE!', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = 'black')
begin_typing = visual.TextStim(win, text='Begin Typing', font='Arial', height = 0.20, pos = (0,0), wrapWidth = 50, color = '#1B1C96')

key_sound = sound.SoundPygame('resp.wav')
stim_sound = sound.SoundPygame('stim.wav')

# Create and save the encoding lists
df = pd.read_csv(path2words + 'balanced_words.csv')
df = df[['Word','val']]
df.rename(columns={'Word':'word', 'val':'valence'}, inplace=True)

df_neg = df[df.valence == 0] # getting the negative words that will be shown this session
df_neg_encode = df_neg.iloc[np.random.permutation(len(df_neg))] 
df_neg_encode = df_neg_encode.head(50) # shuffle the negatives, then get the first 50

df_pos = df[df.valence == 1] # getting the positive words that will be shown this session
df_pos_encode = df_pos.iloc[np.random.permutation(len(df_pos))]
df_pos_encode = df_pos_encode.head(50) # shuffle the positives, then get the first 50 

df_encoded = df_neg_encode.append(df_pos_encode)
df_encoded = df_encoded.reset_index(drop = True)
df_encoded['question'] = 'Describes?' # Let's keep both tasks to a single word, same reading burden and limits eye movements.
df_encoded.ix[0:24, 'question'] = 'Emotion?'
df_encoded.ix[50:74, 'question'] = 'Emotion?' # add the questions so that there is a 50/50 ratio for neg and pos words

df_encoded.to_csv(path2data + 'Encoded_words/encoded_words_' + subject + '.csv', index=False) # saving the words and questions
enc_lists = df_encoded.T.to_dict().values() # turn them into lists of dicts
random.shuffle(enc_lists) # shuffles the list of dicts

# Flips per second; will be updated in case of refresh rate changes
fps = int(np.ceil(1000/refresh))
half_sec = int(0.5*fps)

# Clocks
RT = core.Clock()

#Functions
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

def show_enc_item(in_dict):
    '''Display encoding item and encoding task for 3 seconds'''
    question = in_dict['question']
    curr_item = in_dict['word']
    task.setText(text=question)
    word.setText(text=curr_item)
    word.setPos(newPos=(0,0))

    if question == 'Describes?':
        curr_task = 'Describes'
        options.setText('Yes     No')
    elif question == 'Emotion?':
        curr_task = 'Emotion'
        options.setText('Positive     Negative')
    stim_sound.play()
    for frame in range(6*half_sec):
        word.draw()
        task.draw()
        fix.draw()
        win.flip()

    return curr_item

def show_task(in_dict):
    '''Present encoding task for 1000 ms'''

    question = in_dict['question']
    task.setText(text=question)

    if question == 'Describes?':
        curr_task = 'Describes'
        options.setText('Yes             No')
    elif question == 'Emotion?':
        curr_task = 'Emotion'
        options.setText('Positive             Negative')

    for frame in range(1*fps):
        task.draw()
        fix.draw()
        win.flip()

    return curr_task

def show_enc_full(in_dict):
    '''Display encoding item, encoding task, and options for 10 seconds or until response'''

    response = 'no_response'
    curr_RT = 999.0
    question = in_dict['question']
    curr_item = in_dict['word']
    curr_type = in_dict['valence']
    word.setText(text=curr_item)
    choice.setColor('#ff6542')
    advance = 'false'
    
    word.setPos(newPos=(0,0))
    
    event.clearEvents()
    RT.reset()
    allKeys = []
    frame = 0
    
    while frame < (10*fps) and advance == 'false':
        allKeys = event.getKeys(keyList=[key_1, key_5, quit_key],timeStamped=RT)
        task.draw()
        word.draw()
        fix.draw()
        options.draw()
        win.flip()
        
        if allKeys:
            enc_resp = allKeys[0][0]
            curr_RT = allKeys[0][1]

            if enc_resp == key_1:
                advance = 'true'
                key_sound.play()
                frame = 0
                if question == 'Emotion?':
                    response = 'positive'
                    choice.setText('_______')
                    choice.setPos(newPos=(-0.34, -0.27))
                    advance = 'true'
                if question == 'Describes?':
                    response = 'yes'
                    choice.setText('___')
                    choice.setPos(newPos=(-0.21, -0.27))
                    advance = 'true'
                while frame < (4*half_sec):
                    task.draw()
                    word.draw()
                    fix.draw()
                    options.draw()
                    choice.draw()
                    win.flip()
                    frame = frame + 1
                    
            elif enc_resp == key_5:
                advance = 'true'
                key_sound.play()
                frame = 0
                if question == 'Emotion?':
                    response = 'negative'
                    choice.setText('________')
                    choice.setPos(newPos=(.31, -.27))
                if question == 'Describes?':
                    response = 'no'
                    choice.setText('___')
                    choice.setPos(newPos=(.24, -.27))
                while frame < (4*half_sec):
                    task.draw()
                    word.draw()
                    fix.draw()
                    options.draw()
                    choice.draw()
                    win.flip()
                    frame = frame + 1

            elif enc_resp == quit_key:
                core.quit()

        frame = frame + 1
    return (curr_type, response, curr_RT)

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

def show_no_resp():
    '''Show the text "no response"'''
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

# Instructions
enc_instructions = ['Welcome!\n\nIn this task, words will appear on the screen in front of you. \
\n\nAfter each word is presented, you will be asked one of two questions about \nthe word, and you will respond by pressing a button.\
\n\nPress button 1 to advance.',  
'If you are asked about emotion, select whether you think the word is more positive or negative. \
\n\nPress button 1 to advance.',
'If you are asked if a word describes you, answer yes or no based on whether or not you think the word describes \
or relates to you. \
\n\nPress button 1 to advance.',
'\n\nThere are 2 blocks of trials, with a short break between the blocks. \
\n\nPress button 1 to begin the practice trials.']
final_enc_instructions = ['Do you have any final questions?\n\nIf not, press 1 to begin the task']

break_instructions = 'Good job! You are halfway through this task. \
\n\nThis screen will advance after a short break, and then you will be able to advance to the second half of the task when you are ready.'

break_instructions_2 = ['Press 1 to begin the second half of the task']

recall_instructions = ['Great job! You are finished with that portion of the task. \n\n \
On the next screen, please type all of the words that you can remember seeing from the previous part of \
the task. You may hit space to start a new word, and enter when you have reached the end of the line.\n\n \
Press the "escape" key when you have finished typing all of the words that you can remember. \n\n \
Press 1 to begin.']

end_instructions = ['Great job! You are finished with this task.\n\nThe experimenter will be in shortly']

# Practice Stimuli
pract1 = {'word': 'faker', 'valence' : '1', 'question': 'Emotion?'}
pract2 = {'word': 'generous', 'valence' : '1', 'question': 'Describes?'}
pract3 = {'word': 'loner', 'valence' : '1', 'question': 'Describes?'}
pract4 = {'word': 'thoughtful', 'valence' : '1', 'question': 'Emotion?'}
pract_trials = [pract1, pract2, pract3, pract4]

# Begin practice trials
show_instruct(enc_instructions)

for dict in pract_trials:
    curr_task = show_task(dict)
    curr_item = show_enc_item(dict)
    curr_type, response, curr_RT = show_enc_full(dict)
    if curr_RT == 999.0:
        show_no_resp()
    fix_duration = show_ITI() 
show_instruct(final_enc_instructions)

# RUN EXPERIMENTAL TRIALS

# Open output file for writing the encoding data
enc_file = expInfo['SubjectID'] + '_' + expInfo['Date']
enc_file = open(path2data + enc_file+'_StressMem_enc' +'.csv', 'w')
enc_file.write('subject,trial,block,word,val,task,response,RT,iti_dur(ms)\n')

# Start with 5 seconds of fixation to let the person settle in
for frame in range(10*half_sec):
    fix.draw()
    win.flip()

# Run the trials
trial = 1
for dict in enc_lists:
    block = 1
    curr_task = show_task(dict)
    curr_item = show_enc_item(dict)
    curr_type, response, curr_RT = show_enc_full(dict)
    if curr_RT == 999.0:
        show_no_resp()
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
    curr_item = show_enc_item(dict)
    curr_type, response, curr_RT = show_enc_full(dict)
    if curr_RT == 999.0:
        show_no_resp()
    fix_duration = show_ITI() 

    # Record trial data
    enc_file.write('%s,%i,%i,%s,%i,%s,%s,%.3f,%i\n' %(subject,trial,block,curr_item,curr_type,curr_task,response,curr_RT,fix_duration))

    # Update trial number
    trial = trial + 1
enc_file.close()

# FREE RECALL

# Set up a file to hold the free recall data.
recall_file = expInfo['SubjectID'] + '_' + expInfo['Date']
recall_file = open(path2data + recall_file+'_Recall' +'.csv', 'w')
recall_file.write('')

# Run the recall phase . . . 
show_instruct(recall_instructions)
free_recall()
recall_file.close()
show_instruct(end_instructions)