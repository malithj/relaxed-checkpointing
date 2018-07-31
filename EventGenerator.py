# -*- coding: utf-8 -*-
import random
import math
from enum import Enum

"""
@Distribution retains data related to a distribution

@author: Malith Jayaweera
"""


class DistributionType(Enum):
    EXPONENTIAL = "exponential"
    GAMMA = "gamma"
    NORMAL = "normal"
    WEIBULL = "weibull"


class Distribution:

    def __init__(self, distribution_name=DistributionType.EXPONENTIAL, mean=25, alpha=1, beta=1, sigma=1):
        self.__distribution_name = distribution_name
        self.__mean = mean
        self.__alpha = alpha
        self.__beta = beta
        self.__sigma = sigma

    def __get_mean__(self):
        return self.__mean

    def __get_alpha__(self):
        return self.__alpha

    def __get_beta__(self):
        return self.__beta

    def __get_sigma__(self):
        return self.__sigma

    def __get_distribution_name__(self):
        return self.__distribution_name


"""
@ContentionGenerator generates contention events

@author: Malith Jayaweera
"""


class EventGenerator:
    def __init__(self, distribution):
        """ Returns a FailureEventGenerator object with the specified distribution
        and distribution parameter """
        self.__distribution = distribution
        self.__distribution_name = distribution.__get_distribution_name__()

    def get_next_event(self, mean):
        """ Returns the next failure event time based on the distribution """
        alpha = self.__distribution.__get_alpha__()
        beta = self.__distribution.__get_beta__()
        sigma = self.__distribution.__get_sigma__()

        if self.__distribution_name == DistributionType.EXPONENTIAL:
            return random.expovariate(1 / mean)
        elif self.__distribution_name == DistributionType.WEIBULL:
            __alpha = (mean / math.gamma(1 + 1 / beta))
            return random.weibullvariate(__alpha, beta)
        elif self.__distribution_name == DistributionType.NORMAL:
            return random.normalvariate(mean, sigma)
        elif self.__distribution_name == DistributionType.GAMMA:
            return random.gammavariate(alpha, beta)
        else:
            return random.expovariate(1 / mean)

    def set_distribution(self, distribution):
        distribution_name = distribution.__get_distribution_name__()

        if distribution_name in DistributionType:
            self.__distribution_name = distribution_name
        else:
            raise ValueError("Unsupported distribution type")




"""
@FailureEventGenerator generates failure events 

@author: Malith Jayaweera
"""


class FailureEventGenerator(EventGenerator):

    def __init__(self, mtbf, distribution):
        """ Returns a FailureEventGenerator object with the specified distribution
        and distribution parameter """
        self.__distribution__ = distribution
        self.__mtbf = mtbf
        super().__init__(distribution)

    def get_next_failure(self):
        """ Returns the next failure event time based on the distribution """
        return int(super().get_next_event(self.__mtbf))

    def get_distribution(self):
        return self.__distribution

    def set_distribution(self, distribution):
        self.__distribution = distribution


class FailureEventStorage():

    def __init__(self, failure_gen):
        self.__failure_event_generator = failure_gen
        self.__failure_list = []
        self.__index = 0

    def init_failure_storage(self, compute_time):
        failure_time = self.__failure_event_generator.get_next_failure()
        for time in range(0, compute_time):
            if time == failure_time:
                self.__failure_list.append(failure_time)
                failure_time = time + self.__failure_event_generator.get_next_failure()

    def get_next_failure(self):
        if self.__index < len(self.__failure_list):
            failure = self.__failure_list[self.__index]
            self.__index += 1
            return failure
        else:
            return -1

    def reset_index(self):
        self.__index = 0