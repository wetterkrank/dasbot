import logging
import sentry_sdk

import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from dasbot.config import settings
from dasbot.db.database import Database
from dasbot.db.dict_repo import DictRepo
from dasbot.db.chats_repo import ChatsRepo
from dasbot.db.stats_repo import StatsRepo
from dasbot.interface import Interface
from dasbot.broadcaster import Broadcaster
from dasbot.controller import Controller
from dasbot.maintenance import Maintenance
from dasbot.menu_controller import MenuController, MenuCallback

if settings.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        enable_tracing=False
    )

logging.basicConfig(level=logging.DEBUG if settings.get('DEBUG') else logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


dp = Dispatcher()
bot = Bot(settings.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
db = Database(settings).connect()

dictionary = DictRepo(db['dictionary']).load()
chats_repo = ChatsRepo(db['chats'], db['scores'])
stats_repo = StatsRepo(db['scores'], db['stats'])
chatcon = Controller(bot, chats_repo, stats_repo, dictionary)
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
    await chatcon.stats(message)

# generic message handler; should be last
@dp.message()
async def all_other_messages(message: Message):
    log.debug('generic message received: %s', message)
    await chatcon.generic(message)


def add_coroutines():
  broadcaster = Broadcaster(Interface(bot), chats_repo, dictionary)
  maintenance = Maintenance(stats_repo)
  if settings.get('BROADCAST'):
    asyncio.create_task(broadcaster.run())
  asyncio.create_task(maintenance.run())

async def polling():
  add_coroutines()
  await bot.delete_webhook(drop_pending_updates=True) # ok for polling too
  await dp.start_polling(bot)

def run_webhook():
  async def on_startup(bot: Bot):
      add_coroutines()
      webhook_url = f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}"
      log.info('Setting webhook: %s', webhook_url)
      await bot.delete_webhook(drop_pending_updates=True)
      await bot.set_webhook(webhook_url,  secret_token=settings.WEBHOOK_SECRET)

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


if settings.get('MODE').lower() == 'webhook':
  run_webhook()
else:
  asyncio.run(polling())
