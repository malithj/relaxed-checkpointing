# -*- coding: utf-8 -*-
from SystemComponents import Machine, Job, JobStatus
from Simulator import Simulator, SimulatorProperties
import random
import time

HOUR = 3600
"""
Relaxed Checkpointing randomizes check point interval selection in order to avoid / reduce application contention

@author: Malith Jayaweera
"""


def initialize_jobs(oci_list, beta_list, max_num):
    job_list = []
    for x in range(0, max_num):
        job = Job(random.choice(oci_list), random.choice(beta_list))
        job.__set_status__(JobStatus.RUNNING)
        job_list.append(job)
    return job_list


def main():
    """
    Relaxed Checkpoint Simulator simulates the execution of an application given the job parameters required
    """
    MAX_JOBS = 10
    RUNTIME = 50 * HOUR
    OCI_LIST = [1.2 * HOUR, 1.7 * HOUR, 2.1 * HOUR, 2.8 * HOUR, 3.3 * HOUR, 4.7 * HOUR]
    BETA_LIST = [0.1 * HOUR, 0.2 * HOUR, 0.25 * HOUR, 0.3 * HOUR, 0.35 * HOUR, 0.4 * HOUR]
    CONCURRENCY = 10
    IS_CONTENTION = False

    # Ask for Input
    print("Relaxed Checkpointing Simulator")
    print("Configurations. \n 1) Maximum number of jobs:", MAX_JOBS,
          "\n 2) Total compute time    :", RUNTIME, "seconds\n")

    simulator_properties = SimulatorProperties(RUNTIME, CONCURRENCY, IS_CONTENTION)
    simulator = Simulator(simulator_properties)

    job_list = initialize_jobs(OCI_LIST, BETA_LIST, MAX_JOBS)
    start_time = time.time()
    simulator.__do_simulation__(job_list)
    elapsed_time = time.time() - start_time
    print("\nTime taken for the simulation : {:^.3f} s".format(elapsed_time))


if __name__ == '__main__':
    main()
