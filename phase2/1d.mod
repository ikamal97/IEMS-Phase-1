set jobs;
param processing_time{jobs};
param job_weight{jobs};
param total_time;

var completetion_time{j in jobs} >= 0;
var job_order{j in jobs, k in jobs} binary;

minimize weighted_sum: sum{j in jobs} job_weight[j]*completetion_time[j];

subject to complete_after_proc{j in jobs}: completetion_time[j] >= processing_time[j];
#job k after job j
subject to either_completej{j in jobs, k in jobs: j != k}: completetion_time[j] + processing_time[k] <= completetion_time[k] + total_time*(1-job_order[j,k]);
#job k before job j
subject to or_completek{j in jobs, k in jobs: j != k}: completetion_time[k] + processing_time[j] <= completetion_time[j]+ total_time*job_order[j,k];
