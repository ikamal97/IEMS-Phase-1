import sys
import csv
import argparse

#TODO: if the input is a textfile, the infrastructure is done.
#Would need some minor changes if formatting is different, but shouldn't be bad.
# would just need to come up with some ways of assigning weights
# to each job and sorting the list based on that

class Job(object):

    #inside the object all functions, member variables take self as a parameter, basically like "this"
    def __init__(self, id, processing_time, weight, val):
        self.id = int(id)
        self.processing_time = int(processing_time)
        self.weight = int(weight)
        """Play with this variable to determine how to sort jobs.
           Currently just returns the given weight, but maybe try
           weight*processing_time*val.
           val woudl be a command line parameter that could multiply weight"""
        self.heuristic_weight = int(weight) + val*int(processing_time)

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
def fileReader(filename, param_weight):
    jobs = [] #list of each job
    with open(filename, 'r') as input:              #open the file at the given path
        reader = csv.reader(input, delimiter="\t")  #setup to read with tab separating values
        for row in reader:                          #for each data line
            parsed = row[0].split()                 #separate each element into its own element in a list
            job = Job(parsed[0],parsed[1],parsed[2],param_weight)
            jobs.append(job)
    return jobs

def main():
    if len(sys.argv) < 2:
        print("Too few arguments. Use -h or --help to print out options.")
        exit()

    parser = argparse.ArgumentParser(description='Heuristic Program for Single Machine Scheduling')
    parser.add_argument('-i', '--input',dest='input',action='store',
                    help='Input file name for simulation.')
    parser.add_argument('-v', '--value',dest='value',type=float, default=1.0,
                    help='Amount to value job weight over processing time.')

    args = parser.parse_args()
    # args.value is command line parameter to weight processing time relative to given weight

    jobs = fileReader(args.input, args.value)
    print("Ordering of jobs from the input file")
    for j in jobs:
        print(j)

    init_objective_value = evaluate_cost(jobs)
    print("Objective value is {0}".format(init_objective_value))

    new_order = sort_jobs(jobs)
    print("After applying heuristic the order is: ")
    for j in new_order:
        print(j)

    new_objective_value = evaluate_cost(new_order)
    print("Objective value is {0}".format(new_objective_value))

if __name__ == "__main__":
    main()
