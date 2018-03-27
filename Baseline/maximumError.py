import os
import glob
import random

def maximumError(program_length, solution_line):
    if(solution_line-1 > program_length-solution_line):
        return 1
    else:
        return program_length

def main():
    path_files = "../Files"
    for filename in glob.glob(os.path.join(path_files, "*.txt")):
        with open(filename, 'r') as file:
            with open(filename.replace("Files", "Solutions"), "r") as solution:
                lines = file.readlines()
                # Since first two lines are not part of the program
                program_length = len(lines)-2
                solution_line = int(solution.readline())
                print(os.path.basename(filename) + " " + str(maximumError(program_length,solution_line)))

if __name__=="__main__":
    main()
