from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env.local')

import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from src import handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=os.getenv('BOT_TOKEN'))
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', handlers.start)
tag_handler = CommandHandler('tag', handlers.add_tag,
                             pass_args=True)
search_handler = CommandHandler('search', handlers.search_messages,
                                pass_args=True)
forward_handler = MessageHandler(Filters.forwarded, handlers.bookmark)
message_update_tag_handler = CallbackQueryHandler(
        handlers.set_bookmark,
        pattern="^.*?\\btag_id\\b.*?$")
message_update_done_handler = CallbackQueryHandler(
        handlers.clear_message_from_history,
        pattern="^.*?\\bdone\\b.*?$")
message_pagination_handler= CallbackQueryHandler(
        handlers.update_message_tags,
        pattern="^.*?\\bpage\\b.*?$")

dispatcher.add_handler(start_handler)
dispatcher.add_handler(tag_handler)
dispatcher.add_handler(forward_handler)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(message_update_tag_handler)
dispatcher.add_handler(message_update_done_handler)
dispatcher.add_handler(message_pagination_handler)
updater.start_polling()
