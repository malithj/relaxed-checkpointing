import csv
import matplotlib.pyplot as plt


def plot_graph(file_name):
    relaxed_result_plot = []
    conventional_result_plot = []
    relaxed_result_cont_plot = []
    conventional_result_cont_plot = []
    rows = 0
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows += 1
            relaxed_result_plot.append(float(row['percentage_time_without_contention']))
            conventional_result_plot.append(float(row['precentage_time_without_contention']))
            relaxed_result_cont_plot.append(float(row['precentage_time_with_contention']))
            conventional_result_cont_plot.append(float(row['percentage_time_with_contention']))

    line_rel, = plt.plot(range(0, rows), relaxed_result_plot, 'bs-',
                         label="Relaxed Checkpointing - Without Contention")
    line_conv, = plt.plot(range(0, rows), conventional_result_plot, 'ro-',
                          label="Conventional - Without Contention")
    line_rel_cont, = plt.plot(range(0, rows), relaxed_result_cont_plot, 'go-',
                              label="Relaxed Checkpointing - With Contention")
    line_conv_cont, = plt.plot(range(0, rows), conventional_result_cont_plot, 'yo-',
                               label="Conventional - With Contention")
    plt.legend(handles=[line_rel, line_conv, line_rel_cont, line_conv_cont])
    plt.title("Time spent against the number of applications doing I/O simultaneously")
    plt.xlabel("Number of Applications doing I/O Simultaneously")
    plt.ylabel("Time Observed as a Percentage(%)")
    plt.show()

def main():
    plot_graph('results/time-seen-multiple-apps-doing-io.csv')


if __name__ == '__main__':
    main()
