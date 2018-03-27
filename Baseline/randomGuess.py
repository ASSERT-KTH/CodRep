import os
import glob
import random
import sys
import getopt

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hk:")
    except getopt.GetoptError:
        print("randomGuess.py -k <Top k prediction>")
        sys.exit()
    for opt, arg in opts:
        if opt == "-h":
            print("randomGuess.py -k <Top k prediction>")
            sys.exit()
        elif opt in ("-k"):
            try:
                k = int(arg)
            except ValueError:
                print("k must be integer")
                sys.exit()

    path_files = "../Files"
    for filename in glob.glob(os.path.join(path_files, "*.txt")):
        with open(filename, 'r') as file:
            length = len(file.readlines()) - 2
            try:
                guess = random.sample(list(range(1,length+1)), min(length, k))
            except UnboundLocalError:
                print("randomGuess.py -k <Top k prediction>")
                sys.exit()
            guess_string = ""
            for line in guess:
                guess_string = guess_string + str(line) + " "
            print(os.path.basename(filename) + " " + guess_string)

if __name__=="__main__":
    main(sys.argv[1:])
