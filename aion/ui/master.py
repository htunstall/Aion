import os
import tkinter
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
import matplotlib.pyplot as plt
import glob
import time

import ui.settings
import log.functions
import data_minip.ph_script
import data_minip.unbuffered
import file_handling.conf_values

min_width = 850 # Std: 650
min_height = 450
xpad = 3
ypad = 4

def show(def_values):
    window = tkinter.Tk()
    # Set the master window title
    window.title("Aion - Ver: {0} - Author: Harry Tunstall - Date Compiled: {1} - Master".format(def_values.version, def_values.version_date))
    # Set the .ico from the ui folder
    window.iconbitmap("{0}/ui/aion.ico".format(os.getcwd()))
    # Set master window size
    window.minsize(width=min_width, height=min_height)
    #window.resizable(width=False, height=False)

    # -------------------------------------------------------------------------------
    #  UI variables
    # -------------------------------------------------------------------------------
    smoothed_graph = tkinter.BooleanVar()
    unsmoothed_graph = tkinter.BooleanVar()
    ph_stacked_graph = tkinter.BooleanVar()

    folder_path_cal = tkinter.StringVar(value=def_values.cal_path)
    folder_path_ub = tkinter.StringVar(value=def_values.ub_path)
    pdf_save_ub = tkinter.BooleanVar()

    v_cal_date_lb = tkinter.StringVar()
    u_date_lb(v_cal_date_lb, def_values.cal_date, False)

    v_cal_eqn_lb = tkinter.StringVar()
    u_eqn_lb(v_cal_eqn_lb, def_values.cal_slope, def_values.cal_intercept, def_values.cal_rsquared)

    # -------------------------------------------------------------------------------
    #  Folder path interface (calibration)
    # -------------------------------------------------------------------------------
    folder_frame_cal = tkinter.LabelFrame(window, text="Calibration Calculation")
    folder_frame_cal.pack(fill='x', expand=1, side="top", padx=xpad, pady=ypad)

    # Folder bar and buttons
    browse_frame_cal = tkinter.Frame(folder_frame_cal)
    browse_frame_cal.pack(side="top", fill='x', expand=1)
    run_button_cal = tkinter.Button(browse_frame_cal, text="Run", command=lambda: run_cal(def_values, folder_path_cal.get(), log_st, def_values, v_cal_date_lb, v_cal_eqn_lb, folder_frame_cal, smoothed_graph, unsmoothed_graph, ph_stacked_graph))
    run_button_cal.pack(side="right", padx=xpad, pady=ypad, ipadx=2)
    browse_button_cal = tkinter.Button(browse_frame_cal, text="Browse", command=lambda: browse_click(def_values, folder_path_cal), padx=xpad)
    browse_button_cal.pack(side="right", padx=xpad, pady=ypad, ipadx=2)
    folder_path_cal_tb = tkinter.Entry(browse_frame_cal, textvariable=folder_path_cal)
    folder_path_cal_tb.pack(fill='x', expand=1, side="left", padx=xpad, pady=ypad)

    # Labels containing y=mx+c and data values
    label_frame_cal = tkinter.Frame(folder_frame_cal)
    label_frame_cal.pack(side="bottom", fill='x', expand=1)
    cal_eqn_lb = tkinter.Label(label_frame_cal, textvariable=v_cal_eqn_lb)
    cal_eqn_lb.pack(side="bottom", anchor='w', padx=xpad, pady=ypad-3)
    cal_date_lb = tkinter.Label(label_frame_cal, textvariable=v_cal_date_lb)
    cal_date_lb.pack(side="bottom", anchor='w', padx=xpad, pady=ypad-3)

    # Stacked pH graphs checkbox's
    checkb2_frame_cal = tkinter.Frame(folder_frame_cal)
    checkb2_frame_cal.pack(side="bottom", fill='x', expand=1)
    ph_graphs_lb = tkinter.Label(checkb2_frame_cal, text="Display the average stacked graphs for the three pH values: ")
    ph_graphs_lb.pack(side="left", padx=xpad, pady=ypad-3)
    ph_graphs_cb = tkinter.Checkbutton(checkb2_frame_cal, text="Display", variable=ph_stacked_graph, onvalue=True, offvalue=False)
    ph_graphs_cb.pack(side="left", padx=xpad, pady=ypad-3)
    ph_graphs_cb.select()

    # Smoothed and unsmoothed graphs checkbox's
    checkb_frame_cal = tkinter.Frame(folder_frame_cal)
    checkb_frame_cal.pack(side="bottom", fill='x', expand=1)
    smoothed_lb = tkinter.Label(checkb_frame_cal, text="Display the stacked graphs for the three pH values. Will the data be: ")
    smoothed_lb.pack(side="left", padx=xpad, pady=ypad-3)
    smooth_cb = tkinter.Checkbutton(checkb_frame_cal, text="Smoothed", variable=smoothed_graph, onvalue=True, offvalue=False)
    smooth_cb.pack(side="left", padx=xpad, pady=ypad-3)
    smooth_cb.deselect()
    unsmooth_cb = tkinter.Checkbutton(checkb_frame_cal, text="Unsmoothed", variable=unsmoothed_graph, onvalue=True, offvalue=False)
    unsmooth_cb.pack(side="left", padx=xpad, pady=ypad-3)
    unsmooth_cb.deselect()



    # -------------------------------------------------------------------------------
    #  Folder path interface (unbuffered)
    # -------------------------------------------------------------------------------
    folder_frame_ub = tkinter.LabelFrame(window, text="Unbuffered Analysis")
    folder_frame_ub.pack(fill='x', expand=1, side="top", padx=xpad, pady=ypad)

    # Folder bar and buttons
    browse_frame_ub = tkinter.Frame(folder_frame_ub)
    browse_frame_ub.pack(side="top", fill='x', expand=1)
    run_button_ub = tkinter.Button(browse_frame_ub, text="Run", command=lambda: run_ub(def_values, folder_path_ub.get(), log_st, pdf_save_ub))
    run_button_ub.pack(side="right", padx=xpad, pady=ypad, ipadx=2)
    browse_button_ub = tkinter.Button(browse_frame_ub, text="Browse", command=lambda : browse_click(def_values, folder_path_ub), padx=2)
    browse_button_ub.pack(side="right", padx=xpad, pady=ypad, ipadx=2)
    folder_path_ub_tb = tkinter.Entry(browse_frame_ub, textvariable=folder_path_ub)
    folder_path_ub_tb.pack(fill='x', expand=1, side="left", padx=xpad, pady=ypad)

    # Smoothed and unsmoothed graphs checkbox's
    checkb_frame_ub = tkinter.Frame(folder_frame_ub)
    checkb_frame_ub.pack(side="bottom", fill='x', expand=1)
    pdf_cb = tkinter.Checkbutton(checkb_frame_ub, text="Save PDF (processor intensive)", variable=pdf_save_ub, onvalue=True, offvalue=False)
    pdf_cb.pack(side="left", padx=xpad, pady=ypad-3)
    pdf_cb.select()


    # -------------------------------------------------------------------------------
    #  Action Log Field
    # -------------------------------------------------------------------------------
    log_frame = tkinter.LabelFrame(window, text="Action Log")
    log_frame.pack(side="top", fill='x', expand=1, padx=xpad, pady=ypad)

    log_st = tkinter.scrolledtext.ScrolledText(log_frame, undo=True, borderwidth=3, wrap='word', height=12, state="disabled")
    log_st.pack(fill='x', expand=1, side="top", padx=xpad, pady=ypad)

    # -------------------------------------------------------------------------------
    #  Bottom buttons (get default values)
    # -------------------------------------------------------------------------------
    btm_but_frame = tkinter.Frame(window)
    btm_but_frame.pack(side="left", padx=5, pady=5)

    change_def_val_button = tkinter.Button(btm_but_frame, text="Change Default Values", command=lambda : change_def_values(def_values, def_values, folder_path_cal, folder_path_ub))
    change_def_val_button.pack(side="left", padx=xpad, pady=ypad)


    window.mainloop()

