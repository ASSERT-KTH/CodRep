import sys
import glob
import math
import getopt
import os.path

# Total number of files in chosen datasets
total_files = 0
# Default score of all prediction
score = {}
# Number of correct predictions
correct_files = 0
# Number of correct predictions in your top-1 predictions
correct_files_top1 = 0
# All prediction outputs by your algorithm
all_predictions = {}
# Maximum number of preditions received
k = 0

# When prediction is out of range
class LineOutOfRangeException(Exception):
    pass

# When predicting files outside of chosen datasets
class DatasetsNotChosenException(Exception):
    pass

def lossFunction(guess, solution):
    # Loss function, more information in README
    return math.tanh(abs(solution-guess))

# Count files
def countTasks(chosen_datasets):
    count = 0

    if(chosen_datasets):
        for path_to_dataset in chosen_datasets:
            path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
            for task in os.listdir(path_to_tasks):
                if(task.endswith(".txt")):
                    count += 1
    else:
        path_to_eval = os.path.abspath(os.path.dirname(__file__))
        path_to_datasets = os.path.join(path_to_eval, "../Datasets/")

        for dataset_dir in os.listdir(path_to_datasets):
            path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
            if(os.path.isdir(path_to_dataset)):
                path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
                for task in os.listdir(path_to_tasks):
                    if(task.endswith(".txt")):
                        count += 1

    return count

# Init score for files, default score is 1 for each file
def initScore(chosen_datasets):
    score = {}

    if(chosen_datasets):
        for path_to_dataset in chosen_datasets:
            path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
            for task in os.listdir(path_to_tasks):
                if(task.endswith(".txt")):
                    score[os.path.abspath(os.path.join(path_to_tasks, task))] = 1
    else:
        path_to_eval = os.path.abspath(os.path.dirname(__file__))
        path_to_datasets = os.path.join(path_to_eval, "../Datasets/")

        for dataset_dir in os.listdir(path_to_datasets):
            path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
            if(os.path.isdir(path_to_dataset)):
                path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
                for task in os.listdir(path_to_tasks):
                    if(task.endswith(".txt")):
                        score[os.path.abspath(os.path.join(path_to_tasks, task))] = 1

    return score

# Check the answers against the solution
def checkAnswers(answers, path_to_task, chosen_datasets):
    global score, correct_files, correct_files_top1

    try:
        task = open(path_to_task, "r")
    except IOError:
        print(path_to_task + " does not exist!")
        raise
    # If task exists, then solution should also exists
    solution = open(path_to_task.replace("Tasks", "Solutions"), "r")

    # Ignore first two lines since they are not part of the program
    source_program_length = len(task.readlines()) - 2

    # Check if the task if inside of chosen datasets
    if(chosen_datasets):
        isInChosenDatasets = False
        for path_to_dataset in chosen_datasets:
            if(path_to_dataset in path_to_task):
                isInChosenDatasets = True
        if(not isInChosenDatasets):
            raise DatasetsNotChosenException(path_to_task + " is outside of chosen datasets.")

    # Check if answers are in range
    for answer in answers:
        if(answer < 1 or answer > source_program_length):
            raise LineOutOfRangeException("Line number out of range for file " + path_to_task + "." +
            " Expected: 1<={line}<=" + str(source_program_length) + ", found: " + answer)

    # Read the solution
    sol = int(solution.readline())

    # Use minimum loss among all answers to calculate loss
    min_loss = float('Inf')
    for answer in answers:
        # Correct answer should have minimum loss, therefore we can break
        if(lossFunction(answer, sol) < min_loss):
            min_loss = lossFunction(answer, sol)
        if(sol == answer):
            correct_files+=1
            break

    # Number of prefect prediction in your top-1 prediction
    if(sol == answers[0]):
        correct_files_top1+=1

    # Update the new score
    score[path_to_task]=min_loss

    task.close()
    solution.close()

# Print neccesary statistics
def printStatistics(verbose):
    global total_files, score, correct_files, all_predictions, k
    print("Total files: " + str(total_files))
    print("Average line error: " + str(sum(score.values())/(total_files*1.0)) + " (the lower, the better)")
    print("Recall@1: " + str(correct_files_top1/(total_files*1.0)) + " (the higher, the better)")
    print("Recall@" + str(k) + ": " + str(correct_files/(total_files*1.0)) + " (the higher, the better)")

def main():
    global total_files, score, correct_files, all_predictions, k

    verbose = False #TODO, verbose mode?
    chosen_datasets = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:vh", ["datasets=","help"])
    except getopt.GetoptError:
        raise
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt in ("-d", "--datasets"):
            chosen_datasets = arg.split(":")
        elif opt in ("-h", "--help"):
            print("usage evaluate.py [-vh] [-d path] [--datasets=path] [--help]")
            print("-v for verbose output mode")
            print("-d or --datasets= to evaluate on chosen datasets, must be absolute path, multiple paths should be seperated with ':'. Default is evaluating on all datasets")
            sys.exit()

    total_files = countTasks(chosen_datasets)
    score = initScore(chosen_datasets)

    for args in sys.stdin:
        inputs = args.split()
        path_to_task = inputs[0]
        answers = inputs[1:]
        all_predictions[path_to_task] = answers
        try:
            answers = answers = [int(answer) for answer in answers]
        except ValueError:
            print(answers + " should be integers!")
            raise
        if(len(answers) > k):
            k = len(answers)
        checkAnswers(answers, path_to_task, chosen_datasets)

    printStatistics(verbose)

if __name__=="__main__":
    main()
