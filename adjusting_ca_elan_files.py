#!/usr/bin/env python
# coding: utf-8

# IN THIS SECTION, WE ARE REMOVING ALL THE GAPS AND EXTRA SPACES FROM A .CA FILE

# In[79]:


file = open("2018-11-18-session_2.cha")


# In[80]:


lines = file.readlines()


# In[81]:


# this code removes a lot of (not all of) the special CA characters. THIS WRITES OVER THE EXISTING FILE
with open("2018-11-18-session_2-done.cha", "w") as f:
    # the "with open" command deals with closing the file when you're done
    for line in lines:
        if line[0:2] != "\t(":
            # lines that start with a tab mark gaps
            # let's skip those
            line = line.replace("⌉  ", "⌉ ")
            line = line.replace("⌋  ", "⌋ ")
            line = line.replace("  ⌋  ", " ⌋")
            line = line.replace("s  ","s ")
            line = line.replace(")  ", ") ")
            line = line.replace("	 ","	") 
            line = line.replace("  &", " &")
            line = line.replace(":::",":")
            line = line.replace(":::",":")
            line = line.replace("::::",":")
            # ^ there are some GailBot errors that place a gazillion colons where there should just be one
            line = line.replace("[⌈]","")
            line = line.replace("> <", "")
            line = line.replace("[>]", "")
            f.write(line)
            


# In[ ]:


THE CODE IN THIS SECTION REMOVES LINES THAT START WITH *G -- BECAUSE OF A ONE-TIME MISTAKE WHOOPS


# In[10]:


# you can ignore this code
file = open("newfile.ca")
lines = file.readlines()
with open("newfile2.ca", "w") as f:
    for line in lines:
        if line[0:2] != "*G":
            f.write(line)


# #### THE CODE BELOW TAKES .CHA FILES EXPORTED FROM ELAN AND ADJUSTING THE GAPS
# 
# The ELAN output has all gaps in a ton of decimals. .cha files should only have gaps that round to at least 300ms, and it should be formatted like (0.3)

# In[11]:


file = open("2017-10-30-session-3-gaps.cha")


# In[1]:


lines = file.readlines() 
import re 
import textwrap
    
with open("2017-10-30-session-3-gaps-done.cha", "w") as f:
    for line in lines:
        line = line.replace("  ", " ")
        line = line.replace("*REP:", "%rep:")
        # this bit is to just replace things that aren't the right format 
        
        if line[0] == "@": 
            # ^ write all the metadata
            f.write(line)
            
        elif line[0:5] == "*GAP:": 
            # all "gap" lines in files exported from ELAN stat with "*GAP"
            
            gaplength = float(line[5:10])
            # save the gap duration
            
            if gaplength <= .08:
                line = ("\t" + "LATCH" + "\n")
                f.write(line)
                # if there's less than an 80ms gap between turns, then place a latch symbol 
                
            else:
                gaplength = round(gaplength, 1)
                # round to the nearest 100ms 
                
                if gaplength >= .3:
                    # if the rounded gap length is greater than 300ms
                    
                    line = ("\t" + "(" + str(gaplength) + ")" + line[11:len(line)])
                    # write out the gap in the correct format 
                    
                    f.write(line)
        else:
            line = line.replace("  ", " ")
            f.write(line)


# # Goal: to extract FTOs. IN PROGRESS
# The plan: 
# 
# (1) Process turn one. Store the speaker, start time and end time. 
# 
# (2) Process turn two. Store the speaker, start time and end time. 
# 
# (3) Check to see whether turn two speaker = turn one speaker. If true, skip the rest. If they are different speakers, continue. 
# 
# (4) Calculate the difference in start times. If they are very similar (<80ms), then: 
# -- if this is the first and second utterances, just skip. 
# -- otherwise, compare the speaker of the second turn to the speaker of the turn before turn one. If they are different speakers, do (start time of turn two) - (end time of turn 0).
# 
# (5) otherwise, calcualte: (start time of turn two) - (end time of turn one)
# 
# (6) in a file, save: speaker of previous turn | end time of previous turn one | speaker of turn two | FTO between turn two and previous turn 

# In[2]:


