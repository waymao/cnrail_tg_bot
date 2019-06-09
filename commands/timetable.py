# query_time.py
# Used to search for timetable on 12306.
# By waymao in 2019

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from railroad_lib import query12306
from telegram import ReplyKeyboardRemove
import requests, json
import re
import logging
import pytz
from datetime import datetime

# Setting appropiate timezone.
tz = pytz.timezone('Asia/Shanghai')

from telegram_calendar_keyboard import calendar_keyboard

# iPhone header for better acceptance.
header = {
    'User-Agent':'Mozilla/5.0 (iPad; CPU iPhone OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1'
    }


def calendar_func(bot, update):
    update.message.reply_text('Please select a date: ',
                        reply_markup=calendar_keyboard.create_calendar())

def inline_func(bot, update):
    result = calendar_keyboard.process_calendar_selection(bot, update)
    if result[0]:
        date = result[1]
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text='You selected {}'.format(date.strftime("%Y/%m/%d")),
                        reply_markup=ReplyKeyboardRemove())


class TrainNoDB:
    # Update the trainlist
    def update(self):
        response  = requests.get("https://kyfw.12306.cn/otn/resources/js/query/train_list.js",headers=header)
        result = response.content.decode('utf-8')
        real_json = result[16:]
        self.db = json.loads(real_json)
        logging.info('TrainInfo Updated')
        self.make_index()
    
    # Make an index (for search) from the train list.
    def make_index(self):
        self.train_index = {}
        self.train_no = []
        for t_type in self.db[datetime.now(tz).strftime("%Y-%m-%d")]:
            for train in self.db[datetime.now(tz).strftime("%Y-%m-%d")][t_type]:
                train_search = re.search(r'([A-Z]?\d+)', train['station_train_code'])
                # if found
                if train_search:
                    trainno = train_search.group(1)
                    self.train_no.append(trainno)

                    # After user have entered >=2 answers, we will show hints.
                    for i in range(2, len(trainno) + 1):
                        substr = trainno[0:i]
                        if substr in self.train_index.keys():
                            self.train_index[substr].append(trainno)
                        else:
                            self.train_index[substr] = [trainno]
        logging.info('TrainIndex Updated')
    
    def __init__(self):
        # self.update()
        pass

#train_info = TrainNoDB()
#train_info.update()

def timetable(bot, update, args):
    # Check valid args:
    if len(args) == 0:
        # calendar_func(bot, update)
        bot.send_message(chat_id=update.message.chat_id, text="日历功能设计中")
    if len(args) == 1:
        date = datetime.now(tz).strftime("%Y-%m-%d")
    elif len(args) != 2:
        bot.send_message(chat_id=update.message.chat_id, text="Invalid arguments. Usage: /tt <Train Number> <YYYY-MM-DD>")
        return
    else:
        date = args[1]
    
    # Loading...
    text = "Please wait while I retrieve the timetable..."
    msg = bot.send_message(chat_id=update.message.chat_id, text=text)

    train = args[0]

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
        bot.edit_message_text(chat_id=update.message.chat_id, text=result_str, message_id=msg.message_id)
    
    # Error Handling.
    # KeyError: somehow 12306 returned something with status code != 200
    except (KeyError, json.JSONDecodeError):
        bot.send_message(chat_id=update.message.chat_id,
            text="Sorry, there is no such train no or the train does not leave.")
    # ConnectionError, Timeout: cannot access 12306
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        bot.send_message(chat_id=update.message.chat_id,
            text="Sorry. Could not establish a secure connection to the 12306 server.")
    # Not found or blocked?
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            # a guess
            bot.send_message(chat_id=update.message.chat_id,
                text="Sorry, there is no such train no or the train does not leave.")
        else:
            bot.send_message(chat_id=update.message.chat_id,
                text="Sorry. Could not establish a connection to the 12306 server.")
    
    # Logs down each query.
    logging.info("User {} (id: {}) searched for train {}".format(update.message.from_user.username, update.message.from_user.id, train))

# Add handler for the functions.
timetable_handler = CommandHandler('tt', timetable, pass_args=True)
calendar_handler = CallbackQueryHandler(inline_func, pass_user_data=False)
