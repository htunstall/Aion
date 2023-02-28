class DefaultConf:
    version = None
    path = None
    program_path = None
    log_path = None
    log_level = None
    version_date = None

    cal_date = None
    cal_path = None
    cal_slope = None
    cal_intercept = None
    cal_rsquared = None
    cal_smoothed_graph = None
    cal_unsmoothed_graph = None
    cal_ph_stacked_graph = None

    ub_path = None
    ub_ma_point_factor = None
    ub_truncate_factor = None
    ub_save_pdf = None

    cal_x_axis_label = None
    cal_x_axis_units = None
    cal_y_axis_label = None
    cal_y_axis_units = None
    swv_y_axis_label = None
    swv_y_axis_units = None

class UnbufferedData:
    filename = None
    filename_less_repeat = None
    fullpath = None
    second_der = None

    filename_ph = None # Cast into as a flot
    calculated_ph = None

    repeat_number = None
    set_average_ph = None
    avg_error_ph = None
    error_ph = None
