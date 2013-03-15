# See driver.py for documentation


import framework

#choices = framework.parameter("div_strategy", ["pipeline", "newton raphson"])
#pipeline_depths = framework.parameter("pipeline_depth", range(0,9))
#number_iterations = framework.parameter("outer_iterations", [5]) #range(3,7)

# define a generator which uses information about the param space
# and information about the current state to decide which points to
# explore next.  This could be problem specific or (eventually) generic.
# This one is very specific to Austin's particular problem domain
def brute_force_search():
#val N_EDGE  = get_int_param("PARAM_NUM_EDGE", 4)       /* 3,4,6*/
#val N_SENSE = get_int_param("PARAM_NUM_SENSE", 8) /* 1-unbounded*/
    for num_edges in [4,6]: # 3 is not actually valid - good test for error reporting
        for num_sensors in xrange(7, 10):
            yield {"NUM_EDGE" : num_edges, "NUM_SENSE" : num_sensors}


            # This code is for Austin's image processing
    #for count in number_iterations.values:
        #for choice in choices.values:
            #if choice == "pipeline":
                #for depth in pipeline_depths.values:
                #    yield {number_iterations.name : count, choices.name : choice, pipeline_depths.name : depth}
            #else:
            #    pass # currently non-feasible

def explore_point(args):
    print "Running explore point"

    import os

    jsonfile = "/home/reames/Files/projects/skin/source/emulator/autotuner-output.json"
    if os.path.exists(jsonfile):
        os.remove(jsonfile)

    import subprocess
    import tempfile
    # Grr, writing to a logfile is NOT optional here
    # PP nicely hangs (forever) if we try creating a piped subprocess from
    # within a subprocess of PP
    logfile = tempfile.NamedTemporaryFile(mode='w+b')
    # call is blocking, popen isn't?

    
    if not "CHISEL" in os.environ:
        print "ERROR: CHISEL environment variable not set."
    for k,v in args.items():
        os.environ[ "PARAM_" + str(k) ] = str(v);

    # TODO: need to checkout N unique copies of the damn code
    # the build products are munging each other.

    # TODO: parse result (modify program) to generate result file

    # in reality, this command should be something like:
    # make -C absolute/path/to/your/install
    # /absolute/path/to/script 
    # cmd cd /home/reames/Files/projects/aspire-autotune && ls -l
    cmd = "make -C ~/Files/projects/skin/source/ run_parameterized_emulator"
    retcode = subprocess.call([cmd],stdout=logfile, stderr=subprocess.STDOUT,shell=True)
    # right now, just dumping the content into the master log, probably not ideal
    if os.path.exists(logfile.name):
        with open(logfile.name) as f:
            content = f.read()
            print content
    else:
        print "ERROR - No log file found!"

    if 0 != int(retcode):
        print "ERROR - Command returned non-zero exit status -- " + str(retcode)
        return { "success" : 0 }

    if os.path.exists(jsonfile):
        with open(jsonfile) as f:
            content = f.read()
            import json
            data = json.loads(content)
            result = {}
            for key, value in data.items():
                result[ str(key) ] = float(value)
                
            print "  Results: " + str(result)
            return result
    else:
        print "WARNING - No json output file found!"
        return { "success" : 0 }
    assert False
