# -*- coding: utf-8 -*-
from SystemComponents import Mode, Machine
from multiprocessing import Pool
import matplotlib.pyplot as plt
import copy


def simulator_function(args):
    mode, time_quantum, is_contention, job_list, num = args
    system = Machine()
    system.__add_job_list__(job_list)
    if is_contention:
        system.__turn_on_contention__()
    system.__initialize_storage__()
    for x in range(0, time_quantum):
        print('\rProcess :{0:^2} --- Progress : {1:.2f}%'.format(num, x * 100 / time_quantum), end="")
        system.__elapse_time__(mode)

    return system.__get_contention_data__(), system.__get_job_info__()


"""
Simulator is responsible for orchestrating the event driven mechanism

@author: Malith Jayaweera
"""


class Simulator:
    """
    Simulator class is responsible for orchestrating the relaxed checkpointing mechanism
    Contains the core logic required to perform simulations

    __init__ method initializes by obtaining the system and simulator properties
    """

    def __init__(self, simulator_properties):
        self.__simulator_properties = simulator_properties

    def __get_result_based_on_mode(self, mode, job_list):
        compute_time = self.__simulator_properties.__get_compute_time__()
        concurrency = self.__simulator_properties.__get_concurrency__()
        is_contention = self.__simulator_properties.__get_is_contention__()
        work_per_process = int(compute_time / concurrency)
        p = Pool(concurrency)
        result_list = p.map(simulator_function,
                            [(mode, work_per_process, is_contention, copy.deepcopy(job_list), num) for num
                             in range(0, concurrency)])
        result_list_mode = [result[0] for result in result_list]
        job_list_mode = [result[1] for result in result_list]
        p.close()
        p.join()

        mode_result = {}
        for result_item in result_list_mode:
            for k, v in result_item.items():
                if k in mode_result:
                    mode_result[k] += v
                else:
                    mode_result[k] = v

        job_result = {}
        for job_list in job_list_mode:
            for index, job in enumerate(job_list):
                if index in job_result:
                    job_result[index] += job.__get_useful_work__()
                else:
                    job_result[index] = job.__get_useful_work__()

        return mode_result, job_result

    def __do_simulation__(self, job_list):
        compute_time = self.__simulator_properties.__get_compute_time__()
        conventional_result, job_result_conv = self.__get_result_based_on_mode(Mode.CONVENTIONAL, job_list)
        relaxed_result, job_result_rel = self.__get_result_based_on_mode(Mode.RELAXED_CHKPNT, job_list)

        print('\r{:^20}'.format("Conventional"), '    {:^20}'.format("Relaxed Checkpointing"))
        print('{:^4}'.format("Apps"), '{:^4}'.format("Time"), '{:^10}'.format("Percentage"), '    {:^4}'.format("Apps"),
              '{:^4}'.format("Time"), '{:^10}'.format("Percentage"))

        for (k_con, v_con), (k_rel, v_rel) in zip(conventional_result.items(), relaxed_result.items()):
            print('{:2}'.format(k_con), '{:^8}'.format(v_con),
                  "{0:>6.3f} %".format(v_con * 100 / compute_time), '    {:2}'.format(k_rel), '{:^8}'.format(v_rel),
                  "{0:>6.3f} %".format(v_rel * 100 / compute_time))

        print('\n{:^26}'.format("Conventional"), '    {:^28}'.format("Relaxed Checkpointing"))
        print('{:^4}'.format("Apps"), '{:^4}'.format("Useful Work"), '{:^10}'.format("Percentage"),
              '    {:^4}'.format("Apps"),
              '{:^4}'.format("Useful Work"), '{:^10}'.format("Percentage"))

        for (k_con, v_con), (k_rel, v_rel) in zip(job_result_conv.items(), job_result_rel.items()):
            print('{:2}'.format(k_con), '{:^15}'.format(v_con),
                  "{0:>6.3f} %".format(v_con * 100 / compute_time), '    {:2}'.format(k_rel), '{:^15}'.format(v_rel),
                  "{0:>6.3f} %".format(v_rel * 100 / compute_time))

        relaxed_result = [value * 100 / compute_time for value in relaxed_result.values()]
        conventional_result = [value * 100 / compute_time for value in conventional_result.values()]
        line_rel, = plt.plot(range(0, len(job_list) + 1), relaxed_result, 'bo-', label="Relaxed Checkpointing")
        line_conv, = plt.plot(range(0, len(job_list) + 1), conventional_result, 'ro-', label="Conventional")
        plt.legend(handles=[line_rel, line_conv])
        plt.title("Time spent in Contending while Checkpointing\n as a Percentage of Total Time")
        plt.xlabel("Number of Applications")
        plt.ylabel("Percentage Time Spent Contending (%)")
        plt.show()


"""
@SimulatorProperties retains data related to the Simulator

@author: Malith Jayaweera
"""


class SimulatorProperties:

    def __init__(self, compute_time, concurrency=1, is_contention=False):
        self.__compute_time__ = compute_time
        self.__concurrency__ = concurrency
        self.__is_contention__ = is_contention
        pass

    def __get_compute_time__(self):
        return self.__compute_time__

    def __set_compute_time__(self, compute_time):
        self.__compute_time__ = compute_time

    def __get_concurrency__(self):
        return self.__concurrency__

    def __set_concurrency__(self, concurrency):
        self.__concurrency__ = concurrency

    def __get_is_contention__(self):
        return self.__is_contention__

    def __set_is_contention__(self, is_contention):
        self.__is_contention__ = is_contention
