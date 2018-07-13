# -*- coding: utf-8 -*-
from SystemComponents import Machine, Job, JobStatus
from Simulator import Simulator, SimulatorProperties
import random

HOUR = 3600
"""
Relaxed Checkpointing randomizes check point interval selection in order to avoid / reduce application contention

@author: Malith Jayaweera
"""


def initialize_jobs(system, oci_list, beta_list, max_num):
    for x in range(0, max_num):
        job = Job(random.choice(oci_list), random.choice(beta_list))
        job.__set_status__(JobStatus.RUNNING)
        system.__add_job__(job)


def main():
    """
    Relaxed Checkpoint Simulator simulates the execution of an application given the job parameters required
    """
    MAX_JOBS = 10
    RUNTIME = 50 * HOUR
    OCI_LIST = [1.2*HOUR, 1.7*HOUR, 2.1*HOUR, 2.8*HOUR, 3.3*HOUR, 4.7*HOUR]
    BETA_LIST = [0.1*HOUR, 0.2*HOUR, 0.25*HOUR, 0.3*HOUR, 0.35*HOUR, 0.4*HOUR]

    # Ask for Input
    print("Relaxed Checkpointing Simulator")
    print("Configurations. \n 1) Maximum number of jobs:", MAX_JOBS,
          "\n 2) Total compute time    :", RUNTIME, "seconds\n")

    system = Machine()
    simulator_properties = SimulatorProperties(RUNTIME)
    simulator = Simulator(system, simulator_properties)

    initialize_jobs(system, OCI_LIST, BETA_LIST, MAX_JOBS)
    simulator.__do_simulation__()

main()
