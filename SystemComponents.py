# -*- coding: utf-8 -*-
from enum import Enum
import random

"""
@Job retains data about a job submitted to the system

@author: Malith Jayaweera
"""


class Job:

    def __init__(self, alpha=0, beta=0):
        self.__alpha = alpha
        self.__beta = beta
        self.__remaining_time = 0
        self.__status = JobStatus.INITIALIZING
        self.__useful_work = 0
        self.__io_time = 0
        self.__reset_remaining_time__(Mode.CONVENTIONAL)

    def __set_status__(self, status):
        self.__status = status

    def __get_status__(self):
        return self.__status

    def __reset_at_checkpoint__(self):
        self.__status = JobStatus.CHECKPOINTING
        self.__remaining_time = self.__beta

    def __elapse_time__(self, delta=1):
        if self.__remaining_time > 0:
            self.__io_time += 1
            self.__remaining_time = max(self.__remaining_time - delta, 0)
        if self.__status == JobStatus.RUNNING:
            self.__useful_work += 1

    def __set_alpha__(self, alpha):
        self.__alpha = alpha

    def __get_alpha__(self):
        return self.__alpha

    def __set_beta__(self, beta):
        self.__beta = beta

    def __get_beta__(self):
        return self.__beta

    def __get_useful_work__(self):
        return self.__useful_work

    def __set_useful_work__(self, useful_work):
        self.__useful_work = useful_work

    def __get_remaining_time__(self):
        return self.__remaining_time

    def __set_io_time__(self, io_time):
        self.__io_time = io_time

    def __get_io_time__(self):
        return self.__io_time

    def __reset_remaining_time__(self, mode):
        self.__status = JobStatus.RUNNING
        self.__remaining_time = random.randint(self.__alpha - self.__beta * 0.5,
                                               self.__alpha + self.__beta * 0.5) if mode == Mode.RELAXED_CHKPNT else self.__alpha

    def __repr__(self):
        return "Beta:{0:>7} HRS,Alpha:{1:>5} HRS,Useful:{2:>5} HRS".format(str(self.__beta/3600), str(self.__alpha/3600),
                                                                str(self.__useful_work/3600))


"""
@JobStatus retains JobStatus

@author: Malith Jayaweera
"""


class JobStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    TO_BE_CHECKPOINTED = "to_be_checkpointed"
    TO_RUN = "to_run"
    CHECKPOINTING = "checkpointing"


"""
@Mode decides between conventional method and relaxed checkpointing

@author: Malith Jayaweera
"""


class Mode(Enum):
    CONVENTIONAL = "conventional"
    RELAXED_CHKPNT = "relaxed_checkpointing"


"""
@Machine retains system related data 

@author: Malith Jayaweera
"""


class Machine:

    def __init__(self):
        self.__job_list = []
        self.__contention_data = {}
        self.__max_jobs = 0
        self.__is_contention = False
        self.__contention_reporter = ContentionReporter()

    def __add_job__(self, job):
        self.__job_list.append(job)
        self.__max_jobs += 1

    def __add_job_list__(self, job_list):
        for job in job_list:
            self.__add_job__(job)

    def __initialize_storage__(self):
        for x in range(0, self.__max_jobs + 1):
            self.__contention_data[x] = 0

    def __elapse_time__(self, mode):
        num_of_cp_jobs = 0
        for job in self.__job_list:
            if job.__get_status__() is JobStatus.CHECKPOINTING:
                num_of_cp_jobs += 1
        for job in self.__job_list:
            if job.__get_status__() == JobStatus.RUNNING:
                job.__elapse_time__()
                if job.__get_remaining_time__() == 0:
                    job.__reset_at_checkpoint__()
            elif job.__get_status__() == JobStatus.CHECKPOINTING:
                job.__elapse_time__(self.__delta_given_contention__(num_of_cp_jobs))
                if job.__get_remaining_time__() == 0:
                    job.__reset_remaining_time__(mode)
            else:
                pass

        if num_of_cp_jobs not in self.__contention_data:
            self.__contention_data[num_of_cp_jobs] = 1
        else:
            self.__contention_data[num_of_cp_jobs] += 1

    def __get_contention_data__(self):
        return self.__contention_data

    def __delta_given_contention__(self, apps_contending):
        if self.__is_contention:
            degradation_factor = self.__contention_reporter.__get_degradation__(apps_contending)
            return 1 / (1 + degradation_factor)
        else:
            return 1

    def __get_job_info__(self):
        return self.__job_list

    def __turn_on_contention__(self):
        self.__is_contention = True

    def __turn_off_contention__(self):
        self.__is_contention = False


"""
@ContentionReporter reports the contention at any given moment in time

@author: Malith Jayaweera
"""


class ContentionReporter:

    def __init__(self):
        self.__contention_dict = {0: 0, 1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.6, 6: 0.6, 7: 0.8, 8: 0.8, 9: 0.8, 10: 0.8}
        pass

    def __get_degradation__(self, num_of_apps):
        return self.__contention_dict[num_of_apps]
