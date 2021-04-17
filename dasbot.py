# TODO: add Hint; reply once if /start is repeated; repeat last question if answer unclear
# TODO: use Motor for Mongo?

import logging

import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from pymongo import MongoClient

from dasbot.interface import Interface
from dasbot.broadcaster import Broadcaster
from dasbot.chats_repo import ChatsRepo
from dasbot.controller import Controller
from dasbot.menu_controller import MenuController

from dynaconf import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


if __name__ == '__main__':

    # Initialize bot & dispatcher
    bot = Bot(token=settings.TOKEN)
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
        await menucon.main(message)

    # handler for the settings menu callbacks
    @dp.callback_query_handler()
    async def settings_select(query: types.CallbackQuery):
        log.debug('callback query received: %s', query)
        await menucon.navigate(query)

    # generic message handler; should be last
    @dp.message_handler()
    async def all_other_messages(message: types.Message):
        log.debug('generic message received: %s', message)
        await chatcon.generic(message)

    # TODO: Add DB auth
    client = MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    chats_repo = ChatsRepo(db['chats'], db['scores'], db['stats'])

    chatcon = Controller(bot, chats_repo)
    menucon = MenuController(Interface(bot), chats_repo)
    broadcaster = Broadcaster(Interface(bot), chats_repo)

    loop = asyncio.get_event_loop()
    loop.create_task(broadcaster.run())
    executor.start_polling(dp)
