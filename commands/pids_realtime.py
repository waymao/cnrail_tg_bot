# pids_realtime.py
# Used to get station's real-time PIDS board from com.wifi12306
# By AgFlore in 2021 based on waymao's work.

import logging
from datetime import datetime
import pytz
from telegram import ParseMode
from telegram.ext import CommandHandler
from railroad_lib import query_wifi12306

# Setting appropiate timezone.
tz = pytz.timezone('Asia/Shanghai')

def parse_timetable_line(one_train):
    line = "`%s`" %(one_train.get('trainCode', one_train.get('trainNo', '?')))
    if 'startStationName' in one_train and 'endStationName' in one_train:
        line += "`(%s-%s)`" % (one_train['startStationName'], one_train['endStationName'])
    arrive_time = one_train.get('arriveTime', '-')
    depart_time = one_train.get('departTime', '-')
    if arrive_time == depart_time:
        line += " `%s`" % arrive_time
    else:
        line += " `%s/%s`" % (arrive_time, depart_time)
    line += "\n"
    return line

def parse_timetable(station_code, date):
    station_table = query_wifi12306.queryStoptimeByStationCode(station_code, date)
    if station_table and (station_table[0] != "NO_DATA"):
        result_str = "Timetable: \n"
        station_table.sort(key=lambda one_train:one_train.get('departTime'))
        for one_train in station_table:
            result_str += parse_timetable_line(one_train)
        return result_str
    return ""

def timestamp_to_clock(timestamp):
    return datetime.fromtimestamp(timestamp/1000, tz=tz)

def parse_screen_line(line, ignore_ok=""):
    # The timestamp returned. Note that this is not necessarily the timestamp scheduled in the timetable.
    if line.get('arriveTime'):
        train_time = timestamp_to_clock(line['arriveTime']).strftime("%H:%M")
    else:
        train_time = timestamp_to_clock(line.get('departTime')).strftime("%H:%M")
    # Parse the train status
    # statuses = {1:'候车', 2:'开检', 3:'停检', 4:'正点', 5:'晚点', 6:'预计晚点', 7:'到站', 8:'停运'}
    status_code = line.get('status', 0)
    status_str = query_wifi12306.bigscreen_status_dict.get(status_code, status_code)
    delay_code = line.get('delay')
    if delay_code and status_code not in [5, 8]:
        if isinstance(delay_code, int) and delay_code<0:
            status_str += " 早%s分" % (-delay_code)
        else:
            status_str += " 晚%s分" % (delay_code)
    elif delay_code and status_code==5:
        status_str = "晚%s分" % (delay_code)
    start_end_str = "%s-%s" % (line.get('startStationName'), line.get('endStationName'))
    # Ignore trivial statuses by request
    if (not delay_code) and ((ignore_ok, status_code) in [('D', 1), ('A', 4)]):
        return ""
    # Line Sample: "D2776 太原南-郑州东　　22:57 [晚247分]"
    result_str = "%s %s%s [%s]\n" % (
        line.get('stationTrainCode').ljust(5),
        start_end_str.ljust(9, '　'),
        train_time, status_str)
    return result_str

def parse_screen(station_code, date, flag):
    flag_parser = {'D':('D','Departures',''), 'd':('D', 'Departures', 'D'), 'A':('A', 'Arrivals', ''), 'a':('A', 'Arrivals','A')}
    DA_type, da_string, ignore_ok = flag_parser.get(flag)
    screen = query_wifi12306.getBigScreenByStationCodeAndDate(station_code, date, DA_type)

    if screen and screen[0] != 'NO_DATA':
        result_str = "<pre>%s at %s (%s)\n\n" % (da_string, screen[0].get('currentStationName'), screen[0].get('currentStationCode'))
        if ignore_ok:
            result_str += "(Trains without any non-trivial status have been omitted from the table. They are expected to be running normally.)\n\n"
        for line in screen:
            result_str += parse_screen_line(line, ignore_ok)
            if len(result_str) > 4000:
                result_str += '(...)'
                break
        result_str += "\nUpdated at %s</pre>" % timestamp_to_clock(screen[0].get('updateTime'))
        return result_str
    return "No data were returned for your query."

def station_realtime(update, context):
    # Check valid args:
    if len(context.args) <= 0:
        update.message.reply_text(
            "Usage: /pids <Station Telecode> <A|D|a|d> [Date]\n\nFor a list of station telecodes consult https://kyfw.12306.cn/otn/resources/js/framework/station_name.js\nUse the flags for all [A]rrivals, [D]epartures, or for [a]rrivals/[d]epartures having non-trivial statuses only.",
            reply_to_message_id=update.message.message_id,)
        return
    elif len(context.args) > 3:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /pids <Station Telecode> <A|D|a|d> [Date]",
            reply_to_message_id=update.message.message_id)
        return
    if len(context.args) < 3:
        date = datetime.now(tz).strftime("%Y%m%d")
    else:
        date = query_wifi12306.date_to_integer(context.args[2])
    if len(context.args) < 2:
        query_type = 'A'
    else:
        query_type = context.args[1]

    # Loading...
    text = "Please wait while I retrieve the station's realtime PIDS..."
    msg = context.bot.send_message(chat_id=update.message.chat_id, text=text,
        reply_to_message_id=update.message.message_id)

    station_code = context.args[0].upper()
    result_str = parse_screen(station_code, date, query_type)

    # Edit message, replace placeholder
    context.bot.edit_message_text(chat_id=update.message.chat_id, text=result_str, message_id=msg.message_id, parse_mode=ParseMode.HTML)

    # Logs down each query.
    logging.info("User %s (id: %s) queryed for the screen of %s by %s on %s.", update.message.from_user.username, update.message.from_user.id, station_code, query_type, date)

# Add handler for the functions.
pids_handler = CommandHandler('pids', station_realtime, pass_args=True, run_async=True)