# create a class so you can make utterance objects and eventually manipulate them

class Turn: 
    # initializing function 
    def __init__(self, speaker, words, start_time, end_time): 
        self.speaker = speaker
        self.words = words 
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time


# ### find-turn: 
# 
# this function creates a Turn object from a list of lines and a integer representing the turn to start off on. 
# 
# It returns the Turn object and the line number in the file. The line number is important because the function skips lines that do not start with *

# In[3]:


# this is the function that finds the next non-gap, non-@ turn 
def find_turn(n, linelist): 
    # find something that is not a "*"
    while(linelist[n][0] != "*"): 
        n = n+1
    line = linelist[n]
    speaker = line.split(":")[0]
    times = line.split("\x15")[1]
    start_time = int(times.split("_")[0])
    end_time = int(times.split("_")[1])
    words = line.split(":")[1]
    words = words.split("\x15")[0]
    return Turn(speaker, words, start_time, end_time), n


# ### calculate_fto: 
# 
# This function takes two Turns and calculates the FTO between them. You MUST input the first turn first and the second turn second.
# 
# If the speakers of the two turns are the same, this function returns -99,999 miliseconds (-99 seconds). If the speakers of the two turns are different but start at very similar times, this function returns 99,999 (99 seconds). 

# In[3]:


def calculate_fto(second, first): 
    if abs(second.start_time - first.start_time) < 80: 
        return 99999
    # elif first.speaker == second.speaker: 
    #   return -99999
    else: 
        # print(second.start_time, first.end_time, second.start_time - first.end_time)
        FTO = second.start_time - first.end_time
        return FTO


# In[4]:


def make_FTO_string(turn1, turn2, FTO, n): 
    return (str(n) + "," + turn2.speaker + "," + str(turn2.start_time) +"," + str(turn2.end_time) + "," + turn2.words + "," + str(FTO) + "," + turn1.words + "," + str(turn1.start_time) + "," + str(turn1.end_time) + "," + turn1.speaker + "\n")


# In[5]:


file = open("2018-11-06-session-3.cha")
lines = file.readlines() 
n = 0 

# create three Turns
twobefore_turn, n = find_turn(n, lines)
onebefore_turn, n = find_turn(n+1, lines)
current, n = find_turn(n+1, lines) 


# In[87]:


proportion = .3
chars_after = .3 * len(newtext)
index = len(newtext) - round(chars_after)

newtext = newtext[:index] + "⌈" + newtext[index:] + "⌉"
print(newtext)


# In[5]:


### THIS CELL WILL REPLACE OVERLAP MARKERS AND LATCHES. BUT!!! IT WILL REMOVE METADATA AND CODES. 
# MAKE SURE TO REPLACE THE METADATA AND CODES AFTER THIS, AS WELL 
# AS RUN THE FIX_BULLETS AND INDENT COMMANDS IN CLAN
import re
file = open("2017-10-30-session-3.cha")
lines = file.readlines() 
n = 0 

# create three Turns
twobefore_turn, n = find_turn(n, lines)
onebefore_turn, n = find_turn(n+1, lines)
current, n = find_turn(n+1, lines)

