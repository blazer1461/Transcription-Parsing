# create a class so you can make utterance objects and eventually manipulate them

class Turn:
    # initializing function
    def __init__(self, speaker, words, start_time, end_time):
        self.speaker = speaker
        self.words = words
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        
        
# this is the function that finds the next non-gap, non-@ turn
import re

def find_turn(n, linelist):
# find something that is not a "*"
        while(linelist[n][0] != "*"):
            n = n+1
        line = linelist[n]
        speaker = line.split(":")[0]
        times = line.split("\x15")[1]
        start_time = int(times.split("_")[0])
        end_time = int(times.split("_")[1])
        #words = line.split("    ")[1]
        words = line.replace(" . "," ")
        words = words.split("\x15")[0]
        words = words.strip()
        return Turn(speaker, words, start_time, end_time), n # n is sort of like line number

def calculate_start_difference(first, second):
    # The second turn start time will always be later than the first turn start time
    # this will just tell us by how much
    difference = second.start_time - first.start_time
    return difference

def calculate_end_difference(first, second):
    # we will calculate second turn end time - first turn end time
    # if this is a positive value, the second turn ends after the first turn ends
    # otherwise, the second turn ends before the first turn,
    # (and the bottom end marker should be at the end of the second turn)
    difference = second.end_time - first.end_time
    print("raw end difference is: ", difference)
    return difference

def is_overlapped(first, second):
    # there is an overlap if the second turn begins before the first turn ends
    # so second start time will be smaller than first turn end time
    return second.start_time < first.end_time




def make_line(line):
    # write the line in .cha format
    #take out next line.speaker part?
    new_line = line.words + '   \x15' + str(line.start_time) + '_' + str(line.end_time) + '\x15' + '\n'
    # print("writing: ", new_line)
    return new_line



def starting_overlaps(line1, line2):
       # if there is an overlap:
       if is_overlapped(line1, line2):
           
           # calculate the difference in start times
           start_dif = calculate_start_difference(line1, line2)
           
           # calculates the proportion of line1 that happens before the top left marker
           prop = start_dif / line1.duration
           
           # calculates the number of characters that occur before the top left marker
           top_left = round(prop * len(line1.words))
           
           # handles an edge case
           if top_left - len(line1.words) < 3:
               top_left = top_left - 1
           
           # places the top overlap character
           line1.words = line1.words[0:top_left] + '⌈' + line1.words[top_left:]
           
           # line 2 will always start with the bottom left marker (because line 2 always
           # starts after line 1)
           line2.words = '⌊' + line2.words



def ending_overlaps(line1, line2):
    if is_overlapped(line1, line2):
        end_dif = calculate_end_difference(line1, line2)
        print("end_dif is: ", end_dif)
    
    # if end_dif is positive, that means that turn2 ends after turn1 end
        if(end_dif > 0):
            line1.words = line1.words + '⌉'
            prop = end_dif / line2.duration
            bottom_right_calc = round(prop * len(line2.words))
            print("bottom_right is: ", bottom_right_calc)
            if bottom_right_calc - len(line2.words) < 2:
                bottom_right_calc = bottom_right_calc - 2
        
            bottom_right = len(line2.words) - bottom_right_calc
        
            line2.words = line2.words[0:bottom_right] + '⌋' + line2.words[bottom_right:]
    
    # if end_dif is negative, that means that turn2 ends before turn1 ends
        else:
            end_dif = abs(end_dif)
            line2.words = line2.words + '⌋'
            prop = end_dif / line1.duration
        
            top_right_minus = round(prop * len(line1.words))
            top_right = len(line1.words) - top_right_minus
        
            if top_right - len(line1.words) < 2:
                top_right = top_right - 1
            
        
            line1.words = line1.words[0:top_right] + '⌉' + line1.words[top_right:]



# step 1: set up the previous turn
# that turn will serve as memory, and that's it??
# does this make sense?
# we will only write the "middle_turn" to the file

import re
input_file = input("Which file do you want to open: ")
output_file = input("Which file do you want to output to (do not include .cha tag): ")
file = open("cha_files/" + input_file)
lines = file.readlines()
n = 0
counter = 0

writer_txt = open(output_file+ '.cha', 'w')

for line in lines:
    if line[0] in '@%    ':
        writer_txt.writelines(line)

oldest_turn, n = find_turn(n, lines)
middle_turn, n = find_turn(n+1, lines)

oldest_turn.words = oldest_turn.words.translate({ord(z): None for z in '⌈⌉⌋⌈⌊'})
middle_turn.words = middle_turn.words.translate({ord(z): None for z in '⌈⌉⌋⌈⌊'})

#if(is_overlapped(oldest_turn, middle_turn)):
starting_overlaps(oldest_turn, middle_turn)
#print(oldest_turn.words)
#print(middle_turn.words)

ending_overlaps(oldest_turn, middle_turn)
#print(oldest_turn.words)
#print(middle_turn.words)

writer_txt.writelines(make_line(oldest_turn))



while n < len(lines):
    try:
        # print("n is: ", n)
        newest_turn, n = find_turn(n+1, lines)
        newest_turn.words = newest_turn.words.translate({ord(z): None for z in '⌈⌉⌋⌈⌊'})
        
        # now we have to see if middle_line also overlaps with newest_line
        # print("BEFORE OVELAPS: ")
        # print("middle turn: ", middle_turn.words)
        #print("new turn: ", newest_turn.words)
        
        starting_overlaps(middle_turn, newest_turn)
        
        #print("AFTER STARTING OVERLAPS: ")
        #print("middle turn: ", middle_turn.words)
        #print("new turn: ", newest_turn.words)
        
        ending_overlaps(middle_turn, newest_turn)
        
        #print("AFTER ENDING OVERLAPS: ")
        #print("middle turn: ", middle_turn.words)
        #print("new turn: ", newest_turn.words)
    
        # write middle_turn, save it as oldest_turn
        writer_txt.writelines(make_line(middle_turn))
        
        oldest_turn = middle_turn
    
        # make newest_line middle_line (turn2 becomes turn2)
        middle_turn = newest_turn
        
    except:
        #print("file done!")
        n = n * 100

#writer_txt.writelines(make_line(newest_turn))
writer_txt.writelines("@End")
