# -*- coding: utf-8 -*-
import tkinter
import data_minip.unbuffered

# ----------------------------------------------------------------------------------
# Called Function
# ----------------------------------------------------------------------------------
def show(def_values, o_logbox, list_rn, data_set):
    # Create the toplevel window
    top = tkinter.Toplevel()
    top.title("Unbuffered Plot".format(def_values.version))
    # Set the .ico from the ui folder
    top.iconbitmap("{0}/ui/aion.ico".format(def_values.program_path))
    # Set toplevel window size
    top.minsize(250, 150)
    top.resizable(True, False)

    build(top, list_rn, def_values, data_set, o_logbox)

# ----------------------------------------------------------------------------------
#  Only used in this module
# ----------------------------------------------------------------------------------
def build(_window, _fields, def_values, data_set, o_logbox):
    checkbox_list = []

    # Create the descriptior lebel
    top_label = tkinter.Label(_window, text = "Which values do you wish to plot?", anchor = 'w')
    top_label.pack(side = "top", fill = 'x', padx = 5, pady = 5)

    label_frame = tkinter.LabelFrame(_window, text = "Run number")
    label_frame.pack(side = "top", fill = 'x', padx = 5, pady = 2)

    for field in _fields:
        # Create the variable for teh cb
        var = tkinter.BooleanVar()
        cb = tkinter.Checkbutton(label_frame, text = field, anchor = 'w', variable = var, onvalue = True, offvalue = False)
        cb.pack(side = "top", fill = 'x', padx = 1, pady = 1)
        # Let's save those variables for later use
        checkbox_list.append((field, var))

    plot_bt = tkinter.Button(_window, text = "Plot", command=lambda: data_minip.unbuffered.plot(checkbox_list, def_values, o_logbox, data_set, _window))
    plot_bt.pack(side = "top", padx = 3, pady = 3, ipadx = 2)