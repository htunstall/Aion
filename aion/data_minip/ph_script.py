#!/usr/bin/env python3
import os
import re
import numpy
import csv
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.stats
import time
import file_handling.conf_values
import log.functions

from statsmodels.nonparametric import smoothers_lowess

# =============================================================================
#  Script Global Variables
# =============================================================================
# The value searched for when locating header length
header_substring = "Potential/V"

# Modified to account for any delimiter by looking for "Potential/V"
def find_file_start_row(fullpath):
    # Seek past the guff at the start of our data files
    with open(fullpath) as f:
        row = 0
        while True:
            line = f.readline()
            if not line:
                return row

            if header_substring in line:
                return row
            row += 1

def movingaverage(x,N):
    """ Reversed engineered from how origin implements AAv"""
    out = []
     # The window is kept centered on i, therefore if we;re asked for a even window they get +1
    N += (1 - N%2)
    M = len(x)

    for i in range(len(x)):
        n = (N-1)//2 # n is the window either side of our target

        # At the start and end we reduce the window from both sides
        # until we fit within the available data range,
        # whilst ensuring i is in the middle of the window
        if i < n:
            n = i
        elif i+n+1 > M:
            n = M-i-1

        window = x[i-n:i+n+1]
        out.append(numpy.average(window))
    return out

def differentiate(x, y):
    """ Implemented as in origin: https://www.originlab.com/doc/Origin-Help/Math-Differentiate#Algorithm """
    out = []

    out.append((y[1] - y[0])/(x[1]-x[0]))

    for i in range(1, len(x)-1):
        out.append((1/2)*(((y[i+1] - y[i])/(x[i+1]-x[i])) + ((y[i] - y[i-1])/(x[i] - x[i-1]))))

    n = len(x)-1
    out.append((y[n] - y[n-1])/(x[n] - x[n-1]))

    return out

def find_zero_crossing_point(x, y, datafile):
    """
    We want to find x coord where our signal crosses the zero point
    However we want to ignore any earlier flutuations, so we first find
    the lowest point and trace back from there until we find 0.
    """
    min_point = 999999
    min_i = 0
    for i, val in enumerate(y):
        if (val < min_point):
            min_point = val
            min_i = i
    i = min_i
    v = y[i]
    while v < 0:
        i += 1
        if i >= len(y):
            # We didn't cross 0, hmm
            raise ValueError("Didn't cross zero for datafile: %s" % datafile)
        v = y[i]

    # i is the first value greater than zero after our minimum point
    # we get the x,y coords of the two points before and after crossing zero
    x = x[i-1:i+1]
    y = y[i-1:i+1]

    # We want to project where we actually wouldve crossed zero and plot that
    crossing = numpy.interp(0, y, x)
    return crossing

def calculate_delimiter(datafile, start_row):
    delimiter = None
    with open(datafile, "r") as f:
        for i, line in enumerate(f):
            if i == start_row:
                delimiter = line[len(header_substring)]
    return delimiter


def process_data_file(datafile, o_logbox, data_set, data_files):
    start_row = find_file_start_row(datafile)

    _delimiter = calculate_delimiter(datafile, start_row)
    data = numpy.genfromtxt(datafile, skip_header=start_row + 1, delimiter=_delimiter)

        

    # Calculate the moving average (window 20)
    x = data[:,0]
    y = data[:,1]
    y_avg = movingaverage(y, 20)

    # Let's nab some more data!
    _filename = datafile.rpartition("\\")[2]
    log.functions.log(False, "debug", r"nabbing data for '{0}' for last *.csv use".format(_filename), o_logbox)
    _data_file = [item for item in data_files if datafile in item]
    _ph = _data_file[0][0]
    _repeat = _data_file[0][1]
    data_set.append((_filename, _ph, _repeat, x, y, y_avg))

    log.functions.log(False, "debug", r"Calculating first deferential for '{0}'".format(_filename), o_logbox)
    diff_y_avg = differentiate(x, y_avg)

    log.functions.log(False, "debug", r"Calculating second deferential", o_logbox)
    diff2_y_avg = differentiate(x,diff_y_avg)

    # Lowess smooth the second differential
    low = smoothers_lowess.lowess(diff2_y_avg, x, frac=0.1)
    # lowess helpfully sorts out x parameters, we want them reversed
    low_x = numpy.flip(low[:,0], 0)
    low_y = numpy.flip(low[:,1], 0)

    crossing_x = find_zero_crossing_point(low_x, low_y, datafile)
    return crossing_x

