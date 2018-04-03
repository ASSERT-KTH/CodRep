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

    path_to_current = os.path.abspath(os.path.dirname(__file__))
    path_to_datasets = os.path.join(path_to_current, "../Datasets/")

    for dataset_dir in os.listdir(path_to_datasets):
        path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
        if(os.path.isdir(path_to_dataset)):
            path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
            for task in os.listdir(path_to_tasks):
                if(task.endswith(".txt")):
                    path_to_task = os.path.abspath(os.path.join(path_to_tasks, task))
                    with open(path_to_task, 'r') as file:
                        length = len(file.readlines()) - 2
                        try:
                            # Random guess
                            guess = random.sample(list(range(1,length+1)), min(length, k))
                        except UnboundLocalError:
                            print("randomGuess.py -k <Top k prediction>")
                            sys.exit()
                        guess_string = ""
                        for line in guess:
                            guess_string = guess_string + str(line) + " "
                        print(path_to_task + " " + guess_string)

if __name__=="__main__":
    main(sys.argv[1:])
