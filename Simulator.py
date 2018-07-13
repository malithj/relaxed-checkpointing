# -*- coding: utf-8 -*-
from SystemComponents import Mode

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

    def __init__(self, system, simulator_properties):
        self.__simulatorProperties = simulator_properties
        self.__system = system

    def __simulator_function__(self, mode):
        print("******************** ", mode.name, " ******************************")
        for x in range(0, self.__simulatorProperties.__get_compute_time__() ):
            self.__system.__elapse_time__(mode)

        for k, v in self.__system.__get_contention_data__().items():
            print('{:2}'.format(k), '{:^8}'.format(v), "{0:>.3f} %".format(v * 100 / self.__simulatorProperties.__get_compute_time__()))

    def __do_simulation__(self):
        self.__system.__initialize_storage__()
        self.__simulator_function__(Mode.CONVENTIONAL)
        self.__system.__initialize_storage__()
        self.__simulator_function__(Mode.RELAXED_CHKPNT)


"""
@Distribution retains data related to a distribution

@author: Malith Jayaweera
"""


class SimulatorProperties:

    def __init__(self, compute_time):
        self.__compute_time__ = compute_time
        pass

    def __get_compute_time__(self):
        return self.__compute_time__

    def __set_compute_time__(self, compute_time):
        self.__compute_time__ = compute_time