def plot_directories(results_dirs, o_logbox, _def_values):
    data_set = []
    data_set.append(("filename", "ph", "repeat", "x", "y", "y_avg"))
    output_file = "{}\\all_ph_peaks.csv".format(_def_values.cal_path)

    FILE_PATTERN = re.compile(r".*_pH([0-9]+)_([0-9]+).txt")
    colors = iter(cm.rainbow(numpy.linspace(0, 1, len(results_dirs)+2)))
    X_LABEL = "{0} / {1}".format(_def_values.cal_x_axis_label, _def_values.cal_x_axis_units)
    Y_LABEL = "{0} / {1}".format(_def_values.cal_y_axis_label, _def_values.cal_y_axis_units)

    with open(output_file, "w+") as file:
        csv_file = None
        if file:
            csv_file = csv.writer(file, delimiter=",", quotechar='"', lineterminator='\n')

        xlim = None
        result_dir = results_dirs

        data_files = []
        name = os.path.basename(result_dir)
        for filename in os.listdir(result_dir):
            log.functions.log(False, "debug", r"Processing file '{0}'".format(filename), o_logbox)
            mat = FILE_PATTERN.match(filename)
            if mat:
                log.functions.log(False, "debug", r"File '{0}' matched! Saving for later".format(filename), o_logbox)
                data_files.append((mat.group(1), mat.group(2), os.path.join(result_dir, filename)))
            else:
                log.functions.log(False, "debug", r"File '{0}' isn't a *.txt! T.T".format(filename), o_logbox)

        log.functions.log(True, "info", "All *.txt files located! Starting derivative calculations", o_logbox)

        x=[]
        y=[]
        filename = []
        for ph, sample, datafile in sorted(data_files, key=lambda x:int(x[0])):
            try:
                log.functions.log(False, "debug", r"Starting calculation of 2nd der. for '{0}'".format(datafile.rpartition("\\")[2]), o_logbox)
                crossing = process_data_file(datafile, o_logbox, data_set, data_files)
                x.append(int(ph))
                y.append(crossing)
                filename.append((datafile.rpartition("\\")[2]))
                log.functions.log(False, "debug", r"Calculation complete! for '{0}'".format(datafile.rpartition("\\")[2]), o_logbox)
            except ValueError as e:
                print(e)
                continue

        log.functions.log(True, "info", "All derivatives calculated! (phew - that was hard)", o_logbox)

        if csv_file:
            log.functions.log(False, "debug", r"Writing *.csv file of 'pH, 2nd der.'", o_logbox)
            csv_file.writerow([name])
            csv_file.writerow(["Filename", X_LABEL, Y_LABEL])
            for i in range(len(x)):
                csv_file.writerow([filename[i], x[i], y[i]])
            log.functions.log(False, "debug", r"*.csv file complete!", o_logbox)

    log.functions.log(True, "info", "Plotting the graph: Calibration line", o_logbox)

    color = next(colors)
    plt.figure("Figure - Calibration line")
    plt.scatter(x, y, c=color)

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    # Let's snag some y=mx+c values! and set the date!
    section = []
    option = []
    value = []
    for i in range(0, 4):
        section.insert(i, "Calibration")

    option.append("slope")
    value.append("{:.5f}".format(slope))
    _def_values.cal_slope = "{:.5f}".format(slope)

    option.append("intercept")
    value.append("{:.5f}".format(intercept))
    _def_values.cal_intercept = "{:.5f}".format(intercept)

    option.append("r_squared")
    value.append("{:.5f}".format(r_value))
    _def_values.cal_rsquared = "{:.5f}".format(r_value)

    option.append("date")
    value.append(time.strftime("%c"))
    _def_values.cal_date = time.strftime("%c")

    file_handling.conf_values.set_list(section, option, value)

    if not xlim:
        xlim = plt.gca().get_xlim()
    x_vals = numpy.array(xlim)
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, "r--", color=color, label="{name} (r={r_value:.4f}, y={slope:.4f}x+{intercept:.4f})".format(name=name, r_value=r_value, slope=slope, intercept=intercept))

    plt.xlabel(X_LABEL)
    plt.ylabel(Y_LABEL)
    plt.legend()
    _figure = "{}\\calibration_line.png".format(_def_values.cal_path)
    log.functions.log(True, "info", "Saving figure: calibration_line.png", o_logbox)
    plt.figsize=(8, 8)
    plt.savefig(_figure, bbox_inches='tight')
    plt.draw() # Draw figure Calibration Line

    # ------------------------------------------------------------------------------
    # Now we've graphed up it's time to save some data
    # ------------------------------------------------------------------------------
    # Let's generate the unique ph values (there should
    #  be 3 but they many not be exactly 4, 7 & 10)
    seen = set()
    for item in data_set:
        if item[1] not in seen:
            seen.add(item[1])
    seen.discard("ph")

    # Makes the VITAL assumption that all files in the same folder were ALL
    #  run with the same voltage range!
    log.functions.log(True, "info", "All files MUST have the same voltage range. If they don't the generated files will not return the correct result, but will appear fine!", o_logbox)
    log.functions.log(True, "info", "Saving combined *.csv files", o_logbox)
    _output_filenames_sm = []
    _output_filenames_us = []
    for i in range(0, len(seen)):
        _ph = seen.pop()
        # Smoothed data
        output_file = "{0}\\combined_ph{1}_smoothed.csv".format(_def_values.cal_path, _ph)
        _output_filenames_sm.append(output_file)
        gen_csv_combined(output_file, data_set, _ph, 5, o_logbox)
        # Generate the stacked run plot
        _draw = False
        if _def_values.cal_smoothed_graph:
            _draw = True
        create_stacked_graph(output_file, _ph, "Smoothed", _def_values, o_logbox, _draw)

        # Unsmoothed data
        output_file = "{0}\\combined_ph{1}_unsmoothed.csv".format(_def_values.cal_path, _ph)
        _output_filenames_us.append(output_file)
        gen_csv_combined(output_file, data_set, _ph, 4, o_logbox)
        # Generate the stacked run plot
        _draw = False
        if _def_values.cal_unsmoothed_graph:
            _draw = True
        create_stacked_graph(output_file, _ph, "Unsmoothed", _def_values, o_logbox, _draw)

    log.functions.log(False, "debug", r"*.csv file creation complete!", o_logbox)
    # Plot the pH graphs
    create_ph_graph("Smoothed", _def_values, o_logbox, _def_values.cal_ph_stacked_graph, _output_filenames_sm)
    create_ph_graph("Unsmoothed", _def_values, o_logbox, _def_values.cal_ph_stacked_graph, _output_filenames_us)

