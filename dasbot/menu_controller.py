import logging

from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData

from .interface import Interface

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MenuController(object):
    def __init__(self, bot, chats_repo):
        self.bot = bot
        self.chats_repo = chats_repo
        self.ui = Interface(bot)
        self.callback = CallbackData('menu', 'level', 'menu_id', 'selection')  # menu:<level>:<id>:<action>

    # respond to /settings
    async def main(self, message: Message):
        await self.ui.settings_main(message, self.callback_generator)

    async def navigate(self, query):
        # TODO: Better error handling in case of bad data
        callback_data = self.callback.parse(query['data'])
        current_level = int(callback_data.get('level'))
        menu_id = callback_data.get('menu_id')
        selection = callback_data.get('selection')
        log.debug(f'current level: {current_level}, parent menu: {menu_id}, selection: {selection}')

        settings_actions = {
            1: {'main': self.ui.settings_menu},
            2: {'quiz-time': None,  # self.set_quiz_time,
                'quiz-len': None}  # self.set_quiz_length       }
        }
        action = settings_actions[current_level][menu_id]
        await action(query, self.callback_generator, current_level, selection)

    async def display_submenu(self, query, level, menu_id):
        self.ui.settings_submenu(query, self.callback_generator, level, menu_id)

    def callback_generator(self, level, menu_id, selection):
        return self.callback.new(level=level, menu_id=menu_id, selection=selection)
