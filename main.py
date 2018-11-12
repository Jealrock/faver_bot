from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env.local')

import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from src import handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=os.getenv('BOT_TOKEN'))
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', handlers.start)
tag_handler = CommandHandler('tag', handlers.add_tag,
                             pass_args=True)
forward_handler = MessageHandler(Filters.forwarded, handlers.bookmark)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(tag_handler)
dispatcher.add_handler(forward_handler)
updater.start_polling()
