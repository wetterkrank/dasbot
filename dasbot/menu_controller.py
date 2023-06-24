import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from dasbot.db.chats_repo import ChatsRepo

log = logging.getLogger(__name__)


class MenuController(object):
    def __init__(self, ui, chats_repo):
        self.chats_repo: ChatsRepo = chats_repo
        self.ui = ui
        # NOTE: Can't use colon in callback actions, it's used as a separator
        self.TIME_OPTIONS = ['0900', '1200', '1500', '1800', '2100', '0000', '0300', '0600']
        self.LENGTH_OPTIONS = ['5', '10', '20', '50']
        self.SETTINGS = {
            0: {
                'main': {'hint': self.ui.settings_text['main-hint'], 'row_len': 2, 'btns': [
                    {'text': self.ui.settings_text['main-btn1'], 'action': 'quiz-len'},
                    {'text': self.ui.settings_text['main-btn2'], 'action': 'quiz-time'}
                ]}
            },
            1: {
                'quiz-len': {'hint': self.ui.settings_text['quiz-len-hint'], 'row_len': 4, 'btns': [
                    {'text': n, 'action': n} for n in self.LENGTH_OPTIONS
                ]},
                'quiz-time': {'hint': self.ui.settings_text['quiz-time-hint'], 'row_len': 4, 'btns': [
                    {'text': f"{t[:2]}:{t[2:]}", 'action': t} for t in self.TIME_OPTIONS
                ] + [{'text': self.ui.settings_text['quiz-time-btn'], 'action': 'UNSUBSCRIBE'}]}
            }
        }
        self.callback = CallbackData('menu', 'level', 'menu_id', 'selection')  # menu:<level>:<id>:<action>

    def callback_generator(self, level, menu_id, selection):
        return self.callback.new(level=level, menu_id=menu_id, selection=selection)

    # respond to /settings
    async def main(self, message: Message):
        text = self.SETTINGS[0]['main']['hint']
        keyboard = self.settings_kb(0, 'main')
        await message.answer(text=text, reply_markup=keyboard)

    # respond to callback queries
    async def navigate(self, query: CallbackQuery):
        cb_data = self.callback.parse(query['data'])
        current_level = int(cb_data['level'])
        menu_id = cb_data['menu_id']
        selection = cb_data['selection']
        ACTIONS = {
            1: {'main': self.settings_menu},
            2: {'quiz-time': self.set_quiz_time,
                'quiz-len': self.set_quiz_length}
        }
        action = ACTIONS[current_level][menu_id]
        await action(query, current_level, selection)

    async def settings_menu(self, query, level, menu_id):
        text = self.SETTINGS[level][menu_id]['hint']
        keyboard = self.settings_kb(level, menu_id)
        await query.message.edit_text(text=text, reply_markup=keyboard)

    async def settings_confirm(self, query, text):
        await query.message.edit_text(text=text)

    def settings_kb(self, level, menu_id):
        menu = self.SETTINGS[level][menu_id]
        row_width = menu['row_len']
        buttons = menu['btns']
        markup = InlineKeyboardMarkup(row_width=row_width)
        for i, button in enumerate(buttons):
            callback = self.callback_generator(level=level + 1, menu_id=menu_id, selection=button['action'])
            if i % row_width == 0:
                markup.row()
            markup.insert(InlineKeyboardButton(text=button['text'], callback_data=callback))
        return markup

    # TODO: Refactor into a generic function?
    async def set_quiz_time(self, query, _level, selection):
        chat = self.chats_repo.load_chat(query.message)
        if selection == 'UNSUBSCRIBE':
            chat.unsubscribe()
            log.debug('Chat %s unsubscribed', chat.id)
        else:
            if not (selection in self.TIME_OPTIONS):
                selection = '1200'
            selection = f"{selection[:2]}:{selection[2:]}"
            chat.set_quiz_time(selection)
            chat.subscribe()
            log.debug('Chat %s changed quiz time to %s', chat.id, selection)
        self.chats_repo.save_chat(chat, update_last_seen=True)
        await self.settings_confirm(query, self.ui.quiz_time_set(selection))

    async def set_quiz_length(self, query, _level, selection):
        chat = self.chats_repo.load_chat(query.message)
        new_length = int(selection) if selection in self.LENGTH_OPTIONS else 10
        chat.quiz_length = new_length
        self.chats_repo.save_chat(chat, update_last_seen=True)
        await self.settings_confirm(query, self.ui.quiz_length_set(new_length))
