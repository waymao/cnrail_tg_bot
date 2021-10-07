# train_wifi12306.py
# Used to search for timetable on com.wifi12306 .
# By AgFlore in 2021 based on waymao's work.

import logging
from datetime import datetime
import pytz
from telegram import ParseMode
from telegram.ext import CommandHandler
from railroad_lib import query_wifi12306

# Setting appropiate timezone.
tz = pytz.timezone('Asia/Shanghai')

def parse_timetable(train_data):
    if train_data:
        result_str = "<pre>"

        station_date = ''
        for one_station in train_data:
            if one_station.setdefault("trainDate", '?') != station_date:
                station_date = one_station["trainDate"]
                result_str += "   (%s)\n"%(station_date)

            # Sample line: "08 西安　　0940/0948 1509㎞ Z217 晚750分"
            delay_status = one_station.get('ticketDelay')
            delay_str = one_station.get("stationTrainCode")
            if delay_status:
                if delay_status == -1:
                    delay_str += " 晚点未定"
                elif delay_status == -2:
                    delay_str += " 停运"
                else:
                    delay_str += " 晚%s分"%(delay_status)

            result_str += "{} {}{}/{}\t{}㎞\t{}\n".format(
                one_station.get("stationNo"),
                one_station.get("stationName").ljust(4, '　'),
                one_station.get("arriveTime", '----'),
                one_station.get("startTime", '----'),
                str(one_station.get('distance')).rjust(4),
                delay_str
            )
        result_str += "</pre>"
        return result_str
    return ""

def parse_guide(train_data):
    if not train_data:
        return ""
    guide_payload = ""
    for one_station in train_data:
        this_station_info = ""
        if ("waitingRoom" in one_station) and (one_station["waitingRoom"] != '-'):
            this_station_info += "[候]%s " % (one_station["waitingRoom"])
        if ("wicket" in one_station) and (one_station["wicket"] != '-'):
            this_station_info += "[检]%s " % (one_station["wicket"])
        if ("exit" in one_station) and (one_station["exit"] != '-'):
            this_station_info += "[出]%s" % (one_station["exit"])
        # Print line only when it has content
        if this_station_info:
            # Sample line: "(SZH) 苏州 [候]普速东候车区,普速西候车区 [检]5A检票口 [出]南1出站口,南2出站口"
            guide_payload += "(%s) %s\t%s\n" % (
                one_station.get("stationTelecode"), one_station.get("stationName"), this_station_info)
    # Print block only if it has content
    if guide_payload:
        result_str = "Traveller's Guide:\n%s\n" % (guide_payload)
        return result_str
    return ""


def parse_compilation(train_no):
    '''
    Return sample:
    Compilation:
    01(P1) KD    0
    02(P1) YZ    118
    03(P1) YZ    118
    04(P1) YZ    112 D
    05(P1) YW    66
    '''
    train_compile = query_wifi12306.getTrainCompileListByTrainNo(train_no)
    if train_compile and (train_compile[0] != 'NO_DATA'):
        result_str = "Compilation: \n"
        for one_train in train_compile:
            result_str += "{}({}) {}{} {}\n".format(
                one_train.get('coachNo'),
                one_train.get('origin'),
                one_train.get('coachType'),
                str(one_train.get('limit1')).ljust(3),
                one_train.get('commentCode'))
        return result_str
    return ""

def parse_equipment(train_no):
    train_equipment = query_wifi12306.getTrainEquipmentByTrainNo(train_no)
    if train_equipment and (train_equipment[0] != 'NO_DATA'):
        result_str = "Equipment: \n"
        result_str += "%s\n"%(train_equipment)
        return result_str
    return ""

# main handler for the command.
def train_wifi(update, context):
    # Check valid args:
    if len(context.args) == 0:
        update.message.reply_text(text="Usage: `/train <Train No.> [Date]`\n\nNote: This command returns the scheduled timetable, which does not guarantee that the train actually runs on the date; you may use `/tt` for cross reference :D",
            reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN_V2)
        return
    if len(context.args) == 1:
        date = datetime.now(tz).strftime("%Y%m%d")
    elif len(context.args) != 2:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /train <Train Number>",
            reply_to_message_id=update.message.message_id)
        return
    else:
        date = query_wifi12306.date_to_integer(context.args[1])

    # Loading...
    text = "Please wait while I retrieve the timetable..."
    msg = context.bot.send_message(chat_id=update.message.chat_id, text=text,
        reply_to_message_id=update.message.message_id)

    train_code = context.args[0]
    train_data = query_wifi12306.getStoptimeByTrainCode(train_code, date)
    if train_data[0] != 'NO_DATA':
        result_str = parse_timetable(train_data)
        result_str += "\n<pre>%s</pre><pre>%s (%s - %s)\n%s</pre>\n<pre>%s</pre>"%(
            parse_guide(train_data),
            train_data[0].get("trainNo"),
            train_data[0].get('startDate'),
            train_data[0].get('stopDate'),
            parse_compilation(train_data[0].get("trainNo")),
            parse_equipment(train_data[0].get("trainNo")))

        # Edit message, replace placeholder
        context.bot.edit_message_text(chat_id=update.message.chat_id, text=result_str, message_id=msg.message_id, parse_mode=ParseMode.HTML)

    # Error Handling.
    else:
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text=train_data[1],
            message_id=msg.message_id)

    # Logs down each query.
    logging.info("User %s (id: %s) searched for %s on %s", update.message.from_user.username, update.message.from_user.id, train_code, date)

# Add handler for the functions.
train_handler = CommandHandler('train', train_wifi, pass_args=True, run_async=True)
train_handler_short = CommandHandler('tw', train_wifi, pass_args=True, run_async=True)
