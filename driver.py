
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


def worker_function(args):
    print args
    import time
    time.sleep(1)
    return 1


import pp

# PP nicely includes queue management
# unfortunately, we want to make decisions before dispatching...
# thus, we hack
jobs = None
def dispatch_one_job(job_server, worker_func, item):
    global jobs
    if jobs == None:
        jobs = [ None for x in range(job_server.get_ncpus()) ]
    while True:
        for i in xrange(len(jobs)):
            if None != jobs[i] and jobs[i].finished:
                jobs[i] = None
        for i in xrange(len(jobs)):
            if None == jobs[i]:
                print "Dispatching job " +str(i)
                jobs[i] = job_server.submit(worker_function, (item,));
                return

def drive_autotuner( search_func ):

    # tuple of all parallel python servers to connect with
    ppservers = () #ppservers = ("10.0.0.1",)
    
    
    # PP automatically uses every CPU, to avoid overload, use one less
    job_server = pp.Server(3, ppservers=ppservers)
    
    print "Starting pp with", job_server.get_ncpus(), "workers"


    # PP nicely includes queue management
    # unfortunately, we want to make decisions before dispatching...
    # thus, we hack
    jobs = [ None for x in range(job_server.get_ncpus()) ]
    for item in search_func():
        dispatch_one_job(job_server, worker_function, item)

        # Retrieves the result calculated by job1
        # The value of job1() is the same as sum_primes(100)
        # If the job has not been finished yet, execution will wait here until result is available
        #result = job1()
        #print result

drive_autotuner( brute_force_search )
exit(1);





# Submit a job of calulating sum_primes(100) for execution. 
# sum_primes - the function
# (100,) - tuple with arguments for sum_primes
# (isprime,) - tuple with functions on which function sum_primes depends
# ("math",) - tuple with module names which must be imported before sum_primes execution
# Execution starts as soon as one of the workers will become available
job1 = job_server.submit(worker_function, (100,), (isprime,), ("math",))

# Retrieves the result calculated by job1
# The value of job1() is the same as sum_primes(100)
# If the job has not been finished yet, execution will wait here until result is available
result = job1()

print "Sum of primes below 100 is", result

start_time = time.time()

# The following submits 8 jobs and then retrieves the results
inputs = (100000, 100100, 100200, 100300, 100400, 100500, 100600, 100700)
jobs = [(input, job_server.submit(sum_primes,(input,), (isprime,), ("math",))) for input in inputs]
for input, job in jobs:
    print "Sum of primes below", input, "is", job()

print "Time elapsed: ", time.time() - start_time, "s"
job_server.print_stats()
