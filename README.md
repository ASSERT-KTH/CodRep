# CodRep: Machine Learning on Source Code Competition

CodRep is a machine learning competition on source code data.
The goal of the competition is provide different communities (machine learning, software engineering, programming language) with a common playground to test and compare ideas.
The competition is designed with the following principles:

1. There is no specific background or skill requirements on program analysis to understand the data.
2. The systems that use the competition data can be used beyond the competition itself. In particular, there are potential usages in the field of automated program repair.   

To take part to the competition, you have to write a program which predicts where to insert a specific line into a source code file.
In particular, we consider replacement insertions, where the new line replaces an old line, such as

```diff
public class test{
  int a = 1;
-  int b = 0.1;
+  double b = 0.1;
}
```

More specifically, the program  takes as input a set of pairs (source code line, source code file), and outputs, for each pair,  the predicted line number of the line to be replaced by in the initial source code file.

The competition is organized by KTH Royal Institute of Technology, Stockholm, Sweden. The organization team is [Zimin Chen](https://www.kth.se/profile/zimin) and [Martin Monperrus](http://www.monperrus.net/martin/).

To be get news about CodRep and be informed about the next edition, register to the CodRep mailing list:
[codrep+subscribe@googlegroups.com](mailto:codrep+subscribe@googlegroups.com)

## CodRep Leaderboard

The official CodRep ranking based on Dataset5 (lower score is better):

| # | Team (Institution/Company) | Score | Tool |
| --- | --- | --- | --- |
| (1)* | [Inria](https://github.com/KTH/CodRep-competition/issues/16) | 0.0722766571799 | [tool](https://github.com/tdurieux/CodRep-competition) |
| 1 | [University of Wisconsin--Madison & Microsoft Research](https://github.com/KTH/CodRepcompetition/issues/29) | 0.07747553105298915 | [tool](https://github.com/jjhenkel/instauro) |
| 2 | [KAIST, South Korea](https://github.com/KTH/CodRep-competition/issues/28) | 0.079663531979 | [tool](https://github.com/agb94/coldbrew) |
| 3 | [Universidad Central "Marta Abreu" de Las Villas](https://github.com/KTH/CodRep-competition/issues/20) | 0.08577749683758787 | [tool](https://github.com/cesarsotovalero/CodRep-submission) |

\* Conflict of interest

## CodRep Rules

The official ranking was computed based on a hidden dataset, which was not public or part of already published datasets. In order to maintain integrity, the hash or the encrypted version of the hidden dataset was uploaded beforehand (commit [b8801401](https://github.com/KTH/CodRep-competition/commit/b88014011bdf6c526bc9092ccce519026c7b0adf)). 

## Data Structure and Format

### Format
The provided data are in `Datasets/.../Tasks/*.txt`. The txt files are meant to be parsed by competing programs. Their format is as follows, each file contains:
```
{Code line to insert}
\newline
{The full program file}
```

For instance, let's consider this example input file, called `foo.txt`.
```java
double b = 0.1;

public class test{
  int a = 1;
  int b = 0.1;
}
```
In this example, `double b = 0.1;` is the code line to be added somewhere in the file in place of another line.
For such an input, the competing programs output for instance `foo.txt 3`, meaning replacing line 3 (`int b = 0.1;`) with the new code line `double b = 0.1;`.
To train the system, the correct answer for all input files is given in folder `Datasets/.../Solutions/*.txt`,  e.g. the correct answer to `Datasets/Datasets1/Tasks/1.txt` is in `Datasets/Datasets1/Solutions/1.txt`

### Usage and citation

This data can be used in many ways, completely outside of the scope of CodRep. If you use this data, please acknolwedge it by citing the following technical report: [The CodRep Machine Learning on Source Code Competition](https://arxiv.org/pdf/1807.03200) (Zimin Chen, Martin Monperrus), arXiv 1807.03200, 2018.   

## Data provenance

The data used in the competition is taken from real commits in open-source projects.
For a number of different projects, we have analyzed all commits and extracted all the one line replacement changes.
We have further filtered the data  based on the following criteria (best effort):

* Only source code files are kept (Java files in dataset00)
* Comment-only changes are discarded (e.g. replacing `// TODO` with `// Fixed`)
* Inserted or removed lines are not empty lines, and are not space-only changes
* Only one replaced code line in the whole file

The datasets used in this competition are from:

| Directory | Origin |
| --- | --- |
| [Dataset1/](https://github.com/KTH/CodRep-competition/tree/master/Datasets/Dataset1) | [*An Empirical Study on Real Bug Fixes*](http://stap.sjtu.edu.cn/images/8/86/Icse15-bugstudy.pdf) |
| [Dataset2/](https://github.com/KTH/CodRep-competition/tree/master/Datasets/Dataset2) | [*CVS-Vintage: A Dataset of 14 CVS Repositories of Java Software*](https://hal.archives-ouvertes.fr/hal-00769121/document) |
| [Dataset3/](https://github.com/KTH/CodRep-competition/tree/master/Datasets/Dataset3) | [*Watch out for This Commit! A Study of Influential Software Changes*](https://arxiv.org/pdf/1606.03266.pdf) |
| [Dataset4/](https://github.com/KTH/CodRep-competition/tree/master/Datasets/Dataset4) | [*From Aristotle to Ringelmann: a large-scale analysis of team productivity and coordination in Open Source Software projects*](https://link.springer.com/article/10.1007/s10664-015-9406-4) |
| [Dataset5/](https://github.com/KTH/CodRep-competition/tree/master/Datasets/Dataset5) | [*Where Should the Bugs Be Fixed?*](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6227210&tag=1), [*An Empirical Study on Developer Related Factors Characterizing Fix-Inducing Commits*](http://www.cs.wm.edu/~mtufano/publications/J1.pdf), [*Bug Prediction Based on Fine-Grained Module Histories*](https://www.researchgate.net/profile/Hideaki_Hata/publication/254041680_Bug_prediction_based_on_fine-grained_module_histories/links/5440e0810cf2d655e194428e.pdf) |

**Contributing**: If you like to contribute with a new dataset, drop us a new email.

Main Statistics about the data:

| Directory | Total source code files | Lines of code (LOC) |
| --- | --- |--- |
| Dataset1/ | 3858 | 2056900 |
| Dataset2/ | 10088 | 5388282 |
| Dataset3/ | 15326 | 627593 |
| Dataset4/ | 10431 | 2308279 |
| Dataset5/ | 18366 | 2785599 |

## Command-line interface

To play in the competition, your program takes as input input a folder name, that folder containing input data files (per the format explained above).

```shell
$ your-predictor Files
```

Your programs outputs on the console, for each task, the predicted line number. Warning: by convention, line numbers start from 1 (and not 0). If there is no prediction made for certain task (by not outputting *\<path\> \<line number\>*), you will receive maximum loss (which is 1) for the task, more information about this in **Loss function** below.

```
<Path1> <line number>
<Path2> <line number>
<Path3> <line number>
...
```

E.g.;
```
/Users/foo/bar/CodRep-competition/Datasets/Dataset1/Tasks/1.txt 42
/Users/foo/bar/CodRep-competition/Datasets/Dataset1/Tasks/2.txt 78
/Users/foo/bar/CodRep-competition/Datasets/Dataset1/Tasks/3.txt 30
...
```

## How to evaluate your competing program

You can evaluate the performance of your program by piping the output to `Baseline/evaluate.py`, for example:
```shell
your-program Files | python evaluate.py
```

The output of `evaluate.py` will be:
```
Total files: 15463
Average line error: 0.988357635773 (the lower, the better)
Recall@1: 0.00750177843885 (the higher, the better)
```

For evaluating specific datasets, use [-d] or [-datasets=] options and specify paths to datasets. The default behaviour is evaluating on all datasets. The path must be absolute path and multiple paths should be separated by `:`, for example:
```shell
your-program Files | python evaluate.py -d /Users/foo/bar/CodRep-competition/Datasets/Dataset1:/Users/foo/bar/CodRep-competition/Datasets/Dataset2
```

Explanation of the output of `evaluate.py`:
* `Total files`: Number of prediction tasks in datasets
* `Average error`: A measurement of the errors of your prediction, as defined in **Loss function** below. This is the only measure used to win the competition
* `Recall@1`: The percentage of predictions where the correct answer is in your top 1 predictions. As such, `Recall@1` is the percentage of perfect predictions. We give the recall because it is easily understandable, however, it is not suitable for the competition itself, because it does not has the right properties (explained in **Loss function** below)

## Loss function

The average error is a loss function, output by `evaluate.py`, it measures how well your program performs on predicting the lines to be replaced. The lower the average line  is, the better are your predictions.

The loss function for one prediction task is `tanh(abs({correct line}-{predicted line}))`. The average line error is the loss function over all tasks, as calculated as the average of all individual loss.

This loss function is designed with the following properties in mind:
* There is 0 loss when the prediction is perfect
* There is a bounded and constant loss even when the prediction is far away
* Before the bound, the loss is logarithmic
* A perfect prediction is better, but only a small penalty is given to  almost-perfect ones. (in our context, some code line replacement are indeed insensitive to the exact insertion locations)
* The loss is symmetric, continuous and differentiable (except at 0)
* Easy to understand and to compute

We note that the `Recall@1` does not comply with all those properties.

## Base line systems

We provide 5 dumb systems for illustrating how to parse the data and having a baseline performance. These are:
* `guessFirst.py`: Always predict the first line of the file
* `guessMiddle.py`: Always predict the line in the middle of the file
* `guessLast.py`: Always predict the last line of the file
* `randomGuess.py`: Predict a random line in the file
* `maximumError.py`: Predict the worst case, the farthest line from the correct solution

Thanks to the design of the loss function, `guessFirst.py`, `guessMiddle.py`, `guessLast.py` and `randomGuess.py` have the same order of magnitude of error, therefore the value of `Average line error` are comparable.


## CodeRep'17
 
Registered participants:

1. [JetBrains Research, HSE](https://github.com/KTH/CodRep-competition/issues/11)
1. [Microsoft Research](https://github.com/KTH/CodRep-competition/issues/14)
1. [The University of Edinburgh](https://github.com/KTH/CodRep-competition/issues/15)
1. [Inria](https://github.com/KTH/CodRep-competition/issues/16)
1. [Siemens Technology and Services Private Limited](https://github.com/KTH/CodRep-competition/issues/17)
1. [source{d}](https://github.com/KTH/CodRep-competition/issues/18)
1. [Universidad Central "Marta Abreu" de Las Villas](https://github.com/KTH/CodRep-competition/issues/20)
1. [IPT Sao Paulo](https://github.com/KTH/CodRep-competition/issues/22)
1. [Singapore Management University](https://github.com/KTH/CodRep-competition/issues/23)
1. [Ericsson & Rise](https://github.com/KTH/CodRep-competition/issues/25)
1. [Otto-von-Guericke University Magdeburg](https://github.com/KTH/CodRep-competition/issues/26)
1. [KAIST, South Korea](https://github.com/KTH/CodRep-competition/issues/28)
1. [University of Wisconsin--Madison & Microsoft Research](https://github.com/KTH/CodRep-competition/issues/29)

Dates:

* Official competition start: April 14th 2018.
* Submission deadline for intermediate ranking: July 4th 2018. 
* Announcement of the intermediate ranking: July 14th 2018. 
* Final submission deadline: Oct. 4th 2018.
* Announcement of the final ranking & end of the competition Oct 14th 2018.

The official final ranking based on Dataset5 (Oct 14th 2018)

| # | Team (Institution/Company) | Score |
| --- | --- | --- |
| (1)* | [Inria](https://github.com/KTH/CodRep-competition/issues/16) | 0.0722766571799 |
| 1 | [University of Wisconsin--Madison & Microsoft Research](https://github.com/KTH/CodRepcompetition/issues/29) | 0.07747553105298915 |
| 2 | [KAIST, South Korea](https://github.com/KTH/CodRep-competition/issues/28) | 0.079663531979 |
| 3 | [Universidad Central "Marta Abreu" de Las Villas](https://github.com/KTH/CodRep-competition/issues/20) | 0.08577749683758787 |

\* Conflict of interest

Intermediate ranking based on Dataset4 (July 4th 2018)

| Position | Team name | Score on Dataset4 | 
| --- | --- | --- | 
| #1 | [Thomas Durieux (INRIA)](https://github.com/KTH/CodRep-competition/issues/16) |  0.0834200326357 |
| #2 | [Gabin An & Shin Yoo (KAIST)](https://github.com/KTH/CodRep-competition/issues/28) | 0.0884776175201 |
| #3 | [Jesper Derehag & Olof Mogren (Ericsson & RISE)](https://github.com/KTH/CodRep-competition/issues/25) | 0.09253418191163333 |
| #4 | [Sebastian Nielebock, Robert Heumüller, Kevin Michael Schott, Frank Ortmeier (Otto-von-Guericke University Magdeburg, Germany)](https://github.com/KTH/CodRep-competition/issues/26) | 0.11869677510133332​ |

