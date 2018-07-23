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
        return "Beta:{0:>7} HRS,Alpha:{1:>5} HRS,Useful:{2:>5} HRS".format(str(self.__beta / 3600),
                                                                           str(self.__alpha / 3600),
                                                                           str(self.__useful_work / 3600))


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
        self.__contention_dict = {0: 0.0, 1: 0.009900990099009901, 2: 0.019801980198019802, 3: 0.0297029702970297,
                                  4: 0.039603960396039604, 5: 0.04950495049504951, 6: 0.0594059405940594,
                                  7: 0.06930693069306931, 8: 0.07920792079207921, 9: 0.0891089108910891,
                                  10: 0.09900990099009901, 11: 0.10891089108910891, 12: 0.1188118811881188,
                                  13: 0.12871287128712872, 14: 0.13861386138613863, 15: 0.1485148514851485,
                                  16: 0.15841584158415842, 17: 0.16831683168316833, 18: 0.1782178217821782,
                                  19: 0.18811881188118812, 20: 0.19801980198019803, 21: 0.2079207920792079,
                                  22: 0.21782178217821782, 23: 0.22772277227722773, 24: 0.2376237623762376,
                                  25: 0.24752475247524752, 26: 0.25742574257425743, 27: 0.26732673267326734,
                                  28: 0.27722772277227725, 29: 0.2871287128712871, 30: 0.297029702970297,
                                  31: 0.3069306930693069, 32: 0.31683168316831684, 33: 0.32673267326732675,
                                  34: 0.33663366336633666, 35: 0.3465346534653465, 36: 0.3564356435643564,
                                  37: 0.36633663366336633, 38: 0.37623762376237624, 39: 0.38613861386138615,
                                  40: 0.39603960396039606, 41: 0.40594059405940597, 42: 0.4158415841584158,
                                  43: 0.42574257425742573, 44: 0.43564356435643564, 45: 0.44554455445544555,
                                  46: 0.45544554455445546, 47: 0.46534653465346537, 48: 0.4752475247524752,
                                  49: 0.48514851485148514, 50: 0.49504950495049505, 51: 0.504950495049505,
                                  52: 0.5148514851485149, 53: 0.5247524752475248, 54: 0.5346534653465347,
                                  55: 0.5445544554455446, 56: 0.5544554455445545, 57: 0.5643564356435643,
                                  58: 0.5742574257425742, 59: 0.5841584158415841, 60: 0.594059405940594,
                                  61: 0.6039603960396039, 62: 0.6138613861386139, 63: 0.6237623762376238,
                                  64: 0.6336633663366337, 65: 0.6435643564356436, 66: 0.6534653465346535,
                                  67: 0.6633663366336634, 68: 0.6732673267326733, 69: 0.6831683168316832,
                                  70: 0.693069306930693, 71: 0.7029702970297029, 72: 0.7128712871287128,
                                  73: 0.7227722772277227, 74: 0.7326732673267327, 75: 0.7425742574257426,
                                  76: 0.7524752475247525, 77: 0.7623762376237624, 78: 0.7722772277227723,
                                  79: 0.7821782178217822, 80: 0.7920792079207921, 81: 0.801980198019802,
                                  82: 0.8118811881188119, 83: 0.8217821782178217, 84: 0.8316831683168316,
                                  85: 0.8415841584158416, 86: 0.8514851485148515, 87: 0.8613861386138614,
                                  88: 0.8712871287128713, 89: 0.8811881188118812, 90: 0.8910891089108911,
                                  91: 0.900990099009901, 92: 0.9108910891089109, 93: 0.9207920792079208,
                                  94: 0.9306930693069307, 95: 0.9405940594059405, 96: 0.9504950495049505,
                                  97: 0.9603960396039604, 98: 0.9702970297029703, 99: 0.9801980198019802}
        pass

    def __get_degradation__(self, num_of_apps):
        return self.__contention_dict[num_of_apps]
