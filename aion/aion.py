import os
import classes.classes as classes
import ui.master
import file_handling.conf_values
import log.functions


# ----------------------------------------------------------------------------------
#  Gets the values from the .conf file
# ----------------------------------------------------------------------------------
def_values = classes.DefaultConf()

def_values.version = file_handling.conf_values.get("MiscValues", "version")
def_values.log_level = file_handling.conf_values.get("MiscValues", "log_level")
def_values.version_date = file_handling.conf_values.get("MiscValues", "update")

# Calibration values
def_values.cal_date = file_handling.conf_values.get("Calibration", "date")
def_values.cal_path = file_handling.conf_values.get("Calibration", "path")
def_values.cal_slope = file_handling.conf_values.get("Calibration", "slope")
def_values.cal_intercept = file_handling.conf_values.get("Calibration", "intercept")
def_values.cal_rsquared = file_handling.conf_values.get("Calibration", "r_squared")

# Unbuffered Values
def_values.ub_path = file_handling.conf_values.get("Unbuffered", "path")
def_values.ub_ma_point_factor = int(file_handling.conf_values.get("Unbuffered", "ma_point_factor"))
def_values.ub_truncate_factor = int(file_handling.conf_values.get("Unbuffered", "truncate_factor"))


# Graphing Values
def_values.cal_x_axis_label = file_handling.conf_values.get("Graphing", "cal_x_axis_label")
def_values.cal_x_axis_units = file_handling.conf_values.get("Graphing", "cal_x_axis_units")
def_values.cal_y_axis_label = file_handling.conf_values.get("Graphing", "cal_y_axis_label")
def_values.cal_y_axis_units = file_handling.conf_values.get("Graphing", "cal_y_axis_units")
def_values.swv_y_axis_label = file_handling.conf_values.get("Graphing", "swv_y_axis_label")
def_values.swv_y_axis_units = file_handling.conf_values.get("Graphing", "swv_y_axis_units")

# Grabs the program cwd and saves it to the current values class
def_values.program_path = os.getcwd()
# Generates the path for the log file (independent of where the initial script was run
log.functions.get_path(def_values)
# Initialises the log file
log.functions.init(def_values)



# ----------------------------------------------------------------------------------
#  Calls the master UI into being!
# ----------------------------------------------------------------------------------
ui.master.show(def_values)