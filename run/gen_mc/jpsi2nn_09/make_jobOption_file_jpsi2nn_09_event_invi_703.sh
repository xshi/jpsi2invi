#!/bin/bash

JobText_SaveDir=job_text/jobs703

for num in {1..6}
do
    jobOptions=jobOptions_jpsi2invi_gen_mc_nn_09_event_703-${num}.sh
    echo   " #!/bin/bash                                                  " >> ${JobText_SaveDir}/${jobOptions}
    echo   "                                                              " >> ${JobText_SaveDir}/${jobOptions}
    echo   "cd \$HOME/bes/jpsi2invi/v0.1                                  " >> ${JobText_SaveDir}/${jobOptions}
    echo   "./python/sel_events.py run/gen_mc/jpsi2nn_09/job_text/rootfile_nn_09_703/gen_mc_nn_09_jpsi2invi_703-${num}.root run/gen_mc/jpsi2nn_09/job_text/event_nn_09_703/invi/jpsi2invi_gen_mc_nn_09_event_703-${num}.root                                                              " >> ${JobText_SaveDir}/${jobOptions}
done

