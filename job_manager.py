# Note: This file is very deliberately structured as a module NOT an
# object.  The reason for this is that the search code needs to be
# able to inspect state and change behavior based off the context.
# If this were an object, this would require passing around references
# everywhere.


import time
import pp

# This horribly hacky, but neccessary for the parallel python code
# essentially, pp has to reimport all the related modules.  As a result
# it needs the full list of names you're going to use.  Grrr.
# TODO: long term using python inspect to automagically derive this might
#   be better.  A first hacky attempt didn't work and it's not worth
#   investing the time in right now.
g_modules = ["framework", "driver"]

# PP nicely includes queue management
# unfortunately, we want to make decisions before dispatching...
# thus, we hack
jobs = None
def dispatch_one_job(job_server, worker_func, item, callback):
    """Wait until a job slot is available on the available workers, then dispatch a new job to that worker.  This function may block for long periods of time!"""
    global jobs
    if jobs == None:
        jobs = [ None for x in range(job_server.get_ncpus()) ]
    while True:
        for i in xrange(len(jobs)):
            if None != jobs[i] and jobs[i][1].finished:
                callback(jobs[i][0], jobs[i][1]())
                jobs[i] = None
        for i in xrange(len(jobs)):
            if None == jobs[i]:
                print "Dispatching job " +str(i)
                jobs[i] = [item, job_server.submit(worker_func, (item,),modules=tuple(g_modules),globals=globals())];
                return
        

def job_slot_free(job_server):
    """Returns true if a job slot is free and a new job can be executed"""
    global jobs
    if jobs == None:
        jobs = [ None for x in range(job_server.get_ncpus()) ]
    for i in xrange(len(jobs)):
        if None == jobs[i] or jobs[i][1].finished:
            return True;
    return False

def wait_for_remaining_jobs(job_server, callback):
    global jobs
    job_server.wait()
    if jobs == None:
        return # nothing to do
    for i in xrange(len(jobs)):
        if None != jobs[i]:
            callback(jobs[i][0], jobs[i][1]())
            jobs[i] = None
