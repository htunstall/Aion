# -*- coding: utf-8 -*-
import numpy
import csv
import matplotlib.pyplot as plt
import data_minip.ph_script as calibration
import classes.classes as classes
import matplotlib.font_manager as font_manager
import log.functions
import ui.plot_unbuffered
import glob
import time
import re

from tkinter import messagebox
from matplotlib.backends.backend_pdf import PdfPages
from statsmodels.nonparametric import smoothers_lowess

# ===================================================================================
#  The called procedures
# ===================================================================================
def unbuffered_calculation(o_logbox, _def_values):
    result_dir = _def_values.ub_path
    data_set = []
    uniq_runs = []

    list_files = glob.glob1(result_dir,"*.txt")

    noti_id = []
    # After how many files shall we let the user know the program is still working?
    multiple = 5
    # So long as there are less than 5,000 files the log box will kep the user updated evey 5 processed
    for i in range(1000):
        noti_id.append(i*multiple)
    noti_id.remove(0)

    # Create the pdf for the complete graph output
    pdf_filename = "all_graphs.pdf"
    pdf_filepath = "{0}\\{1}".format(_def_values.ub_path, pdf_filename)
    if _def_values.ub_save_pdf:
        with PdfPages(pdf_filepath) as pdf:
            calculate_file_data(list_files, noti_id, uniq_runs, data_set, _def_values, o_logbox, pdf)
    else:
        calculate_file_data(list_files, noti_id, uniq_runs, data_set, _def_values, o_logbox)

    log.functions.log(True, "info", "All unbuffered data calculated for {0} files!".format(len(list_files)), o_logbox)
    if _def_values.ub_save_pdf:
        log.functions.log(True, "info", r"Saving '{}'".format(pdf_filename), o_logbox)

    # -------------------------------------------------------------------------------
    #  Calculate and save Average pH values
    # -------------------------------------------------------------------------------
    data_set_i = []
    for uniq_id in uniq_runs:
        data_set_i.clear()
        # Get the indexes for a set of repeats
        # INEFICIENT but works
        for i in range(0, len(list_files)):
            if data_set[i].filename_less_repeat == uniq_id:
                data_set_i.append(i)
        _sum_ph = 0
        # Sum the pH values we're interested in
        for i in data_set_i:
            _sum_ph = _sum_ph + data_set[i].calculated_ph

        _average_ph = _sum_ph / len(data_set_i)

        # Save the calculated avg to every item in the data structure
        #  AND save the avg error
        for i in data_set_i:
            data_set[i].set_average_ph = _average_ph
            # Avg pH - filename pH
            data_set[i].avg_error_ph = _average_ph - data_set[i].filename_ph

    # -------------------------------------------------------------------------------
    #  Write the output *.csv
    # -------------------------------------------------------------------------------
    output_file = "{}\\ub_data.csv".format(_def_values.ub_path)
    # First check to see if the file is open!
    try:
        file_o = open(output_file, "w+")
        file_o.close()
    except:
        messagebox.showwarning("Warning!", "The file:\n\'{}\' is open.\nPlease close the file then this message box to continue".format(output_file))


    with open(output_file, "w+") as file:
        csv_file = None
        if file:
            csv_file = csv.writer(file, delimiter=",", quotechar='"', lineterminator='\n')

        if csv_file:
            # -----------------------------------------------------------------------
            #  Write the header
            # -----------------------------------------------------------------------
            headder = []
            headder.append(time.strftime("%c"))
            headder.append("R squared: {}".format(_def_values.cal_rsquared))
            headder.append("Equation: y = {0}x + {1}".format(_def_values.cal_slope, _def_values.cal_intercept))
            csv_file.writerow(headder)

            headder.clear()
            headder = ["Filename",
                       "Unique Group",
                       "Repeat number",
                       "Glass pH",
                       "2nd Derivative",
                       "Calculated pH",
                       "Average pH",
                       "pH error (vs. Average)",
                       "pH error (vs. Run)"]
            csv_file.writerow(headder)

            # -----------------------------------------------------------------------
            #  Write the meaty part!
            # -----------------------------------------------------------------------
            for i in range(len(data_set)):
                # None if the filename was skipped due to being poorly named
                if data_set[i].filename_ph != None:
                    _filename_ph = "{:.2f}".format(data_set[i].filename_ph)
                else:
                    _filename_ph = ""
                csv_file.writerow([data_set[i].filename,
                                   data_set[i].filename_less_repeat,
                                   data_set[i].repeat_number,
                                   _filename_ph,
                                   data_set[i].second_der,
                                   data_set[i].calculated_ph,
                                   data_set[i].set_average_ph,
                                   data_set[i].avg_error_ph,
                                   data_set[i].error_ph])
            log.functions.log(True, "info", r"Finished saving 'ub_data.csv'", o_logbox)

    # -------------------------------------------------------------------------------
    #  Find unique repeat numbers
    # -------------------------------------------------------------------------------
    list_rn = []
    # Create a list if unique repeat numbers (removing any characters not in the
    #  range 0-9)
    for i in range(0, len(data_set)):
        if data_set[i].repeat_number != None:
            cur_rn = re.sub(r"\D", "", str(data_set[i].repeat_number))
            if cur_rn not in list_rn:
                log.functions.log(False, "debug", r"unique run number '{}' discovered! saving".format(cur_rn), o_logbox)
                list_rn.append(cur_rn)

    # Make sure the checkboxes will be in order in the toplevel form
    list_rn.sort()
    list_rn.insert(0, "Average")

    ui.plot_unbuffered.show(_def_values, o_logbox, list_rn, data_set)


