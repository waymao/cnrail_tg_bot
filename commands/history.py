import bot_config
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async
import telegram.error
import logging
from railroad_lib import train_history
from prettytable import PrettyTable
from datetime import datetime, timedelta
import pytz

tz = pytz.timezone('Asia/Shanghai')


# Sample data:
#{'train_no': 'G7501',
# 'train_id': '3776',
# 'train_type': 'CRH380BL',
# 'train_date': '2019-06-14',
# 'company': '上海局'}
#
# General function for formatting a message.
# input: train_list, the list passed from the get_mysql function.
#        no_first, whether we put the number first or not.
# output: formatted string to be sent to the client.
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
        text = "**{}**车次，由{} **{}-{}**， 最近一次于 **{}** 执行。".format(
            train_list['train_no'], 
            train_list['company'],
            train_list['train_type'],
            train_list['train_id'],
            train_list['train_date']
        )
    return text + "\n"


# Handling function for train_no query
@run_async
def train_no(update, context):
    if len(context.args) == 1:
        # get data
        msg = context.bot.send_message(chat_id=update.message.chat_id,
            text="Loading...", reply_to_message_id=update.message.message_id)
        result = train_history.get_train_no_wo_type(context.args[0])
        data_link_msg = ""
    elif len(context.args) == 2:
        # get data
        msg = context.bot.send_message(chat_id=update.message.chat_id,
            text="Loading...", reply_to_message_id=update.message.message_id)
        result = train_history.get_train_no_w_type(context.args[1], context.args[0])

        # compute link to data
        now_time = datetime.now(tz).strftime("%Y-%m-%d")
        old_time = (datetime.now(tz) - timedelta(days=15)).strftime("%Y-%m-%d")
        data_link_msg = "\nTo view more history, please [visit here]" + \
        "(https://t.lifanz.cn/trainhistory.php?train_name={}-{}&daterange={}%2C{})."\
        .format(context.args[0], context.args[1], old_time, now_time)
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /getno <Train Registration> [type]",
            reply_to_message_id=update.message.message_id)
        return
    
    if not result:
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text="Your query did not return any results.", 
            message_id = msg.message_id)
    else:
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text=make_message(result, True) + data_link_msg, 
            parse_mode=telegram.ParseMode.MARKDOWN, 
            message_id = msg.message_id)


# Handling function for train_registration query
@run_async
def train_info(update, context):
    if len(context.args) == 1:
        msg = context.bot.send_message(chat_id=update.message.chat_id,
            text="Loading...", reply_to_message_id=update.message.message_id)
        result = train_history.get_train_id(context.args[0])

        # compute link to data
        now_time = datetime.now(tz).strftime("%Y-%m-%d")
        old_time = (datetime.now(tz) - timedelta(days=15)).strftime("%Y-%m-%d")
        data_link_msg = "\nTo view more history, please [visit here]" + \
        "(https://t.lifanz.cn/searchtrain.php?train_num={}&daterange={}%2C{})."\
        .format(context.args[0], old_time, now_time)
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /getreg <Train No> [type]",
            reply_to_message_id=update.message.message_id)
        return
    
    if not result:
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text="Your query did not return any results.", 
            message_id = msg.message_id)
    else:
        context.bot.edit_message_text(chat_id=update.message.chat_id,
            text=make_message(result, False) + data_link_msg, 
            parse_mode=telegram.ParseMode.MARKDOWN, message_id = msg.message_id)

train_info_handler = CommandHandler('getreg', train_info, pass_args=True)
train_no_handler = CommandHandler('getno', train_no, pass_args=True)
