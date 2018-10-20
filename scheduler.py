import sys
import csv
import argparse
import pyexcel_xlsx
from statistics import mean

import math

class Job(object):

    #inside the object all functions, member variables take self as a parameter, basically like "this"
    def __init__(self, id, processing_time, weight):
        self.id = int(id)
        self.processing_time = int(processing_time)
        self.weight = int(weight)

        #new weight to sort the list on
        self.heuristic_weight = int(weight)

    def update_heuristic_weight(self,average_processing_time, avg_weight):
        if average_processing_time*self.processing_time <= self.weight:
            self.heuristic_weight = (average_processing_time)*self.processing_time + (avg_weight)*self.weight

    def __lt__(self, Job2):
        return self.heuristic_weight < Job2.heuristic_weight

    def __str__(self): #this is like to_String in Java/C#
        return "Job #" + str(self.id) + ", Processing time= " + str(self.processing_time) + ", Weight= " + str(self.weight)

"""Takes a list of jobs and sorts them based
on their given heuristic_weight"""
def sort_jobs(lst_of_jobs):
    heur_weight = [] #list of heuristic_weight
    #get all the heuristic weights
    for j in lst_of_jobs:
        heur_weight.append(j.heuristic_weight)

    #use them to make a new ordering of jobs
    # this line goes through and sorts the lst_of_jobs in descending order
    # based on the corresponding value of its heuristic_weight
    lst_of_jobs =  [x for _,x in sorted(zip(heur_weight,lst_of_jobs),reverse=True)]

    return lst_of_jobs

"""Assumes the order that the jobs appear in the list
is the order that the jobs will run. So at this point
the scheduling has been made. This just evaluates how
we did."""
def evaluate_cost(lst_of_jobs):
    objective_value = 0
    current_time = 0
    for j in lst_of_jobs:
        current_time = current_time + j.processing_time

        #cost calculation is based off of the last slice that this job occupied
        cost = current_time * j.weight
        objective_value = objective_value + cost
    return objective_value


"""Read in a file given by filename, creates Job objects for each line.
 The format in the file is currently job#, processing_time, weight.
 returns a list of Jobs"""
def excel_reader(filename):
    data = pyexcel_xlsx.get_data(filename)
    import json
    jobs = [] #list of each job
    all_data = (json.loads(json.dumps(data)))
    sheet1 = all_data['Sheet1']
    for row_idx in range(0,len(sheet1)):
        if row_idx == 0:
            continue #skip over the heading row
        job_description = sheet1[row_idx]
        job = Job(job_description[0], job_description[1], job_description[2])
        jobs.append(job)
    return jobs

def average_processing(lst_of_jobs):
    lst_processing_times = [x.processing_time for x in lst_of_jobs]
    lst_weights = [x.weight for x in lst_of_jobs]
    avg_proc = mean(lst_processing_times)
    avg_weight = mean(lst_weights)

    return avg_proc, avg_weight


def main():
    if len(sys.argv) < 2:
        print("Too few arguments. Use -h or --help to print out options.")
        exit()

    parser = argparse.ArgumentParser(description='Heuristic Program for Single Machine Scheduling')
    parser.add_argument('-i', '--input',dest='input',action='store',
                    help='Input file name for simulation.')
    parser.add_argument('-v', '--verbose',dest='verbose',action='store_true', default=False,
                    help='Prints out job ordering if given -v.')

    args = parser.parse_args()
    # args.value is command line parameter to weight processing time relative to given weight
    verbose = args.verbose

    jobs = excel_reader(args.input)
    #calculate the average processing time and average weight
    avg_proc, avg_weight = average_processing(jobs)

    print("Ordering of jobs from the input file")
    for j in jobs:
        j.update_heuristic_weight(avg_proc, avg_weight)
        if verbose == True:
            print(j)

    init_objective_value = evaluate_cost(jobs)
    print("Objective value is {0}".format(init_objective_value))

    new_order = sort_jobs(jobs)
    print("After applying heuristic the order is: ")
    for j in new_order:
        if verbose == True:
            print(j)

    new_objective_value = evaluate_cost(new_order)
    print("Objective value is {0}".format(new_objective_value))

if __name__ == "__main__":
    main()
