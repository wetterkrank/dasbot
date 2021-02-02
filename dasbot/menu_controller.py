import logging

from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData

from .interface import Interface

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

SETTINGS_ACTIONS = {
    1: {'main': 'display_submenu'},
    2: {
        'quiz_time': 'set_quiz_time',
        'quiz_len': 'set_quiz_length'
    }
}


class MenuController(object):
    def __init__(self, bot, chats_repo):
        self.bot = bot
        self.chats_repo = chats_repo
        self.ui = Interface(bot)
        self.callback = CallbackData('menu', 'level', 'id', 'action')  # menu:<level>:<id>:<action>

    # respond to /settings
    async def main(self, message: Message):
        await self.ui.settings_main(message, self.callback_generator)

    async def navigate(self, query):
        callback_data = self.callback.parse(query['data'])
        current_level = callback_data.get('level')
        menu_id = callback_data.get('id')
        action = callback_data.get('action')

        log.debug(f'parent menu: {menu_id}, current level: {current_level}, selected: {action}')
        # await message.message.edit_reply_markup(markup)

    def callback_generator(self, level, selected_id, action):
        return self.callback.new(level=level, id=selected_id, action=action)
