# See driver.py for documentation


import framework

choices = framework.parameter("div_strategy", ["pipeline", "newton raphson"])
pipeline_depths = framework.parameter("pipeline_depth", range(0,9))
number_iterations = framework.parameter("outer_iterations", [5]) #range(3,7)

# define a generator which uses information about the param space
# and information about the current state to decide which points to
# explore next.  This could be problem specific or (eventually) generic.
# This one is very specific to Austin's particular problem domain
def brute_force_search():
    for count in number_iterations.values:
        for choice in choices.values:
            if choice == "pipeline":
                for depth in pipeline_depths.values:
                    yield {number_iterations.name : count, choices.name : choice, pipeline_depths.name : depth}
            else:
                pass # currently non-feasible

def explore_point(args):
    print "Running explore point"
    import subprocess
    import tempfile
    # Grr, writing to a logfile is NOT optional here
    # PP nicely hangs (forever) if we try creating a piped subprocess from
    # within a subprocess of PP
    logfile = tempfile.NamedTemporaryFile(mode='w+b')
    # call is blocking, popen isn't?

    # in reality, this command should be something like:
    # make -C absolute/path/to/your/install
    # /absolute/path/to/script 
    subprocess.call(['cd /home/reames/Files/projects/aspire-autotune && ls -l'],stdout=logfile, stderr=subprocess.STDOUT,shell=True)
    # right now, just dumping the content into the master log, probably not ideal
    with open(logfile.name) as f:
        content = f.read()
        print content

        # TODO: now we have to actually parse that output and return it
        return framework.noop_worker_function(args)

    assert False
