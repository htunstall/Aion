import tkinter
import file_handling.conf_values

# -----------------------------------------------------------------------------------
#  Variables only used in this module
# -----------------------------------------------------------------------------------
fields = []
section = []
option = []
value = []
width_l = 30 # Label width

# -----------------------------------------------------------------------------------
#  Only used in this module
# -----------------------------------------------------------------------------------
def build(_window, _fields):
   entries = []
   for field in _fields:
      row = tkinter.Frame(_window)
      lab = tkinter.Label(row, width = width_l, text  =field, anchor = 'w')
      ent = tkinter.Entry(row)
      row.pack(side = "top", fill = 'x', padx = 5, pady = 5)
      lab.pack(side = "left")
      ent.pack(side = "right", expand = 1, fill = 'x')
      entries.append((field, ent))
   return entries

def populate_lists(_def_values):
    fields.clear()
    section.clear()
    option.clear()
    value.clear()
    # Unfortunately not ittarateable T.T
    fields.append("Calibration Path:")
    section.append("Calibration")
    option.append("path")
    value.append(_def_values.cal_path)

    fields.append("Unbuffered Path:")
    section.append("Unbuffered")
    option.append("path")
    value.append(_def_values.ub_path)

    fields.append("Moving Average Smoothing Factor:")
    section.append("Unbuffered")
    option.append("ma_point_factor")
    value.append(_def_values.ub_ma_point_factor)

    fields.append("Truncation Factor:")
    section.append("Unbuffered")
    option.append("truncate_factor")
    value.append(_def_values.ub_truncate_factor)

    fields.append("Calibration Graph x-axis Label:")
    section.append("Graphing")
    option.append("cal_x_axis_label")
    value.append(_def_values.cal_x_axis_label)

    fields.append("Calibration Graph x-axis Units:")
    section.append("Graphing")
    option.append("cal_x_axis_units")
    value.append(_def_values.cal_x_axis_units)

    fields.append("Calibration Graph y-axis Label:")
    section.append("Graphing")
    option.append("cal_y_axis_label")
    value.append(_def_values.cal_y_axis_label)

    fields.append("Calibration Graph y-axis Units:")
    section.append("Graphing")
    option.append("cal_y_axis_units")
    value.append(_def_values.cal_y_axis_units)

    fields.append("SWV Graph y-axis Label:")
    section.append("Graphing")
    option.append("swv_y_axis_label")
    value.append(_def_values.swv_y_axis_label)

    fields.append("SWV Graph y-axis Units:")
    section.append("Graphing")
    option.append("swv_y_axis_units")
    value.append(_def_values.swv_y_axis_units)

# MUST be updated with populate lists IN ORDER!
# MUST be called in confirm procedure AFTER the for loop updating the value list!
# Located here to be next to the populate_lists procedure
def update_def_values(_def_values):
    _def_values.cal_path = value[0]
    _def_values.ub_path = value[1]
    _def_values.ub_ma_point_factor = value[2]
    _def_values.ub_truncate_factor = value[3]
    _def_values.cal_x_axis_label = value[4]
    _def_values.cal_x_axis_units = value[5]
    _def_values.cal_y_axis_label = value[6]
    _def_values.cal_y_axis_units = value[7]
    _def_values.swv_y_axis_label = value[8]
    _def_values.swv_y_axis_units = value[9]

def populate_ui(_ent):
    for i in range(0,len(_ent)):
        _ent[i][1].insert(0,value[i])

def confirm(window, _ent, _def_values, folder_path_cal, folder_path_ub):
    for i in range(0,len(_ent)):
        value[i] = _ent[i][1].get()
    update_def_values(_def_values)
    folder_path_cal.set(value[0])
    folder_path_ub.set(value[1])
    file_handling.conf_values.set_list(section, option, value)
    window.destroy()

def discard(window):
    window.destroy()

# -----------------------------------------------------------------------------------
# Called Function
# -----------------------------------------------------------------------------------
def show(window, def_values, folder_path_cal, folder_path_ub):
    window.title("Aion - Ver: {0} - Default Value Setting".format(def_values.version))
    # Set the .ico from the ui folder
    window.iconbitmap("{0}/ui/aion.ico".format(def_values.program_path))
    # Set toplevel window size
    window.minsize(900, 100)
    window.resizable(True, False)

    populate_lists(def_values)
    _entrys = build(window, fields)
    populate_ui(_entrys)

    tkinter.Button(window, text = "Confirm Changes", command=lambda : confirm(window, _entrys, def_values, folder_path_cal, folder_path_ub)).pack(side = "left", padx = 5, pady = 5)
    tkinter.Button(window, text = "Discard Changes", command=lambda : discard(window)).pack(side = "left", padx = 5, pady = 5)