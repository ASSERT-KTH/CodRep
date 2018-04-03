import os
import glob
import sys

def main():
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
                        length = len(file.readlines())-2
                        #Alwasy guess the line in the middle
                        print(path_to_task + " " + str(length/2))

if __name__=="__main__":
    main()