# -----------------------------------------------------------------------------------
#  Calibration procedures
# -----------------------------------------------------------------------------------
def run_cal(def_values, folder_path, o_logbox, _def_values, o_date_string, o_eqn_string, o_cal_frame, o_smoothed_graph, o_unsmoothed_graph, o_ph_stacked_graph):
    # Remove the \ at the end of a folder if it exists
    split_folder_path = folder_path.split("\\")
    if split_folder_path[len(split_folder_path) - 1] == "":
        split_folder_path.remove("")
        folder_path = "\\".join(split_folder_path)
    _exists = check_path_validity(folder_path)
    # Let's make sure that the path is correct
    def_values.cal_path = folder_path
    _numfiles = len(glob.glob1(folder_path,"*.txt"))
    calculate = True
    if _numfiles == 0:
        _message = "There are no .txt files in the directory: {0}".format(folder_path)
        calculate = False
    elif _exists == False:
        _message = "The path '{0}' does not exist".format(folder_path)
        calculate = False
    elif _numfiles == 1:
        _message = "Calculating calibration line for the single *.txt file in: {0}".format(folder_path)
    else:
        _message = "Calculating calibration line for all {0} *.txt files in: {1}".format(_numfiles, folder_path)
    log.functions.log(True, "info", _message, o_logbox)
    if calculate:
        log.functions.log(True, "info", "Please wait...", o_logbox)
        time_start = time.time()
        # So plot_directories knows if it needs to do graphs
        _def_values.cal_smoothed_graph = o_smoothed_graph.get()
        _def_values.cal_unsmoothed_graph = o_unsmoothed_graph.get()
        _def_values.cal_ph_stacked_graph = o_ph_stacked_graph.get()
        data_minip.ph_script.plot_directories(folder_path, o_logbox, _def_values)

        u_date_lb(o_date_string, _def_values.cal_date, False)
        u_eqn_lb(o_eqn_string, _def_values.cal_slope, _def_values.cal_intercept, _def_values.cal_rsquared)
        time_taken = time.time() - time_start
        log.functions.log(True, "info", r"Done {files} files in {time:.2f} seconds! Yatta ^.^".format(files=_numfiles, time=time_taken), o_logbox)
        log.functions.log(True, "info", "Showing graph(s). Please close all graphs to contiue to use this window.", o_logbox)
        # plt.show() MUST get called last: user input means the UI is halted until graphs are closed
        plt.show()

def u_date_lb(o_stringvar, date, update_ini):
    o_stringvar.set("The calibration was last calculated on: {0}".format(date))
    if update_ini:
        file_handling.conf_values.set("Calibration", "date", date)

def u_eqn_lb(o_stringvar, slope, intercept, rsquared):
    o_stringvar.set("R-squared: {0}   |   y = {1}x + {2}".format(rsquared, slope, intercept))

# -----------------------------------------------------------------------------------
#  Unbuffered Procedure
# -----------------------------------------------------------------------------------
def run_ub(def_values, folder_path, o_logbox, o_pdf_var):
    split_folder_path = folder_path.split("\\")
    if split_folder_path[len(split_folder_path) - 1] == "":
        split_folder_path.remove("")
        folder_path = "\\".join(split_folder_path)
    _exists = check_path_validity(folder_path)

    # Just to make sure we're using the most up to date folder path
    def_values.ub_path = folder_path
    # So we know if we want to save the pdf
    def_values.ub_save_pdf = o_pdf_var.get()

    _numfiles = len(glob.glob1(folder_path,"*.txt"))
    calculate = True
    if _numfiles == 0:
        _message = "There are no .txt files in the directory: {0}".format(folder_path)
        calculate = False
    elif _exists == False:
        _message = "The path '{0}' does not exist".format(folder_path)
        calculate = False
    else:
        _message = "Calculating 2nd derivative for {0} *.txt files in: {1}".format(_numfiles, folder_path)

    log.functions.log(True, "info", _message, o_logbox)
    if calculate:
        time_start = time.time()
        # Call the calculation procedure
        data_minip.unbuffered.unbuffered_calculation(o_logbox, def_values)

        time_taken = time.time() - time_start
        _log_string = None
        if time_taken < 120:
            _log_string = r"Done {files} files in {time:.2f} seconds! Yatta ^.^".format(files=_numfiles, time=time_taken)
        elif time_taken >= 120 and time_taken < 600:
            _log_string = r"Done {files} files in {time:.2f} seconds! Yatta ^.^ That was hard".format(files=_numfiles, time=time_taken)
        elif time_taken >= 600:
            _log_string = r"Done {files} files in {time:.2f} seconds! Yatta ^.^ Phew, that was tricky".format(files=_numfiles, time=time_taken)
        log.functions.log(True, "info", _log_string, o_logbox)

# -----------------------------------------------------------------------------------
#  Change default values Procedure
# -----------------------------------------------------------------------------------
def change_def_values(def_values, cur_values, folder_path_cal, folder_path_ub):
    # Create a new window, as a child of the master, to allow user changes to the .conf file
    top = tkinter.Toplevel()
    ui.settings.show(top, def_values, folder_path_cal, folder_path_ub)

# -----------------------------------------------------------------------------------
#  Misc. Procedures
# -----------------------------------------------------------------------------------
def browse_click(cur_values, o_folder_path):
    _path = tkinter.filedialog.askdirectory()
    # If the user decides not to change the directory, best not change it!
    if _path != "":
        o_folder_path.set(_path)
        cur_values.path = o_folder_path.get()

def check_path_validity(_path):
    exists = os.path.isdir(_path)
    return exists