with open("2017-10-30-session-3-new.cha", "w") as f:
    # we only want to process twobefore at the beginning
    twobefore_turn.words = twobefore_turn.words.replace('⌉', '')
    twobefore_turn.words = twobefore_turn.words.replace('&=laughs', '')
    twobefore_turn.words = onebefore_turn.words.replace('&=Laughs', '')
    twobefore_turn.words = twobefore_turn.words.replace('⌋', '')
    twobefore_turn.words = twobefore_turn.words.replace('⌈', '')
    twobefore_turn.words = twobefore_turn.words.replace('⌊', '')
    twobefore_turn.words = twobefore_turn.words.replace(':', '')
    twobefore_turn.words = twobefore_turn.words.replace('≈', '')
    twobefore_turn.words = twobefore_turn.words.replace('  ', ' ').strip()
    
    while lines[n+1][0] != "@" and (lines[n][0] == "*"): 
        FTO = calculate_fto(onebefore_turn, twobefore_turn)
    
        # strip the turns and remove all current overlap markers    
        onebefore_turn.words = onebefore_turn.words.replace('⌉ ', '')
        onebefore_turn.words = onebefore_turn.words.replace('&=laughs', '')
        onebefore_turn.words = onebefore_turn.words.replace('&=Laughs', '')
        onebefore_turn.words = onebefore_turn.words.replace('⌋', '')
        onebefore_turn.words = onebefore_turn.words.replace('⌈', '')
        onebefore_turn.words = onebefore_turn.words.replace('⌊', '')
        onebefore_turn.words = onebefore_turn.words.replace(':', '')
        onebefore_turn.words = onebefore_turn.words.replace('≈', '')
        onebefore_turn.words = onebefore_turn.words.replace('  ',' ').strip()

        # add an overlap marker if the FTO is negative
        if (FTO < 0):
            print("line n: ", n, " has a negative FTO")
            # if FTO is negative, then the previous turn should have an overlap till the end
            # the current turn should have an overlap marker at the beginning of the turn
            # we need to calculate where the other two overlap markers belong 
            before_proportion = abs(FTO) / twobefore_turn.duration
            after_proportion = abs(FTO) / onebefore_turn.duration
            
            # before_char figures out how far into the previous turn to start the overlap 
            before_char = round(before_proportion * len(twobefore_turn.words))
            if (before_char == 0): 
                before_char = 1
                
            # after_char figures out how far into the current turn to end the overlap 
            after_char = round(after_proportion * len(onebefore_turn.words))
            if (after_char == 0): 
                after_char = 1

            # before index in the index we'll use to place the starting overlap in the first turn
            before_index = len(twobefore_turn.words) - before_char     
            
            # after_index is the index we'll use to place the ending overlap in the second turn 
            after_index = after_char
            
            # does the first turn end after the second turn? 
            if (twobefore_turn.end_time > onebefore_turn.end_time): 
                # if so, we need to figure out where to put the ending overlap 
                prop = (twobefore_turn.end_time - onebefore_turn.end_time) / twobefore_turn.duration
                yikes_index = len(twobefore_turn.words) - round(prop * len(twobefore_turn.words))
            else: 
                yikes_index = len(twobefore_turn.words)
            
            before_text = twobefore_turn.words[:before_index] + "⌈" + twobefore_turn.words[before_index:yikes_index] + "⌉" + twobefore_turn.words[yikes_index:]
            twobefore_turn.words = before_text 
            
            after_text = "⌊" + onebefore_turn.words[:after_index] + "⌋" + onebefore_turn.words[after_index:]
            #print(onebefore_turn.words)
            onebefore_turn.words = after_text 

        if (FTO < 80 and FTO > 0): 
            twobefore_turn.words = twobefore_turn.words + "≈"
            onebefore_turn.words = "≈" + onebefore_turn.words 
        
        f.write(twobefore_turn.speaker + ":\t" + twobefore_turn.words + "    " + "•" + str(twobefore_turn.start_time) + "_" + str(twobefore_turn.end_time) + "•\n")
        
        twobefore_turn = onebefore_turn
        onebefore_turn = current
        current, n = find_turn(n+1, lines)
    
    f.write(twobefore_turn.speaker + ":\t" + twobefore_turn.words + "    " + "•" + str(twobefore_turn.start_time) + "_" + str(twobefore_turn.end_time) + "•\n")
    f.write(onebefore_turn.speaker + ":\t" + onebefore_turn.words + "    " + "•" + str(onebefore_turn.start_time) + "_" + str(onebefore_turn.end_time) + "•\n")


# In[292]:


file = open("2018-11-06-session-1.cha")
lines = file.readlines() 

n = 0 
# create three Turns
twobefore_turn, n = find_turn(n, lines)
onebefore_turn, n = find_turn(n+1, lines)
current, n = find_turn(n+1, lines)

# create the .txt file and make the headers 
f = open("demofile2.txt", "a")
f.write("line," + "previousturn_speaker," + "previousturn_starttime," + "previousturn_endtime," + "previous_turn," + "FTO," + "next_turn," + "nextturn_starttime," + "nextturn_endtime," + "nextturn_speaker" + "\n")

