# Transcription with Overlap.
# 
# Purpose: Takes all .cha files from a directory and parse through the files
#          which has special characters. Also calculates overlap timing and #          manipulates them in the program.
# Date: 3/18/21
# Made by: Spencer Ha

import csv
import os
import re
from string import digits

#goes through the entire directory and takes all cha files. change the listdir
#to your dir with the cha files
def main():
    #prompts the user to edit the character change rate when speaking
    timing_prompt = input("Character Change rate? Lower means more chars moved ")
    path = "cha_files/"
    filelist = os.listdir(path)


    writer_txt = open('transcribed_file_with_overlap.txt', 'w')
    #math_writer = open('overlap_calculations', 'w')
    for i in filelist:
        
        
        if i.endswith(".cha"):
            with open(path + i, 'r') as file:
                print(path + i)
                
                lineCounter = 1
                for line in file:
                    line1 = ""
                    line2 = ""
                    if line[0] == '*':
                        line = line.translate({ord(z): None for z in '-*≈><\t?,∆°↗⇘∬↘⁇↑Ã≤='})
                        
                        line = line_manipulation(line)
                        if len(line) < 2: 
                            continue 
                        else:
                            #this part cuts the code so that only the line and the overlap show
                            line = re.sub('".*?"', '', line)
                            line = line.replace(" %snd:"," ")
                            #line = line_overlap(line)
                            #Allows for us to have two lines that are one after the other which we would push into the calculate_overlap_timing function. This is so important because we have to use TWO lines to calculate any overlap.
                            if lineCounter % 2 == 1:
                                line1 = line
                            else:
                                line2 = line
                            lineCounter = lineCounter + 1
                            calculate_overlap_timing(line1, line2)
                            #temp for now. once i get overlap timing to work this is an easy fix
                            timing = -800
                            #
                            line = overlaptiming(line, timing, int(timing_prompt))
                            writer_txt.writelines(line)
                            
def line_manipulation(line):
    
    line = line.replace(":", ": ")
    line = line.strip()
    # removes all whitespace around the line (important to do this BEFORE adding the \n, after removing overlaps)                    
    line = line + "\n"
    #removes all ⌈⌋⌊⌉().*
    line = line.replace("  ", " ")
    line = line.replace("Mhmm", "mhm")
    line = line.replace("uhm", "um")
    return line



#PROBLEMS HERE :(  
def calculate_overlap_timing(line1, line2):
   
   # remove all non digits and non underscore from the line so that only overlap timing appears
    line1 = re.sub("[^0-9_]", "", line1)
    line2 = re.sub("[^0-9_]", "", line2)
    line1 = line1.split("_") [-1]
    line2 = line2.split("_") [1:-1]
    #You can see the problem here! We have line 2 in an array and there are some arrays that are completely empty which makes it so that it is exteremly hard to index and convert these from string to integers. 
    print (line1)
    print (line2)


    
    return  
        
def overlaptiming(line, timing, user_inputted_timing):
    if timing < 0:
        if "⌋" in line:
            #uses the timing (which at the current moment is hard coded) and the user inputted timing to determine how many chars to move
            char_moved = abs(timing) / user_inputted_timing          
            line_index = line.index("⌋")
            line = line + "Fixing ⌋ error at index " + str(line_index) + "\n"
            #adds the new ⌋ after moving chars
            line = line[:int(line_index + char_moved)] + "⌋" +line[int(line_index + char_moved):]
            #removing old ⌋
            line = line[:line_index] + line[line_index+1:]
            
    return line



main() 



#not needed for now
""" def line_overlap(line):
    if "⌋" in line:
        line_index = line.index("⌋")
        if line[line_index + 1] != " " and line[line_index - 1] != " ":
            space_index = line.find(" ", line_index)
            line = line + "Fixing ⌋ error at index " + str(space_index) + "\n"
            line = line[:space_index] + "⌋" +line[space_index:]
            line = line[:line_index] + line[line_index+1:]
        elif line[line_index - 1] == " ":
            line = line[:line_index-1] + "⌋" +line[line_index-1:]
            line = line[:line_index] +line[line_index+1:]
    #bug here --> fixes needed
    if "⌈" in line:
        line_index = line.index("⌈")
        prev_value = 0
        if line[line_index - 1] != " ":
            for findIndex in re.finditer(" ", line):
                if findIndex.start() > line_index:
                    break
                prev_value = findIndex.end()

                
            line = line = line[:prev_value] + "⌈" +line[prev_value:]
            line = line[:line_index+1] + line[line_index+2:]
            line = line + "Fixing ⌈ error at index " + str(prev_value) + "\n"

    return line  """