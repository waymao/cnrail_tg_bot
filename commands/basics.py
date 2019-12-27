# basics.py
# basic functions for greeting etc.
# By waymao in 2019

from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

# Welcome msg
@run_async
def start(bot, update):
    text = 'Hi {}, I\'m a bot, and you can ask me about the chinese railway!'.\
        format(update.message.from_user['username'])
    bot.send_message(chat_id=update.message.chat_id, text=text,
        reply_to_message_id=update.message.message_id)

start_handler = CommandHandler('start', start)
