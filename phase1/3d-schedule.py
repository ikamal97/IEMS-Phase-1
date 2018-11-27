import sys
import argparse
import pyexcel_xlsx
from statistics import mean

class Grid(object):
    objective_value = 0
    current_time = 0
    completed_jobs = 0
    jobs_in_progress = []
    free_marker = 0

    #Create a 2d grid of the designated size
    def __init__(self, grid_size):
        self.grid = [[self.free_marker for _ in range(grid_size)] for _ in range(grid_size)]

    #Given a job, traverse the grid looking for a contiguous place to assign it
    def tryPlace(self,job):
        for col_idx in range(len(self.grid)):
            for row_idx in range(len(self.grid)):
                #if this point in the grid is free
                #and if this point is not off the bottom of the grid
                #and if this point is not off the right end of the grid
                #and it doesn't intersect with any already allocated job
                if self.grid[row_idx][col_idx] == self.free_marker and \
                row_idx + job.height -1< len(self.grid) and \
                col_idx + job.width -1< len(self.grid) and \
                self.no_overlap(row_idx, col_idx, job):
                    #if the job's area fits within the bounds of the grid and is free return the coordinates
                    return (row_idx, col_idx)
                else:
                    continue
        return (-1, -1) #if cannot place returns -1

    #Ensure there is no overlap inside a job
    def no_overlap(self, row, col, job):
        job_end_row = row + job.height
        job_end_col = col + job.width
        for r in range(row,job_end_row):
            for c in range(col,job_end_col):
                if self.grid[r][c] != self.free_marker:
                    return False
        return True

    #Now the job location has been determined to be valid, allocate it and start running it
    def placeJob(self,job, coordinates):
        job.set_coordinates(coordinates[0], coordinates[1])
        for row_idx in range(coordinates[0],coordinates[0]+job.height):
            for col_idx in range(coordinates[1], coordinates[1] + job.width):
                self.grid[row_idx][col_idx] = job.id
                job.started_at_time = self.current_time
        self.jobs_in_progress.append(job)

    #At the end of each loop call tick. Increments the running count for each allocated job,
    #removes if it reaches its completion
    def tick(self):
        print("Time is: ",self.current_time)
        j = 0
        while j < len(self.jobs_in_progress):
            is_done = self.jobs_in_progress[j].process_tick()
            if is_done == True:
                self.free(self.jobs_in_progress[j])
                j = j - 1
            j = j + 1
        self.current_time = self.current_time + 1

    #Mark a complete job as free space
    def free(self,job):
        x, y = job.get_coordinates()
        for row_idx in range(x,x+job.height):
            for col_idx in range(y, y+job.width):
                self.grid[row_idx][col_idx] = self.free_marker
        self.jobs_in_progress.remove(job)
        self.completed_jobs = self.completed_jobs + 1
        self.add_cost(job)

    #Add the processing time of complete job to the objective_value
    def add_cost(self, job):
        self.objective_value = self.objective_value + self.current_time*job.weight

    #Printing function for debugging
    def __str__(self):
        grid_print = ""
        for row in self.grid:
            grid_print = grid_print + "\n" + str(["%02d" % int(x) for x in row])
        return grid_print


class Job(object):
    ticks_processed = 0 #job has not been started
    x = -1 #job has not been allocated
    y = -1 #job has not been allocated
    complete = False
    started_at_time = -1
    #inside the object all functions, member variables take self as a parameter, basically like "this"
    def __init__(self, id, processing_time, weight, width, height):
        self.id = int(id)
        self.processing_time = int(processing_time)
        self.weight = int(weight)
        self.height = int(height)
        self.width = int(width)

        #new weight to sort the list on
        self.heuristic_weight = self.weight

    def update_heuristic_weight(self,average_area):
        self.heuristic_weight = (1/float(self.processing_time))*self.width*self.height + self.weight*average_area

    #grid.tick() calls this function for each running job
    #tells grid whether or not it is complete
    def process_tick(self):
        self.ticks_processed = self.ticks_processed + 1
        print("Job ID {0} processed {1} ticks out of {2}".format(self.id,self.ticks_processed,self.processing_time))
        if self.ticks_processed == self.processing_time:
            self.complete = True
            return True
        else:
            return False

    #Save the location the job runs at to be freed later
    def set_coordinates(self,x_coord,y_coord):
        self.x = x_coord
        self.y = y_coord

    def get_coordinates(self):
        return (self.x,self.y)

    #Comparator to allow use of built in functions
    def __cmp__(self,Job2):
        return self.id == Job2.id

    #Comparator to allow use of built in functions
    def __lt__(self, Job2):
        return self.heuristic_weight < Job2.heuristic_weight

    def __str__(self): #this is like to_String in Java/C#
        return "Job #" + str(self.id) + ", Processing time= " + str(self.processing_time) + ", Weight= " + str(self.weight) + ", Height = " + str(self.height) + ", Width= " + str(self.width)

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
        job = Job(job_description[0], job_description[1], job_description[2], job_description[3], job_description[4])
        jobs.append(job)
    return jobs

def average_area(lst_of_jobs):
    lst_areas = [x.height*x.width for x in lst_of_jobs]
    avg_area = mean(lst_areas)
    return avg_area

def main():
    if len(sys.argv) < 2:
        print("Too few arguments or missing pyexcel-xlsx. Run pip install pyexcel-xlsx. Use -h or --help to print out options.")
        exit()

    parser = argparse.ArgumentParser(description='Heuristic Program for 3D Scheduling. pip install pyexcel-xlsx required.')
    parser.add_argument('-i', '--input',dest='input',action='store',
                    help='Input file name for simulation.')
    parser.add_argument('-v', '--verbose',dest='verbose',action='store_true', default=False,
                    help='Prints out job ordering if given -v.')
    parser.add_argument('-g', '--grid-size',dest='grid_size',action='store', default=100,
                    help='Define the size of the square grid. Defaults to 100')

    args = parser.parse_args()
    # args.value is command line parameter to weight processing time relative to given weight
    verbose = args.verbose

    #read jobs in from excel sheet
    jobs = excel_reader(args.input)

    #calculate the average area of the jobs
    avg_area = average_area(jobs)
    for j in jobs:
        j.update_heuristic_weight(avg_area)
        if verbose == 1:
            print(j)
    #sort all jobs based on the heuristic priority encoding
    sorted_jobs = sort_jobs(jobs)

    for j in sorted_jobs:
        print(j)

    #define the grid
    # grid_size = 100

    #generate a 2d grid, 0 means this location is free
    g = Grid(int(args.grid_size))

    #while there are still jobs that have not completed
    while g.completed_jobs != len(jobs):
        for job in sorted_jobs:
            if job not in g.jobs_in_progress and not job.complete:
                coords = g.tryPlace(job)
                if coords != (-1,-1):
                    g.placeJob(job, coords)

        g.tick()
        if args.verbose == True:
            print(g)

    print("\n")
    for j in jobs:
        print("Job #{0} started at time: {1}".format(j.id,j.started_at_time))

    print("\nObjective value is {0}".format(g.objective_value))


if __name__ == "__main__":
    main()
