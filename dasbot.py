# TODO: add Hint; reply once if /start is repeated; repeat last question if answer unclear
# TODO: also use Motor for Mongo?
# TODO: Exception handling: sending stuff to a chat that has removed bot

import logging
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from pymongo import MongoClient

from dasbot import config
from dasbot.interface import Interface
from dasbot.scheduler import Scheduler
from dasbot.chats_repo import ChatsRepo
from dasbot.controller import Controller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


if __name__ == '__main__':

    # Initialize bot & dispatcher
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(bot)

    # /help command handler
    @dp.message_handler(commands='help')
    async def help_command(message: types.Message):
        log.debug('/help received: %s', message)
        await chatcon.help(message)

    # /start command handler
    @dp.message_handler(commands='start')
    async def start_command(message: types.Message):
        log.debug('/start received: %s', message)
        await chatcon.start(message)

    # /settings command handler
    @dp.message_handler(commands='settings')
    async def settings_command(message: types.Message):
        log.debug('/settings received: %s', message)
        await chatcon.settings(message)

    # generic message handler
    @dp.message_handler()
    async def all_other_messages(message: types.Message):
        log.debug('generic message received: %s', message)
        await chatcon.generic(message)

    # /settings callback: unsubscribe button
    @dp.callback_query_handler(text='UNSUBSCRIBE')
    async def settings_unsubscribe_callback(query: types.CallbackQuery):
        log.debug('UNSUBSCRIBE callback received: %s', query)
        await chatcon.settings_unsubscribe(query)

    # /settings callback: one of the time options
    @dp.callback_query_handler(text=Interface.time_choices)
    async def settings_timepref_callback(query: types.CallbackQuery):
        log.debug('quiz time preference callback received: %s', query)
        await chatcon.settings_timepref(query)

    # TODO: Add DB auth
    client = MongoClient(config.DB_ADDRESS)
    db = client[config.DB_NAME]['chats']
    chats_repo = ChatsRepo(db)

    chatcon = Controller(bot, chats_repo)
    scheduler = Scheduler(Interface(bot), chats_repo)

    loop = asyncio.get_event_loop()
    loop.create_task(scheduler.run())
    executor.start_polling(dp)
