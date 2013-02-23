
import time

class parameter:
    def __init__(self, name, values):
        self.name = name
        self.values = values


choices = parameter("div_strategy", ["pipeline", "newton raphson"])
pipeline_depths = parameter("pipeline_depth", range(0,9))
number_iterations = parameter("outer_iterations", [5]) #range(3,7)

# define a generator which uses information about the param space
# and information about the current state to decide which points to
# explore next.  This could be problem specific or (eventually) generic.
def brute_force_search():
    for count in number_iterations.values:
        for choice in choices.values:
            if choice == "pipeline":
                for depth in pipeline_depths.values:
                    yield {number_iterations.name : count, choices.name : choice, pipeline_depths.name : depth}
            else:
                pass # currently non-feasible


# Note: This is a toy worker.  In reality, we expect a full run
# to take upwards of 9 hours.
def worker_function(args):
    import random
    import time
    time.sleep(random.randint(1,5))
    return random.random() # FP 0 <= 1

#TODO: add a standard wrapper for JSON, JAML, XML, python serializer jobs


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

def drive_autotuner( search_func, worker_func ):
    """ Given a search function which decides which points to explore
    (structured as a generator) and a worker_func that takes the parameters
    and returns a result, this function handles the logic of dispatching
    all of the jobs to each available core and (potentially) machine"""
    global results_to_date

    import time

    start_time = time.time()

    # tuple of all parallel python servers to connect with
    ppservers = () #ppservers = ("10.0.0.1",)
    
    # PP automatically uses every CPU, to avoid overload, use one less
    job_server = pp.Server(3, ppservers=ppservers)
    
    print "Starting pp with", job_server.get_ncpus(), "workers"

    # TODO: We will need to add timeouts
    for item in search_func():
        dispatch_one_job(job_server, worker_func, item)

        # This allows the search func to _only_ be called when
        # there is a slot free.  This gives it slightly better
        # insight and control on how to dispatch jobs
        while not job_slot_free(job_server):
            # TODO: probably want some form of exponential backoff here
            import time
            time.sleep(1)

    # Wait for any remaining jobs to finish
    job_server.wait()
    for i in xrange(len(jobs)):
        if None != jobs[i]:
            results_to_date[ frozendict(jobs[i][0]) ] = jobs[i][1]()
            jobs[i] = None

    print "Time elapsed: ", time.time() - start_time, "s"
    job_server.print_stats()
    print results_to_date


drive_autotuner( brute_force_search, worker_function )

exit(1);

