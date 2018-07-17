# -*- coding: utf-8 -*-
from enum import Enum
import queue
import random

"""
@Job retains data about a job submitted to the system

@author: Malith Jayaweera
"""


class Job:

    def __init__(self, alpha, beta):
        self.__alpha = alpha
        self.__beta = beta
        self.__remaining_time = 0
        self.__status = JobStatus.INITIALIZING
        self.__reset_remaining_time__(Mode.CONVENTIONAL)
        self.__useful_work = 0

    def __set_status__(self, status):
        self.__status = status

    def __get_status__(self):
        return self.__status

    def __reset_at_checkpoint__(self):
        self.__status = JobStatus.CHECKPOINTING
        self.__remaining_time = self.__beta

    def __elapse_time__(self, delta=1):
        if self.__remaining_time > 0:
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

    def __get_remaining_time__(self):
        return self.__remaining_time

    def __reset_remaining_time__(self, mode):
        self.__status = JobStatus.RUNNING
        self.__remaining_time = random.randint(self.__alpha - self.__beta * 0.5,
                                               self.__alpha + self.__beta * 0.5) if mode == Mode.RELAXED_CHKPNT else self.__alpha

    def __repr__(self):
        return "Beta:{0:>7}  Alpha:{1:>5} Useful:{2:>5}".format(str(self.__beta), str(self.__alpha),
                                                                str(self.__useful_work))


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
        self.__job_queue = queue.Queue()
        self.__checkpointing_queue = queue.Queue()
        self.__to_be_checkpointed_queue = queue.Queue()
        self.__job_list = []
        self.__contention_data = {}
        self.__max_jobs = 0
        self.__is_contention = False
        self.__contention_reporter = ContentionReporter()

    def __add_job__(self, job):
        self.__job_queue.put(job)
        self.__job_list.append(job)
        self.__max_jobs += 1

    def __add_job_list__(self, job_list):
        for job in job_list:
            self.__add_job__(job)

    def __get_job__(self):
        return self.__job_queue.get()

    def __has_jobs__(self):
        return not self.__job_queue.empty()

    def __get_checkpointing_job(self):
        return self.__checkpointing_queue.get()

    def __set_checkpointing_job(self, job):
        self.__checkpointing_queue.put(job)

    def __get_to_be_checkpointed_job(self):
        return self.__to_be_checkpointed_queue.get()

    def __set_to_be_checkpointed_job(self, job):
        self.__to_be_checkpointed_queue.put(job)

    def __initialize_storage__(self):
        for x in range(0, self.__max_jobs + 1):
            self.__contention_data[x] = 0

    def __elapse_time__(self, mode):

        queue_size = self.__job_queue.qsize()
        while not self.__job_queue.empty() and queue_size > 0:
            job = self.__job_queue.get()
            job.__elapse_time__()
            if job.__get_status__() == JobStatus.RUNNING and job.__get_remaining_time__() == 0:
                job.__reset_at_checkpoint__()
                self.__to_be_checkpointed_queue.put(job)
            else:
                self.__job_queue.put(job)
            queue_size -= 1

        queue_size = self.__checkpointing_queue.qsize()
        apps_contending = queue_size
        if queue_size not in self.__contention_data:
            self.__contention_data[queue_size] = 1
        else:
            self.__contention_data[queue_size] += 1
        while not self.__checkpointing_queue.empty() and queue_size > 0:
            job = self.__checkpointing_queue.get()
            job.__elapse_time__(self.__delta_given_contention__(apps_contending))
            if job.__get_status__() == JobStatus.CHECKPOINTING and job.__get_remaining_time__() == 0:
                job.__reset_remaining_time__(mode)
                self.__job_queue.put(job)
            else:
                self.__checkpointing_queue.put(job)
            queue_size -= 1

        while not self.__to_be_checkpointed_queue.empty():
            job = self.__to_be_checkpointed_queue.get()
            self.__checkpointing_queue.put(job)

    def __get_contention_data__(self):
        return self.__contention_data

    def __delta_given_contention__(self, apps_contending):
        degradation_factor = self.__contention_reporter.__get_degradation__(apps_contending)
        return 1 / (1 + degradation_factor) if self.__is_contention else 1

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
        self.__contention_dict = {0: 0, 1: 0.8, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.6, 6: 0.6, 7: 0.8, 8: 0.3, 9: 0.2, 10: 0.3}
        pass

    def __get_degradation__(self, num_of_apps):
        return self.__contention_dict[num_of_apps]