# calculate the first FTO and add to the file 
first_FTO = calculate_fto(onebefore_turn, twobefore_turn)
if abs(first_FTO) < 90000: 
    f.write(make_FTO_string(onebefore_turn, twobefore_turn, first_FTO, n))


# In[71]:


# while the rest of the file is going on: 
while lines[n+1][0] != "@" and lines[n][0] == "*": 
    print(str(n))
    # first, calculate FTO between current and previous 
    if twobefore_turn.end_time > onebefore_turn.end_time: 
        onebefore_turn = twobefore_turn
    
    FTO = calculate_fto(current, onebefore_turn)

    # if the result is fine, add the FTO and incrementore
    if abs(FTO) < 90000: 
        print("abs FTO < 90000")
        f.write(make_FTO_string(current, onebefore_turn, FTO, n))
        print("moving on")
        twobefore_turn = onebefore_turn
        onebefore_turn = current
        current, n = find_turn(n+1, lines)
    
    # otherwise, if it's positive 99999 (they began speaking at almost exactly the same time)
    elif FTO > 90000: 
        print("FTO is greater than 90000")
        
    # then check the FTO between current and twobefore 
        FTO = calculate_fto(current, twobefore_turn)
    
    # if that result is fine, add the FTO 
        if abs(FTO) < 90000: 
            print("abs FTO 2 is < 90000")
            f.write(make_FTO_string(current, twobefore_turn, FTO, n))
            print("moving on")
            twobefore_turn = onebefore_turn
            onebefore_turn = current
            current, n = find_turn(n+1, lines)
    
        else: 
            print("abs FTO is < 90000")
            print("moving on")
            twobefore_turn = onebefore_turn
            onebefore_turn = current
            current, n = find_turn(n+1, lines)
            
    else:
        print("moving on")
        twobefore_turn = onebefore_turn
        onebefore_turn = current
        current, n = find_turn(n+1, lines)
            
# close the file
f.close()


# # GOAL: to calculate the relevant FTOs / durations for analysis
# This includes: 
# <b>FTOs</b> 
# (1) trouble source FTO
# (2) OIR FTO 
# (3) solution FTO 
# 
# <b>Durations</b>
# (4) trouble source duration
# (5) OIR duration
# (6) solution duration
# 
# <b>speaker data</b> 
# (7) trouble source speaker 
# (8) OIR speaker 
# (9) solution speaker
# 
# <b>turns</b> 
# (10) trouble source turn 
# (11) OIR turn 
# (12) solution turn
# 
# <b>metadata</b> 
# (13) file name 
# (14) line number of trouble source
# (15) 
# 
# <b>other values</b>
# overlapping talk during the trouble source that doesn't come from the trouble source (can I even analyze this?) 
# also, probability the OIR FTO comes from the general distribution of FTOs
# 
# Note: someone will have to make sure the solution is a real solution! 
# 

# In[72]:


#pip install pandas 
#pip install xlrd
import pandas as pd 
import xlrd


# In[1]:


file = open("2018-11-06-session-1.cha")
lines = file.readlines()


# In[3]:


print(lines[10])


# In[73]:


data = pd.read_excel(file)

print(data)


# In[98]:


is_OIR = data['OIR?']=="X"
OIRs = data[is_OIR]
nonOIRs = data[is_OIR== False]
nonOIR_FTOs = nonOIRs['FTO']


# In[104]:


import matplotlib.pyplot as plt
plt.hist(nonOIR_FTOs.values)


# In[109]:


nonOIR_FTOs.plot()


# In[107]:


nonOIR_FTOs.values[:]


# In[53]:


hmm["FTO"]


# In[ ]:


# if the "OIR?" file is "X", then do the following 

# get the FTO of that row (the OIR FTO)

# get the FTO of the previous row (the trouble source FTO)

# get the FTO of the next row (the solution FTOd)


# In[21]:


import os
import glob

writefile = open("trythis.txt", "a")

for filename in glob.glob('*.cha'):
    with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
        for line in f: 
            if line[0] == "*": 
                writefile.write(line)
                
        writefile.write("<|endoftext|>\n")

writefile.close()


# In[14]:


os.getcwd()


# In[ ]:




