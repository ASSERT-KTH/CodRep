# CodRep: Machine Learning on Source Code Competition

CodRep is a machine learning competition on source code data.
The goal of the competition is provide different communities (machine learning, software engineering, programming language) with a common playground to test and compare ideas.
The competition is designed with the following principles:

1. there is no specific background or skill requirements on program analysis to understand the data
2. the systems that use the competition data can be used beyond the competition itself. In particular, there potential usages in the field of automated program repair.   

To take part to the competition, you have to write a program which predicts where to insert a specific line into a source code file. 
In particular, we consider replacement insertions, where the new line replaces an old line, such as

```diff
public class test{
  int a = 1
-  int b = 0.1
+  double b = 0.1
}
```

More specifically, the program  takes as input a set of pairs (Java source code line, Java source code file), and outputs, for each pair,  the predicted line number of the line to be replaced by in the initial source code file.

The competition is organized by KTH Royal Institute of Technology, Stockholm, Sweden. The current organization team is Zimin Chen and Martin Monperrus.

## The winners

What the winner gets? 

1. She gets her name in the hall of fame below
2. She receives some KTH goodies by post
3. Her solution is invited to be part of the futuristic program repair bot designed and implemented at KTH

Hall of fame:

| Data | Name | Score | Link |
| --- | --- |--- | --- |
| ... | ... | ... | ... |




## Data Structure and Format

The provided data is `Files/*.txt`. The txt files are meant to be parsed by competing programs. Their format is as follows, each file contains:
```
{Code line to insert}
\newline
{The full program file}
```

For instance, let's consider this example input file, called `foo.txt`.
```java
double b = 0.1

public class test{
  int a = 1
  int b = 0.1
}
```
In this example, `double b = 0.1` is the code line to be added somewhere in the file in place of another line.

For such an input, the competing programs output for instance `foo.txt 3`, meaning replacing line 3 (`int b = 0.1`) with the new code line `double b = 0.1`.

To train the system, the correct answer for all input files is given in folder `Solutions/`,  e.g. the correct answer to `Files/1.txt` is in `Solutions/1.txt`

## Data provenance

The data used in the competition is taken from real commits in open-source projects.
For a number of different projects, we have analyzed all commits and extracted all the one line replacement changes.
We have further filtered the data  based on the following criteria:

* Only Java files are kept
* Comment-only changes are discarded (eg insertion of `//int a = 1`)
* Inserted or removed lines are not empty lines, and are not space-only changes

## Command-line interface

To play in the competition, your program takes as input input a folder name, that folder containing input data files (per the format explained above).

```shell
$ your-predictor Files
```

Your programs outputs on the console, for each input data file, the predicted line numbers. Several line numbers can be predicted if the tool is not 100% sure of a single prediction. Warning: by convention, line numbers start from 1 (and not 0).
Your program does not have to predict something for all input files, if there is no clear answer, simply don't output anything, the error computation takes that into account, more information about this in **Loss function** below.

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

## How to evaluate your competing program

You can evaluate the performance of your program by piping the output to `Baseline/evaluate.py`, for example:
```shell
cd Baseline
your-program Files | python evaluate.py
```

The output of `evaluate.py` will be:
```
Total files: 2760
Average error: 0.960075351257 (the lower, the better)
Top 1 accuracy: 0.0187232372644 (the higher, the better)
Top 5 accuracy: 0.0246376811594 (the higher, the better)
```

Explanation of the output of `evaluate.py`:
* `Total files`: Number of prediction tasks in `Files/`
* `Average error`: A measurement of the errors of your prediction, as defined in **Loss function** below. This is the only measure used to win the competition.
* `Top k accuracy`: The percentage of correct answers in your top k predictions. As such, `Top 1 accuracy` is the percentage of perfect predictions. We give the accuracy because it is easily understandable, however, it is not suitable for the competition itself, because it does not has the right properties (explained in `Loss function` below).

## Loss function

The average error is a loss function, output by `evaluate.py`, it measures how well your program performs on predicting the lines to be replaced. The lower the average line  is, the better are your predictions. 

The loss function for one prediction task is `tanh(abs({predicted line}-{correct line}))`. The average error is the loss function over all tasks, as calculated as the average of all individual loss. 

This loss function is designed with the following properties in mind:
* there i 0 loss when the prediction is perfect
* there is a bounded and constant loss even when the prediction is far away
* before the bound, the loss is logarithmic
* a perfect prediction is better, but only a small penalty is given to  almost-perfect ones. (in our context, some code line replacement are indeed insensitive to the exact insertion locations).
* the loss is symmetric, continuous and differentiable

We note that the `Top k accuracy` does not comply with all those properties. 

## Base line systems

We provide 5 dumb systems for illustrating how to parse the data and having a baseline performance. These are:
* `guessFirst.py`: Always predict the first line of the file
* `guessMiddle.py`: Always predict the line in the middle of the file
* `guessLast.py`: Always predict the last line of the file
* `randomGuess.py`: Predict a random line in the file
* `maximumError.py`: Predict the worst case, the farthest line from the correct solution

Thanks to the design of the loss function, `guessFirst.py`, `guessMiddle.py`, `guessLast.py` and `randomGuess.py` have the same error, the value of `average error` is comparable. 