def gen_csv_combined(output_file, data_set, _ph, smoothed, o_logbox):
    # Note the smoothed value should be either 4 (unsmoothed) or 5 (smoothed)
    _str_smoothed = None
    if smoothed == 4:
        _str_smoothed = "Unsmoothed"
    else:
        _str_smoothed = "Smoothed"
    log.functions.log(False, "debug", r"Writing *.csv file for ph{}: {}".format(_ph, _str_smoothed), o_logbox)
    with open(output_file, "w+") as file:
            csv_file = None
            csv_file = csv.writer(file, delimiter=",", quotechar='"', lineterminator='\n')

            _ph_data_set = []
            for item in data_set:
                if item[1] == _ph:
                    _ph_data_set.append(item)

            _row = []
            _row_head = []
            for k in range(0,len(_ph_data_set)):
                _row.append(_ph_data_set[k][0])
                _row_head.append("A ({})".format(k))

            _row.insert(0, "") # Voltage row doesn't have a filename
            csv_file.writerow(_row)

            _row_head.insert(0, "V")
            _row_head.append("A (average)")
            csv_file.writerow(_row_head)

            _row.clear()
            for l in range(0, len(_ph_data_set[0][5])):
                for m in range(0,len(_ph_data_set)):
                    # create a temp row of unsmoothed (4 - NB smoothed = 5) y values
                    _row.append(_ph_data_set[m][smoothed][l])
                # Calculate average ampage & append
                _avg_ampage = sum(_row) / float(len(_row))
                _row.append(_avg_ampage)

                # Add V to the start of our row
                _row.insert(0, _ph_data_set[0][3][l])
                csv_file.writerow(_row)
                _row.clear()

