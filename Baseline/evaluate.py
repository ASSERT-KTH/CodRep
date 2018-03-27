import sys
import glob
import math

class LineOutOfRangeException(Exception):
    pass

def lossFunction(guess, solution):
    return math.tanh(abs(solution-guess))

def main():
    k = 0 # Maximum number of solutions received

    path_files = "../Files/"
    path_solutions = "../Solutions/"

    # All txt files, ignore other file extension such as hidden files
    all_files = glob.glob1(path_files, "*.txt")

    total_files = len(all_files)
    correct_files = 0

    # Init loss of each file as maximum, x ->inf, tanh(x) -> 1
    score = {}
    for filename in all_files:
        score[filename] = 1

    for args in sys.stdin:
        inputs = args.split()
        filename = inputs[0]
        answers = inputs[1:]
        answers = [int(answer) for answer in answers]
        # Use maximum number of returned answer to show top k acc
        if(len(answers) > k):
            k = len(answers)
        try:
            code_file = open(path_files+filename, "r")
            solution_file = open(path_solutions+filename, "r")

            # Ignore first two lines since they are not part of the program
            code_file_length = len(code_file.readlines())-2

            # Check if answers are in range
            for answer in answers:
                if(answer < 1 or answer > code_file_length):
                    raise LineOutOfRangeException("Line number out of range for file " + filename + "." +
                    " Expected: 1<={line}<=" + str(code_file_length) + ", found: " + answer)

            # Read the solution
            solution = solution_file.readline()
            solution = int(solution)

            # Use minimum loss among all answers to calculate loss
            min_loss = float('Inf')
            for answer in answers:
                # Correct answer should have minimum loss, therefore we can break
                if(lossFunction(answer, solution) < min_loss):
                    min_loss = lossFunction(answer, solution)
                if(solution == answer):
                    correct_files+=1
                    break

            # Update the new score
            score[filename]=min_loss

            code_file.close()
            solution_file.close()
        except ValueError:
            print(answer + " should be integer")
            raise
        except IOError:
            print(filename + " does not exist!")
            raise
    print(str(sum(score.values())))
    print(str(total_files))
    print("Total files: " + str(total_files))
    print("Average line error: " + str(sum(score.values())/(total_files*1.0)) + " (the lower, the better)")
    print("Top " + str(k) + " accuracy: " + str(correct_files/(total_files*1.0)) + " (the higher, the better)")

if __name__=="__main__":
    main()