# Called by the ui for plotting unbuffered data
def plot(checkbox_list, def_values, o_logbox, data_set, _toplevel):
    _legend = []
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(0, len(checkbox_list)):
        # If we wanted to plot this value
        if checkbox_list[i][1].get() == True:
            if checkbox_list[i][0] == "Average":
                _legend.append("Average Error")
            else:
                _legend.append("Run {} Error".format(checkbox_list[i][0]))

            x_vals = []
            y_vals = []
            done_avg = []
            for j in range(0, len(data_set)):
                if data_set[j].repeat_number != None:
                    # If our repeat number is in the data_set repeat number plot the value
                    if str( checkbox_list[i][0]) in str(data_set[j].repeat_number):
                        x_vals.append(data_set[j].filename_ph)
                        y_vals.append(data_set[j].error_ph)
                    elif checkbox_list[i][0] ==  "Average":
                        # So we don't plot each average n repeat times
                        if data_set[j].filename_less_repeat not in done_avg:
                            x_vals.append(data_set[j].filename_ph)
                            y_vals.append(data_set[j].avg_error_ph)
                            done_avg.append(data_set[j].filename_less_repeat)

            plt.scatter(x_vals, y_vals)

    # Remove the user selection pane
    _toplevel.destroy()

    # Modify the graph elements
    _fontsize = 8
    draw_graph(ax, "pH error in unbuffered", "Measured pH (Glass Probe)", "pH error", _legend=True, _legend_data=_legend, _sci=False, _fontsize=_fontsize, _bold=True, _hline=True)
    _figure = "{}\\unbuffered_scatter.png".format(def_values.ub_path)
    log.functions.log(True, "info", "Saving figure: unbuffered_scatter.png", o_logbox)
    fig.savefig(_figure, bbox_inches = 'tight')
    plt.show(fig)
    plt.close(fig)

