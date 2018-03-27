import os
import glob
import sys

def main():
    path_files = "../Files"
    for filename in glob.glob(os.path.join(path_files, "*.txt")):
        with open(filename, 'r') as file:
            length = len(file.readlines()) - 2
            print(os.path.basename(filename) + " " + str(length))

if __name__=="__main__":
    main()
