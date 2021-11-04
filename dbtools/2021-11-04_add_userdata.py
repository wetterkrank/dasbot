# Adds user names to the db

import logging

import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import asyncio
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import exceptions, executor
from pymongo import MongoClient
from dynaconf import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


async def get_chat_data(chat_id):
    try:
        chat_data = await bot.get_chat(chat_id)
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{chat_id}]: invalid chat ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await get_chat_data(chat_id)
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{chat_id}]: chat is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{chat_id}]: failed")
    else:
        return chat_data
    return None

async def process_chats(chats_col):
    chats = chats_col.find({})
    for chat in chats:
        await asyncio.sleep(.1)
        data = await get_chat_data(chat['chat_id'])
        if data:
            user_data = {'username': data.username or data.title, 'first_name': data.first_name, 'last_name': data.last_name}
            print(chat['chat_id'], user_data)


if __name__ == '__main__':
    client = MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    chats_col = db['chats']

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(bot)

    executor.start(dp, process_chats(chats_col))