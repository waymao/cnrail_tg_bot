# query_time.py
# Used to search for timetable on 12306.
# By waymao in 2019

import bot_config
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async
import telegram.error
import requests, json
import re
import logging


# Gets the current version of the db.
def get_db_ver():
    js = requests.get("http://moerail.ml/version.js", headers=bot_config.header)
    match = re.findall(r'\d{4}.\d{2}.\d{2}', js.text)
    return match[0]

# get the image from the moerail server.
@run_async
def retrieve_img(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Invalid arguments. Usage: /graph <Train Number>",
            reply_to_message_id=update.message.message_id)
        return
    
    # get train num from arguments
    train_no = context.args[0].upper()

    # if it's not C, G or D, just exit.
    if train_no[0] not in ['C', 'G', 'D']:
        context.bot.send_message(chat_id=update.message.chat_id,
            text="Sorry, Graphs for Non-EMU trains are not available.",
            reply_to_message_id=update.message.message_id)
        return
    
    # Write the URL. I'm using moerail data for now.
    url = "http://moerail.ml/img/{}.png".format(train_no)
    response = requests.head(url, headers=bot_config.header)

    # Success:
    if response.status_code == 200:
        msg = context.bot.send_message(chat_id=update.message.chat_id,
              text="Loading the image...")
        db_version = get_db_ver()
        try:
            context.bot.send_photo(update.message.chat_id, url,
            reply_to_message_id=update.message.message_id)
        except telegram.error.TimedOut:
            context.bot.send_message(chat_id=update.message.chat_id,
              text="If you don\'t see the photo, please wait a few sec for it to upload.",
              reply_to_message_id=update.message.message_id)
            pass
        context.bot.edit_message_text(chat_id=update.message.chat_id,
                         message_id = msg.message_id,
            text='The planning graph is last updated on {}.'.format(db_version))
    # Train not found:
    elif response.status_code == 404:
        context.bot.send_message(chat_id=update.message.chat_id,
            text='Sorry, this train is not included in the db.',
            reply_to_message_id=update.message.message_id)
    # Some other weird error:
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
            text='Sorry, there\'s some error with the moerail server.',
            reply_to_message_id=update.message.message_id)

graph_handler = CommandHandler('graph', retrieve_img, pass_args=True)