# ===================================================================================
#  Internal procedures
# ===================================================================================
def calculate_file_data(_list_files, _noti_id, _uniq_runs, _data_set, _def_values, _o_logbox, _pdf=None):
    for i in range(0, len(_list_files)):
        if i in _noti_id:
            log.functions.log(True, "info", r"Files processed:{:4d}".format(i), _o_logbox)
        # Let's assume the filename is named correctly
        good_filename = True

        split_filename = _list_files[i].split("_")
        split_filename_len = len(split_filename)

		# This is because the defined filename structure requires at least 2
		#  underscores, and hence 3 sections. [identifier]_[pH]_[repeat-number]
        if split_filename_len <= 2:
            good_filename = False
        # Even if the filename is bad, we'll make a class that won't be used
        #  Otherwise the index would be one out in the for loop
        _data_set.append(classes.UnbufferedData())
        _data_set[i].filename = _list_files[i]

        # ---------------------------------------------------------------------------
        #  Set reference filename & filename_less_repeat
        # ---------------------------------------------------------------------------
        _data_set[i].fullpath = "{0}\\{1}".format(_def_values.ub_path, _data_set[i].filename)
        log.functions.log(False, "debug", r"Setting reference filename '{0}'".format(_data_set[i].filename), _o_logbox)

        if good_filename:
            # -----------------------------------------------------------------------
            #  Calculate and set the 2nd derivative
            # -----------------------------------------------------------------------
            # Calculate the 2nd derivative and check the validity of the data
            #  The validity check purely checks for if there is a positive current value
            #   in the graph, if there is the user is questioned
            returned = process_data_file_ub(_data_set[i].fullpath, _o_logbox, _def_values, _pdf)
            crossing = returned[0]
            good_data = returned[1]
            if good_data:
                log.functions.log(False, "debug", r"Calculation complete! for '{0}' | Value: {1}".format(_data_set[i].filename, crossing), _o_logbox)
                # Save the second derivative to the data_set
                _data_set[i].second_der = crossing

                # Create a list of unique runs
                del(split_filename[-1])
                _data_set[i].filename_less_repeat = "_".join(split_filename)
                if _data_set[i].filename_less_repeat not in _uniq_runs:
                    _uniq_runs.append(_data_set[i].filename_less_repeat)

                # -------------------------------------------------------------------
                #  Set repeat number - 0 if null value
                # -------------------------------------------------------------------
                split_filename = _data_set[i].filename.split("_")
                # List index of final section "_[repeat_number].txt"
                list_index = len(split_filename) - 1
                if split_filename[list_index] != ".txt":
                    split_filename_dot = split_filename[list_index].split(".")
                    _data_set[i].repeat_number = split_filename_dot[0]
                    log.functions.log(False, "debug", r"Repeat number for filename '{0}' set as '{1}'".format(_data_set[i].filename, _data_set[i].repeat_number), _o_logbox)
                else: # Edge case for pHX,XX_.txt with no repeat number selected
                    _data_set[i].repeat_number = 0
                    log.functions.log(False, "debug", r"Repeat number for filename '{0}' set as '0'".format(_data_set[i].filename), _o_logbox)

                # -------------------------------------------------------------------
                #  Set the filename pH
                # -------------------------------------------------------------------
                # List index of penultimate section "_[repeat_number].txt"
                list_index = len(split_filename) - 2
                # Replace the comma with a decimal point
                _ph = split_filename[list_index].replace(",", ".")
                # Remove the "pH" from the string
                _ph = _ph[2:]
                # Cast _ph to a float
                _data_set[i].filename_ph = float(_ph)
                log.functions.log(False, "debug", r"Filename pH for filename '{0}' set as '{1}'".format(_data_set[i].filename, _data_set[i].filename_ph), _o_logbox)

                # -------------------------------------------------------------------
                #  Calculate pH & error
                # -------------------------------------------------------------------
                y = float(_data_set[i].second_der)
                c = float(_def_values.cal_intercept)
                m = float(_def_values.cal_slope)
                _data_set[i].calculated_ph = float((y - c) / m)

                # Error (calculated pH - file pH)
                _data_set[i].error_ph = _data_set[i].calculated_ph - _data_set[i].filename_ph
            else:
                # Bad Data
                log.functions.log(True, "info", r"The file '{0}' is not valid data Skipping!".format(_list_files[i]), _o_logbox)
                _data_set[i].filename_less_repeat = "Skipped! Invalid data"
        else:
            # Bad filename
            _data_set[i].filename_less_repeat = "Skipped! Incorrect file name formating"
            log.functions.log(True, "info", r"The file '{0}' is not named correctly! Skipping!".format(_list_files[i]), _o_logbox)


