# TODO: add Hint; reply once if /start is repeated; repeat last question if answer unclear
# TODO: also use Motor for Mongo?
# TODO: Exception handling: sending stuff to a chat that has removed bot

import logging
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from mongomock import MongoClient

from dasbot import config
from dasbot.scheduler import Scheduler
from dasbot.chats_repo import ChatsRepo
from dasbot.controller import Controller

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initialize bot & dispatcher
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


# /help command handler
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    log.debug('/help received: %s', message)
    await chatcon.help(message)


# /start command handler
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    log.debug('/start received: %s', message)
    await chatcon.start(message)


# generic message handler
@dp.message_handler()
async def any_msg_handler(message: types.Message):
    log.debug('generic message received: %s', message)
    await chatcon.generic(message)


# # /settings command handler
# @dp.message_handler(commands=['settings'])
# async def process_settings_command(message: types.Message):
#     pass


if __name__ == '__main__':
    # TODO: Add username & password
    client = MongoClient(config.DB_ADDRESS)
    db = client[config.DB_NAME]
    chats_repo = ChatsRepo(db['chats'])

    chatcon = Controller(bot, chats_repo)
    scheduler = Scheduler(bot, chats_repo)

    loop = asyncio.get_event_loop()
    loop.create_task(scheduler.run())
    executor.start_polling(dp)
