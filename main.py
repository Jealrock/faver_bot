from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env.local')

import os
import logging
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler, RegexHandler
)
from src import handlers
from database import db
import db_initializer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

db_initializer.bind_models_to_db(db)
updater = Updater(token=os.getenv('BOT_TOKEN'))
dispatcher = updater.dispatcher

# Command handlers
start_handler = CommandHandler('start', handlers.CommandHandler)
tag_handler = CommandHandler('tag', handlers.CommandHandler, pass_args=True)
search_handler = CommandHandler('search', handlers.CommandHandler, pass_args=True)

forward_handler = MessageHandler(Filters.forwarded, handlers.ForwardMessageHandler)
inline_callbacks_handler = CallbackQueryHandler(handlers.InlineCallbackHandler)

reply_keyboard_handler = RegexHandler('^(<|>)$', handlers.ReplyKeyboardCallbackHandler)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(tag_handler)
dispatcher.add_handler(forward_handler)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(inline_callbacks_handler)
dispatcher.add_handler(reply_keyboard_handler)
updater.start_polling()
