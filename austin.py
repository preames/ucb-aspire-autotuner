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
    print "Running expore point"
    return framework.noop_worker_function(args)