def find_sequential_sublists(_y, _list_of_sublists, _def_values):
    neg_i = []
    pos_i = []
    # Create 2 lists: one with the indexes of the +ve numbers, the other with -ve
    #  numbers for the 2nd derivative
    for i, val in  enumerate(_y):
        if val >= 0:
            pos_i.append(i)
        else:
            neg_i.append(i)

    temp_list = []
    prev_value = pos_i[0]
    temp_list.append(pos_i[0])
    for i in range(1, len(pos_i)):
        if pos_i[i] == prev_value + 1:
            temp_list.append(pos_i[i])
            prev_value = pos_i[i]
        else:
            # 3 membered tuple used for later use: [sublist, length, max 2nd der value, index of max 2nd der value]
            _list_of_sublists.append([temp_list, len(temp_list), None, None])
            temp_list = []
            temp_list.append(pos_i[i])
            prev_value = pos_i[i]

    _list_of_sublists.append([temp_list, len(temp_list), None, None])

    # -------------------------------------------------------------------------------
    #  Remove any sublists that start with the zeroth index OR end at the final index
    # -------------------------------------------------------------------------------
    # Rather than remove the dataset entirely let's chop of the last x data points so
    #  any sharp spikes don't ruin the data set. UNLESS the list is < x long, in
    #  which case we remove the sublist
    #
    # x is calculated by dividing the length of the data set by the truncation
    #  factor. The size of the dataset (with a truncation factor of 10) is ~100 for
    #  1100 data points, and ~50 for 550
    x = int(len(_y) / _def_values.ub_truncate_factor)
    if _list_of_sublists[0][0][0] == 0:
        # If the length of the sublist is MORE than the number of items we're
        #  removing, then you can remove x items.
        if len(_list_of_sublists[0][0]) > x:
            _list_of_sublists[0][0] = _list_of_sublists[0][0][x:]
        # Else remove the list, as it is less than x items long. This can be done
        #  because if the list is < x long it is not relevant
        else:
            del _list_of_sublists[0]

    last_list = len(_list_of_sublists) - 1
    last_index = len(_list_of_sublists[last_list][0]) - 1
    final_index = len(_y) - 1
    if _list_of_sublists[last_list][0][last_index] == final_index:
        # If the length of the sublist is MORE than the number of items we're
        #  removing, then you can remove x items.
        if len(_list_of_sublists[last_list][0]) > x:
            _list_of_sublists[last_list][0] = _list_of_sublists[last_list][0][:-x]
        # Else remove the list, as it is less than x items long. This can be done
        #  because if the list is < x long it is not relevant
        else:
            del _list_of_sublists[last_list]

def find_max_sec_der(_y, _list_of_sublists):
    j = 0
    for sublist, length, max_value, max_index in _list_of_sublists:
        max_value = _y[sublist[0]]
        for i in range(1, len(sublist)):
            if _y[sublist[i]] > max_value:
                max_value = _y[sublist[i]]
                max_index = sublist[i]
        _list_of_sublists[j][2] = max_value
        _list_of_sublists[j][3] = max_index
        j += 1

# Returns the index of the sublist which contains the max value
def pick_sublist(_list_of_sublists):
    temp_list = []
    # Final index 1 = max sublist size
    # Final index 2 = max 2nd der
    #  This is based on the 2 membered tuple created previously
    final_i = 2
    for i in range(len(_list_of_sublists)):
        temp_list.append(_list_of_sublists[i][final_i])

    return temp_list.index(max(temp_list))

