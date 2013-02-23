# Note: This file is very deliberately structured as a module NOT an
# object.  The reason for this is that the search code needs to be
# able to inspect state and change behavior based off the context.
# If this were an object, this would require passing around references
# everywhere.


import time
import pp

# needed to make the dictionary itself a valid hash key
class frozendict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

# Note: This should be moved into a SQL database or some such
#TODO
# alternately, this could be used to cache results only long enough
# for the search algorithm to decide what to retain - advantages
# to each I suppose.  Cache size might become a problem
results_to_date = {}

# PP nicely includes queue management
# unfortunately, we want to make decisions before dispatching...
# thus, we hack
jobs = None
def dispatch_one_job(job_server, worker_func, item):
    """Wait until a job slot is available on the available workers, then dispatch a new job to that worker.  This function may block for long periods of time!"""
    global jobs
    global results_to_date
    if jobs == None:
        jobs = [ None for x in range(job_server.get_ncpus()) ]
    while True:
        for i in xrange(len(jobs)):
            if None != jobs[i] and jobs[i][1].finished:
                results_to_date[ frozendict(jobs[i][0]) ] = jobs[i][1]()
                jobs[i] = None
        for i in xrange(len(jobs)):
            if None == jobs[i]:
                print "Dispatching job " +str(i)
                jobs[i] = [item, job_server.submit(worker_func, (item,))];
                return
        

def job_slot_free(job_server):
    """Returns true if a job slot is free and a new job can be executed"""
    global jobs
    global results_to_date
    if jobs == None:
        jobs = [ None for x in range(job_server.get_ncpus()) ]
    for i in xrange(len(jobs)):
        if None == jobs[i] or jobs[i][1].finished:
            return True;
    return False

def wait_for_remaining_jobs(job_server):
    global jobs
    global results_to_date
    job_server.wait()
    for i in xrange(len(jobs)):
        if None != jobs[i]:
            results_to_date[ frozendict(jobs[i][0]) ] = jobs[i][1]()
            jobs[i] = None
