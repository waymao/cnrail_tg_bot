# query_time.py
# Used to search for timetable on 12306.
# By waymao in 2019

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from railroad_lib import query12306
from telegram import ReplyKeyboardRemove
from telegram.ext.dispatcher import run_async
import requests, json
import re
import logging
import pytz
from datetime import datetime

# Setting appropiate timezone.
tz = pytz.timezone('Asia/Shanghai')

#train_info = TrainNoDB()
#train_info.update()

# function timetable
# main handler for the command.
def timetable(update, context):
    # Check valid args:
    if len(context.args) == 0:
        # calendar_func(bot, update)
        update.message.reply_text(text="Please enter the train no. \
                The calendar function is being developed.",
            reply_to_message_id=update.message.message_id)
        return
    if len(context.args) == 1:
        date = datetime.now(tz).strftime("%Y-%m-%d")
    elif len(context.args) != 2:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /tt <Train Number>",
            reply_to_message_id=update.message.message_id)
        return
    else:
        date = context.args[1]

    # Loading...
    text = "Please wait while I retrieve the timetable..."
    msg = context.bot.send_message(chat_id=update.message.chat_id, text=text,
        reply_to_message_id=update.message.message_id)

    train = context.args[0]

    try:
        # Calling lfz's code
        train_data = query12306.getTimeList(train, date)

        # First line
        result_str = "{} {}\t {} {}".format(
            train_data[0]["train_class_name"],
            train_data[0]['station_train_code'],
            date,
            train_data[-1]["arrive_day_str"]
        )

        # detailed timetable
        for one_station in train_data:
            result_str += "\n"
            result_str += "{} \t {} \t {}".format(
                one_station["station_name"].ljust(10),
                one_station["arrive_time"],
                one_station["start_time"]
            )

        # Edit message, replace placeholder
        context.bot.edit_message_text(chat_id=update.message.chat_id, text=result_str, message_id=msg.message_id)

    # Error Handling.
    # KeyError: somehow 12306 returned something with status code != 200
    except (KeyError, json.JSONDecodeError):
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text="Sorry, there is no such train no or the train does not run this day.",
            message_id=msg.message_id)
    # ConnectionError, Timeout: cannot access 12306
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text="Sorry. Could not establish a secure connection to the 12306 server.",
            message_id=msg.message_id)
    # Not found or blocked?
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            # a guess
            context.bot.edit_message_text(chat_id=update.message.chat_id,
                text="Sorry, there is no such train no or the train does not run this day.",
                message_id=msg.message_id)
        else:
            context.bot.edit_message_text(chat_id=update.message.chat_id,
                text="Sorry. Could not establish a connection to the 12306 server.",
                message_id=msg.message_id)

    # Logs down each query.
    logging.info("User {} (id: {}) searched for train {}".format(update.message.from_user.username, update.message.from_user.id, train))

# Add handler for the functions.
timetable_handler = CommandHandler('tt', timetable, pass_args=True, run_async=True)