def create_stacked_graph(file_path, _ph, str_type, _def_values, o_logbox, _draw):
    # Read the generated *.csv to get the data in a nice readable way
    data = numpy.genfromtxt(file_path, skip_header=2, delimiter=",")

    plt.figure("Figure - {} stacked pH{}".format(str_type, _ph))
    #colors = iter(cm.rainbow(numpy.linspace(0, 1, len(data[0])+2)))
    _x = data[:,0]
    _legend = []
    for i in range(1, len(data[0])):
        #color = next(colors)
        plt.plot(_x, data[:,i]) # c=color
        if i != len(data[0])-1:
            _legend.append("A ({})".format(i))
        else:
            _legend.append("A (average)")

    x_label = "{0} / {1}".format(_def_values.cal_y_axis_label, _def_values.cal_y_axis_units)
    y_label = "{0} / {1}".format(_def_values.swv_y_axis_label, _def_values.swv_y_axis_units)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(_legend)
    # Set the axis to scientific
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    log.functions.log(True, "info", "Saving figure: {}_stacked_ph{}.png".format(str_type, _ph), o_logbox)
    _figure = "{}\\{}_stacked_ph{}.png".format(_def_values.cal_path, str_type.lower(), _ph)
    plt.figsize=(6, 6)
    plt.savefig(_figure, bbox_inches='tight')
    if _draw == False:
        plt.close()

def create_ph_graph(str_type, _def_values, o_logbox, _draw, file_paths = []):
    data = []
    ph = []
    for file_path in file_paths:
        # Read the generated *.csv to get the data in a nice readable way
        data.append(numpy.genfromtxt(file_path, skip_header=2, delimiter=","))
        _ph_filename = file_path.rpartition("ph")[2]
        _ph_filename_split = _ph_filename.split("_")
        ph.append(_ph_filename_split[0])

    plt.figure("Figure - {} pH Graph".format(str_type))
    #colors = iter(cm.rainbow(numpy.linspace(0, 1, len(data[0])+2)))
    _x = data[0][:,0] # Let's grab the x-axis
    _legend = []
    for i in range(0, len(data)):
        # Len(data[i].sum(axis=0)) returns the number of columns in the *.csv files
        #  read in
        plt.plot(_x, data[i][:,len(data[i].sum(axis=0))-1])
        _legend.append("pH {}".format(ph[i]))

    x_label = "{0} / {1}".format(_def_values.cal_y_axis_label, _def_values.cal_y_axis_units)
    y_label = "{0} / {1}".format(_def_values.swv_y_axis_label, _def_values.swv_y_axis_units)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(_legend)
    # Set the axis to scientific
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    log.functions.log(True, "info", "Saving figure: {}_stacked_ph_graph.png".format(str_type), o_logbox)
    _figure = "{}\\{}_stacked_ph_graph.png".format(_def_values.cal_path, str_type.lower())
    plt.savefig(_figure, bbox_inches='tight')
    if _draw == False:
        plt.close()