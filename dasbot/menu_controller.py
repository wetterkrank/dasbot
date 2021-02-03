import logging

import re
from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData

log = logging.getLogger(__name__)


class MenuController(object):
    def __init__(self, ui, chats_repo):
        self.chats_repo = chats_repo
        self.ui = ui
        self.callback = CallbackData('menu', 'level', 'menu_id', 'selection')  # menu:<level>:<id>:<action>

    def callback_generator(self, level, menu_id, selection):
        return self.callback.new(level=level, menu_id=menu_id, selection=selection)

    # respond to /settings
    async def main(self, message: Message):
        await self.ui.settings_main(message, self.callback_generator)

    # respond to inline keyboard callbacks
    async def navigate(self, query):
        # TODO: Better error handling in case of bad data
        callback_data = self.callback.parse(query['data'])
        current_level = int(callback_data.get('level'))
        menu_id = callback_data.get('menu_id')
        selection = callback_data.get('selection')
        settings_actions = {
            1: {'main': self.ui.settings_menu},
            2: {'quiz-time': self.set_quiz_time,
                'quiz-len': self.set_quiz_length}
        }
        action = settings_actions[current_level][menu_id]
        await action(query, self.callback_generator, current_level, selection)

    # TODO: Refactor into a generic function?
    async def set_quiz_time(self, query, callback_gen, level, selection):
        await query.answer()  # To confirm reception
        chat = self.chats_repo.load_chat(query.message.chat.id)
        if selection == 'UNSUBSCRIBE':
            chat.unsubscribe()
        else:
            selection = re.search(r'^\d{4}$', selection).string or '1200'
            selection = f"{selection[:2]}:{selection[2:]}"
            chat.set_quiz_time(selection)
        chat.stamp_time()
        self.chats_repo.save_chat(chat)
        await self.ui.settings_confirm(query, self.ui.quiz_time_set(selection))

    async def set_quiz_length(self, query, callback_gen, level, selection):
        await query.answer()  # To confirm reception
        chat = self.chats_repo.load_chat(query.message.chat.id)
        selection = re.search(r'^(\d)$|^(\d{2})$', selection).string or '10'
        selection = int(selection)
        chat.quiz_length = selection  # NOTE: We could do the validation in the model
        chat.stamp_time()
        self.chats_repo.save_chat(chat)
        await self.ui.settings_confirm(query, self.ui.quiz_length_set(selection))
