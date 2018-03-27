import sys
import math

class LineOutOfRangeException(Exception):
    pass

def lossFunction(guess, solution):
    #return abs(solution-guess)
    return math.tanh(0.3*abs(solution-guess))

def main():
    k = 0 # Maximum number of solutions received

    path_files = "../Files/"
    path_solutions = "../Solutions/"

    total_files = 0
    correct_files = 0
    loss = 0

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

            for answer in answers:
                if(answer < 1 or answer > code_file_length):
                    raise LineOutOfRangeException("Line number out of range for file " + filename + "." +
                    " Expected: 1<={line}<=" + str(code_file_length) + ", found: " + answer)

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

            total_files+=1
            loss+=min_loss

            code_file.close()
            solution_file.close()
        except ValueError:
            print(answer + " should be integer")
            raise
        except IOError:
            print(filename + " does not exist!")
            raise

    print("Total files: " + str(total_files))
    print("Average line error: " + str(loss/(total_files*1.0)) + " (the lower, the better)")
    print("Top " + str(k) + " accuracy: " + str(correct_files/(total_files*1.0)) + " (the higher, the better)")

if __name__=="__main__":
    main()
