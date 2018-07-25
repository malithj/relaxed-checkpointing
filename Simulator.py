# -*- coding: utf-8 -*-
from SystemComponents import Mode, Machine, Job
import matplotlib.pyplot as plt
import copy
import csv
import os


def simulator_function(args):
    mode, time_quantum, is_contention, job_list, num = args
    system = Machine()
    system.__add_job_list__(job_list)
    if is_contention:
        system.__turn_on_contention__()
    else:
        system.__turn_off_contention__()
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

    def __get_result_based_on_mode(self, mode, job_list, contention=False):
        compute_time = self.__simulator_properties.__get_compute_time__()
        concurrency = self.__simulator_properties.__get_concurrency__()
        is_contention = contention
        work_per_process = int(compute_time / concurrency)
        result_list = simulator_function([mode, work_per_process, is_contention, copy.deepcopy(job_list), 0])
        result_list_mode = [result_list[0]]
        job_list_mode = [result_list[1]]

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
                    job_result[index].__set_useful_work__(
                        job_result[index].__get_useful_work__() + job.__get_useful_work__())
                else:
                    job_tracker = Job()
                    job_tracker.__set_useful_work__(job.__get_useful_work__())
                    job_result[index] = job_tracker

        return mode_result, job_result

    def __do_simulation__(self, job_list):
        compute_time = self.__simulator_properties.__get_compute_time__()
        conventional_result, job_result_conv = self.__get_result_based_on_mode(Mode.CONVENTIONAL, job_list,
                                                                               contention=False)
        relaxed_result, job_result_rel = self.__get_result_based_on_mode(Mode.RELAXED_CHKPNT, job_list,
                                                                         contention=False)

        conventional_result_cont, job_result_conv_cont = self.__get_result_based_on_mode(Mode.CONVENTIONAL, job_list,
                                                                                         contention=True)
        relaxed_result_cont, job_result_rel_cont = self.__get_result_based_on_mode(Mode.RELAXED_CHKPNT, job_list,
                                                                                   contention=True)

        print('\r{:^20}'.format("Conventional"), '    {:^20}'.format("Relaxed Checkpointing"),
              '{:^20}'.format("Conventional"), '    {:^20}'.format("Relaxed Checkpointing"))
        print('{:^4}'.format("Apps"), '{:^4}'.format("Time"), '{:^10}'.format("Percentage"), '    {:^4}'.format("Apps"),
              '{:^4}'.format("Time"), '{:^10}'.format("Percentage"), '    {:^4}'.format("Apps"), '{:^4}'.format("Time"),
              '{:^10}'.format("Percentage"), '    {:^4}'.format("Apps"),
              '{:^4}'.format("Time"), '{:^10}'.format("Percentage"))

        for (k_con, v_con), (k_rel, v_rel), (k_con_cont, v_con_cont), (k_rel_cont, v_rel_cont) in zip(
                conventional_result.items(), relaxed_result.items(), conventional_result_cont.items(),
                relaxed_result_cont.items()):
            print('{:2}'.format(k_con), '{:^8}'.format(v_con),
                  "{0:>6.3f} %".format(v_con * 100 / compute_time), '    {:2}'.format(k_rel), '{:^8}'.format(v_rel),
                  "{0:>6.3f} %".format(v_rel * 100 / compute_time), '    {:2}'.format(k_con_cont),
                  '{:^8}'.format(v_con_cont),
                  "{0:>6.3f} %".format(v_con_cont * 100 / compute_time), '    {:2}'.format(k_rel_cont),
                  '{:^8}'.format(v_rel_cont),
                  "{0:>6.3f} %".format(v_rel_cont * 100 / compute_time))

        print('\n{:^26}'.format("Conventional"), '    {:^28}'.format("Relaxed Checkpointing"))
        print('{:^4}'.format("Apps"), '{:^4}'.format("Useful Work"), '{:^10}'.format("Percentage"),
              '    {:^4}'.format("Apps"),
              '{:^4}'.format("Useful Work"), '{:^10}'.format("Percentage"))

        con_useful = 0
        rel_useful = 0
        con_useful_cont = 0
        rel_useful_cont = 0

        for (k_con, v_con), (k_rel, v_rel), (k_con_cont, v_con_cont), (k_rel_cont, v_rel_cont) in zip(
                job_result_conv.items(), job_result_rel.items(), job_result_conv_cont.items(),
                job_result_rel_cont.items()):
            print('{:2}'.format(k_con), '{:^15}'.format(v_con.__get_useful_work__()),
                  "{0:>6.3f} %".format(v_con.__get_useful_work__() * 100 / compute_time), '    {:2}'.format(k_rel),
                  '{:^15}'.format(v_rel.__get_useful_work__()),
                  "{0:>6.3f} %".format(v_rel.__get_useful_work__() * 100 / compute_time))
            con_useful += v_con.__get_useful_work__()
            rel_useful += v_rel.__get_useful_work__()
            con_useful_cont += v_con_cont.__get_useful_work__()
            rel_useful_cont += v_rel_cont.__get_useful_work__()

        print("\nSystem Average Useful Work")
        print('\n{:^26}'.format("Conventional"), '    {:^28}'.format("Relaxed Checkpointing"))
        print('{:^18}'.format("Without contention"), ' {:^13}'.format("With contention"),
              '{:^18}'.format("Without contention"), ' {:^13}'.format("With contention"))
        print('{0:^18} {1:^13} {2:^18} {3:^13}'.format(con_useful * 100 / (compute_time * len(job_list)),
                                                       con_useful_cont * 100 / (compute_time * len(job_list)),
                                                       rel_useful * 100 / (compute_time * len(job_list)),
                                                       rel_useful_cont * 100 / (compute_time * len(job_list))))

        conv_without_score = 0
        conv_with_score = 0
        rel_without_score = 0
        rel_with_score = 0
        conv_adj_compute_time = compute_time
        rel_adj_compute_time = compute_time
        conv_cont_adj_compute_time = compute_time
        rel_cont_adj_compute_time = compute_time

        for (k_con, v_con), (k_rel, v_rel), (k_con_cont, v_con_cont), (k_rel_cont, v_rel_cont) in zip(
                conventional_result.items(), relaxed_result.items(), conventional_result_cont.items(),
                relaxed_result_cont.items()):
            if k_con == 0:
                conv_adj_compute_time -= v_con
                rel_adj_compute_time -= v_rel
                conv_cont_adj_compute_time -= v_con_cont
                rel_cont_adj_compute_time -= v_rel_cont
                continue

            conv_without_score += (k_con - 1) * (v_con / conv_adj_compute_time)
            rel_without_score += (k_rel - 1) * (v_rel / rel_adj_compute_time)
            conv_with_score += (k_con_cont - 1) * (v_con_cont / conv_cont_adj_compute_time)
            rel_with_score += (k_rel_cont - 1) * (v_rel_cont / rel_cont_adj_compute_time)
        print("\nContention Score")
        print('\n{:^26}'.format("Conventional"), '    {:^28}'.format("Relaxed Checkpointing"))
        print('{:^18}'.format("Without contention"), ' {:^13}'.format("With contention"),
              '{:^18}'.format("Without contention"), ' {:^13}'.format("With contention"))
        print('{0:^18} {1:^13} {2:^18} {3:^13}'.format(conv_without_score, conv_with_score, rel_without_score,
                                                       rel_with_score))

        relaxed_result_plot = [value * 100 / compute_time for value in relaxed_result.values()]
        conventional_result_plot = [value * 100 / compute_time for value in conventional_result.values()]
        relaxed_result_cont_plot = [value * 100 / compute_time for value in relaxed_result_cont.values()]
        conventional_result_cont_plot = [value * 100 / compute_time for value in conventional_result_cont.values()]
        line_rel, = plt.plot(range(0, len(job_list) + 1), relaxed_result_plot, 'bo-',
                             label="Relaxed Checkpointing - Without Contention")
        line_conv, = plt.plot(range(0, len(job_list) + 1), conventional_result_plot, 'ro-',
                              label="Conventional - Without Contention")
        line_rel_cont, = plt.plot(range(0, len(job_list) + 1), relaxed_result_cont_plot, 'go-',
                                  label="Relaxed Checkpointing - With Contention")
        line_conv_cont, = plt.plot(range(0, len(job_list) + 1), conventional_result_cont_plot, 'yo-',
                                   label="Conventional - With Contention")
        plt.legend(handles=[line_rel, line_conv, line_rel_cont, line_conv_cont])
        plt.title("Time spent against the number of applications doing I/O simultaneously")
        plt.xlabel("Number of Applications doing I/O Simultaneously")
        plt.ylabel("Time Observed as a Percentage(%)")
        plt.show()

        print("\nJob Information")
        for job in job_list:
            print(job)

        if not os.path.exists('results'):
            os.makedirs('results', 0o777)

        with open('results/time-seen-multiple-apps-doing-io.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                ['conv_num_apps', 'overlapped_time_in_seconds_without_contention', 'precentage_time_without_contention',
                 'rel_num_apps',
                 'overlapped_time_in_seconds_without_contention', 'percentage_time_without_contention', 'conv_num_apps',
                 'overlapped_time_in_seconds_with_contention', 'precentage_time_with_contention', 'rel_num_apps',
                 'overlapped_time_in_seconds_with_contention', 'percentage_time_with_contention'])
            for (k_con, v_con), (k_rel, v_rel), (k_con_cont, v_con_cont), (k_rel_cont, v_rel_cont) in zip(
                    conventional_result.items(), relaxed_result.items(), conventional_result_cont.items(),
                    relaxed_result_cont.items()):
                writer.writerow(
                    [k_con, v_con, v_con * 100 / compute_time, k_rel, v_rel, v_rel * 100 / compute_time, k_con_cont,
                     v_con_cont, v_con_cont * 100 / compute_time, k_rel_cont, v_rel_cont,
                     v_rel_cont * 100 / compute_time])

        with open('results/useful-work-done-per-each-application.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                ['conv_app_id', 'useful_work_in_seconds_without_cont', 'precentage_time_without_cont', 'rel_app_id',
                 'useful_work_in_seconds_without_cont',
                 'percentage_time_without_cont', 'conv_app_id', 'useful_work_in_seconds_with_cont',
                 'precentage_time_with_cont', 'rel_app_id', 'useful_work_in_seconds_with_cont',
                 'percentage_time_with_cont'])
            for (k_con, v_con), (k_rel, v_rel), (k_con_cont, v_con_cont), (k_rel_cont, v_rel_cont) in zip(
                    job_result_conv.items(), job_result_rel.items(), job_result_conv_cont.items(),
                    job_result_rel_cont.items()):
                writer.writerow(
                    [k_con, v_con.__get_useful_work__(), v_con.__get_useful_work__() * 100 / compute_time, k_rel,
                     v_rel.__get_useful_work__(), v_rel.__get_useful_work__() * 100 / compute_time, k_con_cont,
                     v_con_cont.__get_useful_work__(), v_con_cont.__get_useful_work__() * 100 / compute_time,
                     k_rel_cont,
                     v_rel_cont.__get_useful_work__(), v_rel_cont.__get_useful_work__() * 100 / compute_time])

        with open('results/job-info.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                ['Jobid', 'beta (HRS)', 'alpha (HRS)'])
            for index, job in enumerate(job_list):
                writer.writerow([index, job.__get_beta__() / 3600, job.__get_alpha__() / 3600])

        with open('results/avg-contention-score.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                ['conventional_without_contention', 'conventional_with_contention', 'rel_without_contention',
                 'rel_with_contention'])
            writer.writerow([conv_without_score, conv_with_score, rel_without_score, rel_with_score])

        with open('results/avg-useful-work.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                ['conventional_without_contention', 'conventional_with_contention', 'rel_without_contention',
                 'rel_with_contention'])
            writer.writerow([con_useful * 100 / (compute_time * len(job_list)),
                             con_useful_cont * 100 / (compute_time * len(job_list)),
                             rel_useful * 100 / (compute_time * len(job_list)),
                             rel_useful_cont * 100 / (compute_time * len(job_list))])


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
