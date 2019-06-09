# __init__.py
# init.py for the commands folder
# By waymao in 2019

from . import basics, timetable

handlers = [
    basics.start_handler,
    timetable.timetable_handler,
    timetable.calendar_handler
]