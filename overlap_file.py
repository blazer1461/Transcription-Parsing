# Transcription with Overlap.
# export to .csv
# Purpose: Takes all .cha files from a directory and parse through the files
#          which has special characters. Output them all to a seperate new csv ile
# Date: 2/9/21
# Made by: Spencer Ha

import csv
import os
import re
from string import digits

#goes through the entire directory and takes all cha files. change the listdir
#to your dir with the cha files
def main():
    path = "cha_files/"
    filelist = os.listdir(path)


    writer_txt = open('transcribed_file_with_overlap.txt', 'w')
    #math_writer = open('overlap_calculations', 'w')
    for i in filelist:
        
        
        if i.endswith(".cha"):
            with open(path + i, 'r') as file:
                print(path + i)
                line1 = ""
                line2 = ""
                lineCounter = 1
                for line in file:
                
                    if line[0] == '*':
                        line = line.translate({ord(z): None for z in '-*≈><\t?,∆°↗⇘∬↘⁇↑Ã≤='})
                        
                        line = line_manipulation(line)
                        #print(line)
                        if len(line) < 2: 
                            continue 
                        else:
                            #this part cuts the code so that only the line and the overlap shows
                            line = line.split('"')
                            line = line[0] + line[-1]
                            line = line.replace(" %snd:"," ")
                            line = line_overlap(line)
                            if lineCounter % 2 == 1:
                                line1 = line
                            else:
                                line2 = line
                            lineCounter = lineCounter + 1
                            calculate_overlap_timing(line1, line2)
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

#next step: improve modularity. like a lot...
def line_overlap(line):
    if "⌋" in line:
        line_index = line.index("⌋")
        if line[line_index + 1] != " " and line[line_index - 1] != " ":
            space_index = line.find(" ", line_index)
            #line = line + "Fixing ⌋ error at index " + str(space_index) + "\n"
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
            #line = line + "Fixing ⌈ error at index " + str(prev_value) + "\n"

    return line 

#bug here too :(  
def calculate_overlap_timing(line1, line2):
    line1 = line1.split("_")[0]
    line2 = line2.split("_")[-1]
    firstSentenceTime = 0
    secondSentenceTime = 0
    print (line1)
    print (line2)
    return 
        



main() 
