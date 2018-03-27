# The CodRep Competition

This competition is about predicting source Code Replacement (CodRep) changes.

As input, you are given a pair (Java line, Java file) and as output you give a line number corresponding to the line to be replaced by in the file.

## Submission format

To play in the competition, you have to submit a program which takes as input, a pair (Java line, Java file), and outputs on the console, the predicted line numbers (line number starts from 1!). Several line numbers can be predicted if the tool is not 100% sure of the prediction. The loss function of the competition in takes this into account.

```
<FileName> <line numer>
<FileName1> <line numer> <line numer>
<FileName2> <line numer>
```

E.g.;
```
1.txt 42
2.txt 78 526
...
```

## Folder structure and input format

The provided data is `Files/*.txt`. The txt files are in a format that has been designed to be super easy to parse.
Each file contains:
```
{Code line to insert}
\newline
{The program}
```

In the example below of data file `foo.txt`, `double b = 0.1` is the code line to be added somewhere in the file in place of another line.
```
double b = 0.1

public class test{
  int a = 1
  int b = 0.1
}
```

If your program output `foo.txt 3`, it means replace line 3 (`int b = 0.1`) with the new code line `double b = 0.1`.

For each data file , the correct answer is given in folder `Solutions/`,  e.g. the correct answer to `Files/1.txt` is in `Solutions/1.txt`

## The dataset

The data in the competition is taken from [here](https://github.com/monperrus/real-bug-fixes-icse-2015/), which consist of bug fixes in the [Apache software foundation](http://apache.org) extracted by Hao Zhong and Zhendong Su and analysed in [*An Empirical Study on Real Bug Fixes*](http://stap.sjtu.edu.cn/images/8/86/Icse15-bugstudy.pdf). They claim that
> ..., and most Apache projects carefully maintains the link between bug reports and bug fixes...

We extracted all the one line replacement changes from the dataset and filter it further based on the following criteria:
* Only Java files
* Not only comment changes, but changes like 'int a = 1' to '//int a = 1' are possible, and verse versa
* Inserted or removed line are not empty lines. Meaning that the inserted code line are not empty line, and the replaced code line are not empty line either
* No test files


## Loss function

The loss, or average line error, outputs by `evaluate.py`, is a measurement on how well your program performs on the competition. The lower the average line error is, the better are your predictions. The loss function was designed with following properties in mind:
* 0 loss when your prediction is perfect
* Constant loss even when your prediction is far away (The maximum loss is bounded)
* Logarithmic curve between 0 and the constant so that the loss function outputs loss in the same magnitude when predictions are equally bad (Deviation of 50 or 100 lines are both equally bad!). And small gain if your prediction are really close (Since some code replacement are insensitive to locations, e.g. importing modules).
* Symmetric, continuous and differentiable

When comparing different algorithms, the outputs of average line error should be compared, not the accuracy. Since the accuracy is just a 0-1 loss function.

The loss function we used is tanh(abs({predicted line}-{correct line})). And the average line error is calculated as the average of all loss. The range of tanh(abs(x)) is between 0 and 1, meaning maximum loss from a prediction is 1. By using bounded range, we also assure that we do not punish prediction on longer files, since the maximum loss is always 1. One example of advantages of using tanh(abs(x)) is illustrated in **Base line systems**


## Base line systems

We provide 5 stupid systems for illustrating our to parse the data, and having a baseline performance. These are:
* `guessFirst.py`: Always predict the first line
* `guessMiddle.py`: Always predict the line in the middle
* `guessLast.py`: Always predict the last line
* `randomGuess.py`: Predict random line, can take as argument number of outputs
* `maximumError.py`: Predict the farthest line from the solution

We would expect that `guessFirst.py`, `guessMiddle.py`, `guessLast.py` and `randomGuess.py` performs equally bad and the loss function, or average line error, should reflect that. A test run shows that even when `guessMiddle.py` and `randomGuess.py` have 10x better accuracy (the intuition is `randomGuess.py` and `guessMiddle.py` are statically closer in average to the solution), the difference in the average line error is unnoticeable!.
