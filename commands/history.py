import bot_config
from telegram.ext import Updater, CommandHandler
import telegram.error
import logging
from railroad_lib import train_history
from prettytable import PrettyTable
from datetime import datetime, timedelta
import pytz

tz = pytz.timezone('Asia/Shanghai')

{'train_no': 'G7501',
 'train_id': '3776',
 'train_type': 'CRH380BL',
 'train_date': '2019-06-14',
 'company': '上海局'}
# General function for formatting a message.
# input: train_list, the list passed from the get_mysql function.
#        no_first, whether we put the number first or not.
# output: formatted string to be sent to the client.
# TODO: Completely seperate the make message functions for train no and reg.
def make_message(train_list, no_first):
    # t = PrettyTable(['NO', 'Registration', 'Type', 'Date', 'Company'])
    if no_first:
        text = "{}的列车注册号**{}-{}**，最近一次于**{}**在执行**{}**次任务"\
              .format(train_list['company'], 
                      train_list['train_type'],
                      train_list['train_id'],
                      train_list['train_date'],
                      train_list['train_no'])
    else:
        text = make_trainno_msg(train_list)
    return text


# Special function for formatting a message for train model and registration
#     query.
# input: train_list, the list passed from the get_mysql function.
# output: formatted string to be sent to the client.
def make_trainno_msg(train_list):
    # two trains running on the same day, i.e. chonglian
    if train_list[0]['train_date'] == train_list[1]['train_date']:
        text = "**{}**车次，由{} **{}-{}** 和 **{}-{}**， 最近一次于 **{}** 执行。".format(
            train_list[0]['train_no'], 
            train_list[0]['company'],
            train_list[0]['train_type'],
            train_list[0]['train_id'],
            train_list[1]['train_type'],
            train_list[1]['train_id'],
            train_list[0]['train_date']
        )
    else:
        text = "**{}**车次，由{} **{}-{}**重联， 最近一次于 **{}** 执行。".format(
            train_list[0]['train_no'], 
            train_list[0]['company'],
            train_list[0]['train_type'],
            train_list[0]['train_id'],
            train_list[0]['train_date']
        )
    return text


# Handling function for train_no query
def train_no(bot, update, args):
    if len(args) == 1:
        # get data
        msg = bot.send_message(chat_id=update.message.chat_id, text="Loading...")
        result = train_history.get_train_no_wo_type(args[0])
        data_link_msg = ""
    elif len(args) == 2:
        # get data
        msg = bot.send_message(chat_id=update.message.chat_id, text="Loading...")
        result = train_history.get_train_no_w_type(args[1], args[0])

        # compute link to data
        now_time = datetime.now(tz).strftime("%Y-%m-%d")
        old_time = (datetime.now(tz) - timedelta(days=15)).strftime("%Y-%m-%d")
        data_link_msg = "\nTo view more history, please [visit here](https://t.lifanz.cn/trainhistory.php?train_name={}-{}&daterange={}%2C{}).".format(args[0], args[1], old_time, now_time)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Invalid arguments. Usage: /getno <Train Registration> [type]")
        return
    
    if not result:
        bot.edit_message_text(chat_id=update.message.chat_id, text="Your query did not return any results.", message_id = msg.message_id)
    else:
        bot.edit_message_text(chat_id=update.message.chat_id, text=make_message(result, True) + data_link_msg, parse_mode=telegram.ParseMode.MARKDOWN, message_id = msg.message_id)

# Handling function for train_registration query
def train_info(bot, update, args):
    if len(args) == 1:
        msg = bot.send_message(chat_id=update.message.chat_id, text="Loading...")
        result = train_history.get_train_id(args[0])

        # compute link to data
        now_time = datetime.now(tz).strftime("%Y-%m-%d")
        old_time = (datetime.now(tz) - timedelta(days=15)).strftime("%Y-%m-%d")
        data_link_msg = "\nTo view more history, please [visit here](https://t.lifanz.cn/searchtrain.php?train_num={}&daterange={}%2C{}).".format(args[0], old_time, now_time)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Invalid arguments. Usage: /getreg <Train No> [type]")
        return
    
    if not result:
        bot.edit_message_text(chat_id=update.message.chat_id, text="Your query did not return any results.", message_id = msg.message_id)
    else:
        bot.edit_message_text(chat_id=update.message.chat_id, text=make_message(result, False) + data_link_msg, parse_mode=telegram.ParseMode.MARKDOWN, message_id = msg.message_id)

train_info_handler = CommandHandler('getreg', train_info, pass_args=True)
train_no_handler = CommandHandler('getno', train_no, pass_args=True)
