
# TODO (big picture)
# pull a active machine list from a central location on launch
# have each machine launched with local cutoff
# define standard search routines
# add a standard wrapper for JSON, JAML, XML, python serializer jobs
# figure out standard database (wrapper?  default?)

# Note: pp nicely handles remote workers that abort with restart
# this means that so long as the master stays up, any slaves can be
# freely killed.  Yeah!

import time
import sqlite3
import os

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
    return {"perf" : random.random(), "random_name": 1} # FP 0 <= 1


def create_table():
    conn = sqlite3.connect('example.db')

    c = conn.cursor()

    #TODO: need to key by run type too!
    c.execute('''CREATE TABLE sample_point
             (instance INT PRIMARY_KEY, param_hash text, result_hash text);''')

    c.execute('''CREATE TABLE param_instances
             (param_key int, key text, value text,
              FOREIGN KEY(param_key) REFERENCES sample_point(instance) );''')

    c.execute('''CREATE TABLE result_instances
             (result_key int, key text, value text,
              FOREIGN KEY(result_key) REFERENCES sample_point(instance));''')

    c.execute('''CREATE TABLE stocks
             (date text, trans text, symbol text, qty real, price real)''')
        
    conn.commit()
    conn.close()

def wrap_db_record_impl(inner_func, params):
    if not os.path.exists("example.db"):
        create_table()
    conn = sqlite3.connect('example.db')
    
    c = conn.cursor()

    results = inner_func(params)

    param_hash = hash(frozenset(params.items()))
    result_hash = hash(frozenset(results.items()))

    # get a new sample id key
    c.execute("INSERT INTO sample_point(param_hash, result_hash) VALUES(?,?)", [param_hash, result_hash])
    c.execute('SELECT last_insert_rowid()')
    fkey = c.fetchone()[0]
    fkey = str(fkey)

    # add the data tied to that key
    for name, value in params.iteritems():
        sql = "INSERT INTO param_instances VALUES (?,?,?)"
        c.execute(sql, [str(fkey), str(name), str(value)])

    for name, value in results.iteritems():
        sql = "INSERT INTO result_instances VALUES (?,?,?)"
        c.execute(sql, [str(fkey), str(name), str(value)])
        
    conn.commit()
    conn.close()
    return results

def wrap_db_record(inner_func):
    rval = lambda x: wrap_db_record_impl(inner_func, x)
    return rval



import pp
import job_manager

def add_module(name):
    """ Add your module with your implementation and anything it depends on."""
    job_manager.g_modules += [name]

class autotuner_options:
    def __init__(self):
        self.save_results_in_db = True
        self.reuse_results = True

# Note: This should be moved into a SQL database or some such
#TODO
# alternately, this could be used to cache results only long enough
# for the search algorithm to decide what to retain - advantages
# to each I suppose.  Cache size might become a problem
results_to_date = {}
def internal_result_handler(params, results):
    global results_to_date
    results_to_date[ frozendict(params) ] = results

def drive_autotuner( search_func, worker_func, options ):
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