def draw_graph(_ax, _title, _xlabel, _ylabel, _fontsize=8, _hline=False, _draw=False, _x=None, _y=None, _linewidth=1, _sci=True, _grid=True, _bold=False, _legend=False, _legend_data=None):
    if _draw:
        _ax.plot(_x, _y, linewidth = _linewidth)
    if _bold:
        _ax.set_title(_title, fontsize = _fontsize + 2, fontweight = "bold")
    else:
        _ax.set_title(_title, fontsize = _fontsize)
    _ax.set_xlabel(_xlabel, fontsize = _fontsize)
    _ax.set_ylabel(_ylabel, fontsize = _fontsize)
    if _legend:
        _ax.legend(_legend_data)
    if _grid:
        _ax.set_axisbelow(True)
        _ax.tick_params(axis = "both", direction = "out", labelsize = _fontsize)
        _ax.yaxis.grid(color = "lightgray", linestyle = "-", linewidth = _linewidth)
        _ax.xaxis.grid(color = "lightgray", linestyle = "-", linewidth = _linewidth)
    if _hline:
        _ax.axhline(0, color = "black", linewidth = _linewidth)
    if _sci:
        _ax.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0,0), fontsize = _fontsize)
        _ax.yaxis.offsetText.set_fontsize(_fontsize)



# Draws the elements of one of the six subfigures contained within each page of the PDF file
def plot_subfig(x, y, _title, axis, row, column, fullpath, _xlabel, _ylabel, _fontsize=8, hline=False, draw=True):
    if draw:
        if hline:
            draw_graph(axis[row, column], _title, _xlabel, _ylabel, _draw=True, _x=x, _y=y, _hline=True)
        else:
            draw_graph(axis[row, column], _title, _xlabel, _ylabel, _draw=True, _x=x, _y=y)
    else:
        with open(fullpath) as file:
            lines = file.read().splitlines()
        date = "{:<25}\n{:>29}".format("Date of data collection:", lines[0])
        for line in lines:
            if "Instrument Model:" in line:
                line = line.rpartition(":")[2].strip()
                instrument = "{:<25}{}".format("Instrument Model:", line)
            elif "Incr E (V)" in line:
                line = line.rpartition("=")[2].strip()
                incr_e = "{:<25}{}".format("Increment E (V):", line)
            elif "Amplitude (V)" in line:
                line = line.rpartition("=")[2].strip()
                amplitude = "{:<25}{}".format("Amplitude (V):", line)
            elif "Frequency (Hz)" in line:
                line = line.rpartition("=")[2].strip()
                frequency = "{:<25}{}".format("Frequency (Hz):", line)
            elif "Sensitivity (A/V)" in line:
                line = line.rpartition("=")[2].strip()
                sensitivity = "{:<25}{}".format("Sensitivity (A/V):", line)


        _data = "File Metadata\n\n{}\n{}\n{}\n{}\n{}\n{}".format( date,
                                                                  instrument,
                                                                  incr_e,
                                                                  amplitude,
                                                                  frequency,
                                                                  sensitivity)

        o_font = font_manager.FontProperties()
        o_font.set_family(o_font)
        o_font.set_family("monospace")
        axis[row, column].text( 0,
                                1,
                                _data,
                                size=_fontsize + -2,
                                ha='left',
                                va='top',
                                fontproperties=o_font)
        axis[row, column].axis("off")

