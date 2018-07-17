# -*- coding: utf-8 -*-
from SystemComponents import Mode, Machine
from multiprocessing import Pool
import copy


def simulator_function(args):
    mode, time_quantum, job_list, num = args
    system = Machine()
    system.__add_job_list__(job_list)
    system.__initialize_storage__()
    for x in range(0, time_quantum):
        system.__elapse_time__(mode)

    return system.__get_contention_data__()


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

    def __do_simulation__(self, job_list):
        compute_time = self.__simulator_properties.__get_compute_time__()
        concurrency = self.__simulator_properties.__get_concurrency__()
        work_per_process = int(compute_time / concurrency)
        p = Pool(concurrency)
        result_list = p.map(simulator_function,
                            [(Mode.CONVENTIONAL, work_per_process, copy.deepcopy(job_list), num) for num in range(0, concurrency)])
        p.close()
        p.join()
        
        conventional_result = {}
        for result_item in result_list:
            for k, v in result_item.items():
                if k in conventional_result:
                    conventional_result[k] += v
                else:
                    conventional_result[k] = v

        p = Pool(concurrency)
        result_list = p.map(simulator_function,
                            [(Mode.RELAXED_CHKPNT, work_per_process, copy.deepcopy(job_list), num) for num in range(0, concurrency)])
        p.close()
        p.join()

        relaxed_result = {}
        for result_item in result_list:
            for k, v in result_item.items():
                if k in relaxed_result:
                    relaxed_result[k] += v
                else:
                    relaxed_result[k] = v

        print('{:^20}'.format("Conventional"), '    {:^20}'.format("Relaxed Checkpointing"))
        print('{:^4}'.format("Apps"), '{:^4}'.format("Time"), '{:^10}'.format("Percentage"), '    {:^4}'.format("Apps"),
              '{:^4}'.format("Time"), '{:^10}'.format("Percentage"))

        for (k_con, v_con), (k_rel, v_rel) in zip(conventional_result.items(), relaxed_result.items()):
            print('{:2}'.format(k_con), '{:^8}'.format(v_con),
                  "{0:>6.3f} %".format(v_con * 100 / compute_time), '    {:2}'.format(k_rel), '{:^8}'.format(v_rel),
                  "{0:>6.3f} %".format(v_rel * 100 / compute_time))


"""
@Distribution retains data related to a distribution

@author: Malith Jayaweera
"""


class SimulatorProperties:

    def __init__(self, compute_time, concurrency=1):
        self.__compute_time__ = compute_time
        self.__concurrency__ = concurrency
        pass

    def __get_compute_time__(self):
        return self.__compute_time__

    def __set_compute_time__(self, compute_time):
        self.__compute_time__ = compute_time

    def __get_concurrency__(self):
        return self.__concurrency__

    def __set_concurrency__(self, concurrency):
        self.__concurrency__ = concurrency
