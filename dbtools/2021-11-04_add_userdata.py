# One-off script to add user names to the db

from dynaconf import settings
from aiogram.utils import exceptions, executor
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import pymongo
import asyncio
import logging

import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))


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
        log.error(
            f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await get_chat_data(chat_id)
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{chat_id}]: chat is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{chat_id}]: failed")
    else:
        return chat_data
    return None


def insert_data(chat_id, data):
    query = {"chat_id": chat_id}
    update = {"$set": data}
    try:
        result = chats_col.update_one(query, update, upsert=False)
        return result.matched_count > 0
    except pymongo.errors.PyMongoError as e:
        log.debug(e)
        return False


async def process_chats(chats_col):
    chats = chats_col.find({})
    for chat in chats:
        chat_id = chat['chat_id']
        chat_data = await get_chat_data(chat_id)
        if chat_data:
            # chat_data.title for groups -- let's ignore for now
            user_data = {'user': {'username': chat_data.username,
                         'first_name': chat_data.first_name, 'last_name': chat_data.last_name}}
            updated = insert_data(chat_id, user_data)
            if updated:
                print(chat_id, user_data, 'UPDATED')
            else:
                print(chat_id, user_data, 'NOT UPDATED')
        await asyncio.sleep(.1)


if __name__ == '__main__':
    client = pymongo.MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    chats_col = db['chats']

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(bot)

    executor.start(dp, process_chats(chats_col))