# Modified from ph_script
def process_data_file_ub(datafile, o_logbox, def_values, pdf):
    # Let's assume we have a valid dataset
    _good_data = True
    # For log message formatting
    _filename = datafile.rpartition("\\")[2]

    start_row = calibration.find_file_start_row(datafile)
    _delimiter = calibration.calculate_delimiter(datafile, start_row)
    data = numpy.genfromtxt(datafile, skip_header=start_row + 1, delimiter=_delimiter)

    # Calculate the moving average (window 20)
    x = data[:,0]
    y = data[:,1]

    # Is it a valid data set? (all values < 0)
    if y.max() > 0:
        messagebox.showwarning("Warning!", "The file:\'{}\' has been flagged as an invalid dataset. After you close this message box the data in question will be shown to you. Please determine if it is indeed invalid data, then close the graph.\nA further dialog will be provided after the graph is closed.".format(_filename))

        fig, ax = plt.subplots(figsize = (6, 5))
        _fontsize = 8
        draw_graph(ax, "Potential Erroneous Data", "Voltage / V", "Current / A", _grid=True, _sci=True, _draw=True, _x=x, _y=y, _bold=True, _fontsize=_fontsize)
        plt.show(fig)
        plt.close()

        if messagebox.askyesno("Further Information Required!", "Was the data invalid?"):
            _good_data = False
    _error = False
    if _good_data:
        y_avg = calibration.movingaverage(y, 20)

        log.functions.log(False, "debug", r"Calculating first deferential for '{0}'".format(_filename), o_logbox)
        # Calculate the first differential
        diff_y_avg = calibration.differentiate(x, y_avg)

        log.functions.log(False, "debug", r"Calculating second deferential for {0}".format(_filename), o_logbox)
        # Calculate the second differential
        diff2_y_avg = calibration.differentiate(x, diff_y_avg)
        # Lowess smooth the second differential
        low = smoothers_lowess.lowess(diff2_y_avg, x, frac=0.1)
        # lowess helpfully sorts out x parameters, we want them reversed
        low_x = numpy.flip(low[:,0], 0)
        low_y = numpy.flip(low[:,1], 0)

        # ---------------------------------------------------------------------------
        #  Calculate the large moving average and 2nd derivative (250 point moving
        #   average is the default - value changed in the default.ini file)
        # ---------------------------------------------------------------------------
        # _points is the number of points used in the very smoothed moving average
        #  The default value for the moving average factor is 10 which gives a moving
        #  average of 110 points with a data set size 1100, and a 55 point moving
		#  average width with a 550 size data set
        _points = int(len(y) / def_values.ub_ma_point_factor)
        # N.B: The "vs_" prefix = very smoothed
        vs_y = calibration.movingaverage(y_avg, _points)
        vs_diff_y_avg = calibration.differentiate(x, vs_y)
        vs_diff2_y_avg = calibration.differentiate(x, vs_diff_y_avg)
        # Lowess smooth the second differential
        vs_low = smoothers_lowess.lowess(vs_diff2_y_avg, x, frac=0.1)
        # lowess helpfully sorts out x parameters, we want them reversed
        vs_low_y = numpy.flip(vs_low[:,1], 0)

        # ---------------------------------------------------------------------------
        #  Saving the pdf
        # ---------------------------------------------------------------------------
        if def_values.ub_save_pdf:
            # Debuging graphs used to understand the shape of the data, and ergo how
            #  to algorithmically pick the correct 2nd derivative
            _fontsize = 8
            # 8.27, 11.69 inces is A4
            fig, axis = plt.subplots(nrows = 3, ncols = 2, figsize = (8.27, 11.69))
            # Draw subgraphs
            x_label = "Voltage / V"
            y_label = "Current / A"
            # Raw data & smoothed data
            plot_subfig([], [], "", axis, 0, 0, datafile, x_label, y_label, _fontsize=_fontsize, draw = False)
            plot_subfig(x, y_avg, "Plot of 20 point moving\naverage input data", axis, 1, 0, datafile, x_label, y_label, _fontsize=_fontsize)
            # \n\n for padding from the bold title at the top of the page
            plot_subfig(x, y, "\n\nPlot of input data", axis, 0, 1, datafile,x_label, y_label, _fontsize=_fontsize)
            plot_subfig(x, vs_y, "Plot of smoothed {}\npoint moving average".format(_points), axis, 1, 1, datafile, x_label, y_label, _fontsize=_fontsize)
            # 2nd derivative data
            y_label = "f''(Current) / AV⁻²"
            plot_subfig(low_x, low_y, "2nd derivative of the 20 point\n moving average, then lowess smoothed", axis, 2, 0, datafile, x_label, y_label, _fontsize=_fontsize, hline = True)
            plot_subfig(low_x, vs_low_y, "2nd derivative of the {} point\n moving average, then lowess smoothed".format(_points), axis, 2, 1, datafile, x_label, y_label, _fontsize=_fontsize, hline = True)
            fig.suptitle(r"Graphs for file: '{}'".format(_filename), fontsize = _fontsize, fontweight = "bold")
            fig.tight_layout()
            pdf.savefig(fig)
            # Uncomment to show each page of the PDF as it is being saved
            #plt.show(fig)
            plt.close(fig)

        crossing_x, _error = find_zero_crossing_point_mod(low_x, low_y, vs_low_y, o_logbox, def_values)
    else:
        crossing_x = None

    if _error:
        _good_data = False
        log.functions.log(True, "warning", r"The issue was with the file '{}'".format(_filename), o_logbox)
    return [crossing_x, _good_data]

