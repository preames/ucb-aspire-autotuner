# This file shows how the new autotuning framework can be setup for
# a particular client.  The parameter space and the search algorithm
# are specific to Austin's particular workload.  We haven't defined
# a metric yet.

# ----------------------------------------------------
# IMPORTANT, IMPORTANT, IMPORTANT
# Key note: The fact that everything except main lives in a different 
# file is unfortuntately required (for now).  This is due to a limitation
# of the master-server dispatch library we're using.  If you don't maintain
# this seperation you will get errors indicating any functions in this file
# called by the autotuner do not exist.
# -----------------------------------------------------

# TODO: (project specific)
# hookup the Py->JSON->Scala->parse output->Py code around the black box
# hook into the database for retention and parameterize
# - important, allow restart, how separate?
# define a metric (can defer)



import framework
import austin

import framework
if __name__ == "__main__":
    # create_table()
    framework.add_module("austin")
    framework.drive_autotuner( austin.brute_force_search, austin.explore_point )

    exit(1);

