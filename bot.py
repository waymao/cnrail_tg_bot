# bot.py
# Core functionalities for the bot.
# By waymao in 2019

from telegram.ext import Updater, CommandHandler
import bot_config, bot_logging
import commands

updater = Updater(token=bot_config.TG_TOKEN)

# add handlers to the commands.
for handler in commands.handlers:
    updater.dispatcher.add_handler(handler)

updater.start_polling()