# Redesigned from ph_script - 3 lines remain in tact!
def find_zero_crossing_point_mod(x, y, vs_y, o_logbox, _def_values):
    """
    We want to find x coord where our signal crosses the zero point
    However we want to ignore any earlier fluctuations, so we first find
    the lowest point and trace back from there until we find 0.

    Logic redesigned by Harry Tunstall and documented in the supporting
    document (./aion-master/docs).
    """
    # -------------------------------------------------------------------------------
    #  Start of new logic
    # -------------------------------------------------------------------------------
    #  This logic is designed to discover where the true turning point is. It is
    #   fully documented in the supporting document. Helpful comment lines will be
    #   placed to aid understanding.
    #
    # ===============================================================================
    #  Normal smoothed data analysis
    # ===============================================================================
    # Find and save all sequential sublists
    list_of_sublists = []
    find_sequential_sublists(y, list_of_sublists, _def_values)
    # Find max 2nd derivative value of each sublist
    find_max_sec_der(y, list_of_sublists)

    # ===============================================================================
    #  Very smoothed data analysis
    # ===============================================================================
    # Find and save all sequential sublists
    vs_list_of_sublists = []
    find_sequential_sublists(vs_y, vs_list_of_sublists, _def_values)
    # Find max 2nd derivative value of each sublist
    find_max_sec_der(vs_y, vs_list_of_sublists)

    # -------------------------------------------------------------------------------
    #  Which 2nd derivative sublist will you pick!
    # -------------------------------------------------------------------------------
    vs_max_i = pick_sublist(vs_list_of_sublists)
    # vs_list_of_sublists[vs_max_i][3] = index of the largest 2nd derivative value
    vs_mid_i = vs_list_of_sublists[vs_max_i][3]

    # Find which sublist in the normal data is the correct one
    max_i = None
    for i in range(len(list_of_sublists)):
        # If the index is contained within the sublist of indexes
        if vs_mid_i in list_of_sublists[i][0]:
            max_i = i

    # Since i is used in the original code to denote the first +ve index after the
    #  turning point we must set it accordingly
    _error = False
    if max_i != None:
        i = list_of_sublists[max_i][0][0]
    else:
        _error = True
        log.functions.log(True, "warning", r"The turning point could not be found!", o_logbox)
        i = list_of_sublists[max_i][0][0]
    # -------------------------------------------------------------------------------
    #   End of new logic
    # -------------------------------------------------------------------------------
    # i is the first value greater than zero after our turning point. We get the x, y
    #  coords of the points directly before and after crossing zero.
    x = x[i-1:i+1]
    y = y[i-1:i+1]

    # We want to project where we actually would've crossed zero and plot that
    if _error == False:
        crossing = numpy.interp(0, y, x)
    else:
        crossing = None
    return [crossing, _error]