# First Draft Transciption.
# transciption_main.py
# Purpose: Takes all .cha files from a directory and parse through the files
#          which has special characters. Output them all to a seperate new text #          file
# Date: 2/9/21
# Made by: Spencer Ha

import os

#goes through the entire directory and takes all cha files. change the listdir
#to your dir with the cha files
path = "/Users/spencer/Desktop/Transcription-Parsing/cha_files/"
filelist = os.listdir(path)

writer= open('transcribed_file.txt', 'w') 
for i in filelist:
    if i.endswith(".cha"):
        with open(path + i, 'r') as file:
            writer.write("File being transcribed is " + str(i) + "\n")
            for line in file:
                if line.startswith('@'):
                    continue
                #removes all characters after the '%'. Can change if needed
                sep = '%'
                line = line.split(sep, -1)[0] + '\n'
                writer.writelines(line)
            writer.write("\n")

            
            



