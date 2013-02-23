
import time

class parameter:
    def __init__(self, name, values):
        self.name = name
        self.values = values


# Define a dummy worker function for testing purposes.  
# Note: This is a toy worker.  In reality, we expect a full run
# to take upwards of 9 hours.
def noop_worker_function(args):
    import random
    import time
    time.sleep(random.randint(1,5))
    return [random.random(), 1] # FP 0 <= 1


#TODO: add a standard wrapper for JSON, JAML, XML, python serializer jobs

import pp
import job_manager

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
        job_manager.dispatch_one_job(job_server, worker_func, item)

        # This allows the search func to _only_ be called when
        # there is a slot free.  This gives it slightly better
        # insight and control on how to dispatch jobs
        while not job_manager.job_slot_free(job_server):
            # TODO: probably want some form of exponential backoff here
            import time
            time.sleep(1)

    # Wait for any remaining jobs to finish
    job_manager.wait_for_remaining_jobs(job_server)

    print "Time elapsed: ", time.time() - start_time, "s"
    job_server.print_stats()
    print job_manager.results_to_date


