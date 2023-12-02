import logging

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiohttp import web

from pymongo import MongoClient
from urllib.parse import urlparse, quote_plus

from dasbot.db.dict_repo import DictRepo
from dasbot.db.chats_repo import ChatsRepo
from dasbot.db.stats_repo import StatsRepo
from dasbot.interface import Interface
from dasbot.broadcaster import Broadcaster
from dasbot.controller import Controller
from dasbot.menu_controller import MenuController, MenuCallback

from dynaconf import Dynaconf

settings = Dynaconf(environments=['default', 'production', 'development'],
                    settings_file='settings.toml',
                    load_dotenv=True)

logging.basicConfig(level=logging.DEBUG if settings.get('DEBUG') else logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


def main() -> None:
    dp = Dispatcher()
    bot = Bot(settings.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)

    log.debug('connecting to database: %s', settings.DB_ADDRESS)
    db_uri = urlparse(settings.DB_ADDRESS)
    if settings.get('DB_USERNAME'):
        creds = ':'.join([
            quote_plus(settings.DB_USERNAME),
            quote_plus(settings.get('DB_PASSWORD'))
        ])
        db_uri = db_uri._replace(netloc='@'.join([creds, db_uri.hostname]))
    client = MongoClient(db_uri.geturl())
    db = client[settings.DB_NAME]

    dictionary = DictRepo(db['dictionary']).load()
    chats_repo = ChatsRepo(db['chats'], db['scores'])
    stats_repo = StatsRepo(db['scores'], db['stats'])
    chatcon = Controller(bot, chats_repo, stats_repo, dictionary)
    broadcaster = Broadcaster(Interface(bot), chats_repo, dictionary)
    menucon = MenuController(Interface(bot), chats_repo)


    # /help command handler
    @dp.message(Command('help'))
    async def help_command(message: Message):
        log.debug('/help received: %s', message)
        await chatcon.help(message)

    # /start command handler
    @dp.message(CommandStart())
    async def start_command(message: Message):
        log.debug('/start received: %s', message)
        await chatcon.start(message)

    # /settings command handler
    @dp.message(Command('settings'))
    async def settings_command(message: Message):
        log.debug('/settings received: %s', message)
        await menucon.main(message)

    # handler for the settings menu callbacks
    @dp.callback_query(MenuCallback.filter())
    async def settings_navigate(query: CallbackQuery, callback_data: MenuCallback):
        log.debug('callback query received: %s', query)
        await menucon.navigate(query, callback_data)

    # /stats command handler
    @dp.message(Command('stats'))
    async def stats_command(message: Message):
        log.debug('/stats received: %s', message)
        await chatcon.stats(message, dictionary)

    # generic message handler; should be last
    @dp.message()
    async def all_other_messages(message: Message):
        log.debug('generic message received: %s', message)
        await chatcon.generic(message)


    broadcast_enabled = settings.get('BROADCAST')
    if settings.get('MODE').lower() == 'webhook':
        async def on_startup(bot: Bot):
            webhook_url = f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}"
            log.info('setting webhook: %s', webhook_url)
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(webhook_url,  secret_token=settings.WEBHOOK_SECRET)
            if broadcast_enabled:
                asyncio.create_task(broadcaster.run())

        dp.startup.register(on_startup)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.WEBHOOK_SECRET,
        )
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host=settings.WEBAPP_HOST, port=settings.WEBAPP_PORT)
    else:
        if broadcast_enabled:
            asyncio.create_task(broadcaster.run())
        bot.delete_webhook(drop_pending_updates=True) # ok for polling too
        dp.start_polling(bot)


if __name__ == '__main__':
    main()
