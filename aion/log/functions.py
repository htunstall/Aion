import logging
import datetime
import time
import os

def get_path(o_values):
    o_values.log_path = o_values.program_path[:-4] + "logs/"

def init(o_values):
    now = datetime.datetime.now()
    filename = "{year}-{month:02d}-{day:02d}--{hour:02d}-{minute:02d}-{second:02d}.log".format(year = now.year, month = now.month, day = now.day, hour = now.hour, minute = now.minute, second = now.second)
    if not os.path.isdir(o_values.log_path):
        # Create the log folder if it does not exist
        os.makedirs(o_values.log_path)
    logging.basicConfig(filename = o_values.log_path + filename, format = '%(asctime)s :%(levelname)s: %(message)s', datefmt = '%m/%d/%Y %I:%M:%S %p', level = int(o_values.log_level))


def log(display, level, message, o_logbox):
    if display:
        _user_message = "{} - {}".format(time.strftime("%H:%M"), message)
        o_logbox.config(state = "normal")
        o_logbox.insert("end", _user_message + "\n")
        o_logbox.see("end")
        o_logbox.config(state = "disabled")
    if level=="info":
        logging.info(message)
    elif level=="warning":
        logging.warning(message)
    elif level=="debug":
        logging.debug(message)
    o_logbox.update()