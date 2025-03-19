import logging

from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from dasbot.db.chats_repo import ChatsRepo
from dasbot.models.quiz import QuizMode
from dasbot.i18n import t


log = logging.getLogger(__name__)


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_id: str
    selection: str


class MenuController(object):
    def __init__(self, chats_repo):
        self.chats_repo: ChatsRepo = chats_repo
        # NOTE: Can't use colon in callback actions, it's used as a separator
        self.TIME_OPTIONS = [
            "0900",
            "1200",
            "1500",
            "1800",
            "2100",
            "0000",
            "0300",
            "0600",
        ]
        self.LENGTH_OPTIONS = ["5", "10", "20", "50"]
        self.MODE_OPTIONS = [mode.value for mode in list(QuizMode)]
        self.QUIZ_OFF = "off"
        self.SETTINGS = {
            0: {
                "main": {
                    "row_len": 1,
                    "buttons": [
                        {
                            "action": "quiz_length",
                        },
                        {
                            "action": "quiz_mode",
                        },
                        {
                            "action": "quiz_time",
                        },
                    ],
                }
            },
            1: {
                "quiz_length": {
                    "row_len": 4,
                    "buttons": [{"text": n, "action": n} for n in self.LENGTH_OPTIONS],
                },
                "quiz_time": {
                    "row_len": 4,
                    "buttons": [
                        *(
                            {"text": f"{t[:2]}:{t[2:]}", "action": t}
                            for t in self.TIME_OPTIONS
                        ),
                        {"action": self.QUIZ_OFF},
                    ],
                },
                "quiz_mode": {
                    "row_len": 1,
                    "buttons": [
                        {
                            "action": QuizMode.Advance.value,
                        },
                        {
                            "action": QuizMode.Review.value,
                        },
                    ],
                },
            },
        }
        self.ACTIONS = {
            1: {"main": self.settings_menu},
            2: {
                "quiz_time": self.set_quiz_time,
                "quiz_length": self.set_quiz_length,
                "quiz_mode": self.set_quiz_mode,
            },
        }

    # respond to /settings message
    async def main(self, message: Message):
        text = self.settings_text("0.main.hint")
        keyboard = self.settings_kb(0, "main")
        await message.answer(text=text, reply_markup=keyboard)

    # respond to callback queries
    async def navigate(self, query: CallbackQuery, data: MenuCallback):
        action = self.ACTIONS[data.level][data.menu_id]
        await action(query, data.level, data.selection)

    async def settings_menu(self, query, level, menu_id):
        text = self.settings_text(f"{level}.{menu_id}.hint")
        keyboard = self.settings_kb(level, menu_id)
        await query.message.edit_text(text=text, reply_markup=keyboard)

    def settings_kb(self, level, menu_id):
        menu = self.SETTINGS[level][menu_id]
        row_width = menu["row_len"]
        buttons = menu["buttons"]
        builder = InlineKeyboardBuilder()
        for button in buttons:
            # menu:<level>:<menu_id>:<action>
            callback = MenuCallback(
                level=level + 1, menu_id=menu_id, selection=button["action"]
            ).pack()
            text = button.get(
                "text",
                self.settings_text(f"{level}.{menu_id}.buttons.{button['action']}"),
            )
            builder.button(text=text, callback_data=callback)
        builder.adjust(row_width)
        return builder.as_markup()

    def settings_text(self, key):
        return t(f"settings.menu.{key}")

    # Actions-related methods below
    async def set_quiz_time(self, query, _level, selection):
        chat = self.chats_repo.load_chat(query.message)
        if selection == self.QUIZ_OFF:
            chat.unsubscribe()
            log.info("Settings: chat %s unsubscribed", chat.id)
        else:
            if not (selection in self.TIME_OPTIONS):
                selection = "1200"
            selection = f"{selection[:2]}:{selection[2:]}"
            chat.set_quiz_time(selection)
            chat.subscribe()
            log.info("Settings: chat %s changed quiz time to %s", chat.id, selection)
        self.chats_repo.save_chat(chat, update_last_seen=True)
        if selection == self.QUIZ_OFF:
            await self.action_confirm(query, "quiz_off")
        else:
            await self.action_confirm(query, "quiz_time_set", pref=selection)

    async def set_quiz_length(self, query, _level, selection):
        chat = self.chats_repo.load_chat(query.message)
        new_length = int(selection) if selection in self.LENGTH_OPTIONS else 10
        chat.quiz_length = new_length
        self.chats_repo.save_chat(chat, update_last_seen=True)
        await self.action_confirm(query, "quiz_length_set", pref=new_length)

    async def set_quiz_mode(self, query, _level, selection):
        chat = self.chats_repo.load_chat(query.message)
        if not (selection in self.MODE_OPTIONS):
            selection = self.MODE_OPTIONS[0]
        chat.quiz_mode = QuizMode(selection)
        self.chats_repo.save_chat(chat, update_last_seen=True)
        await self.action_confirm(
            query,
            f"quiz_mode_{selection}",
        )

    # NOTE: Telegram Web has a bug with inline kb not disappearing?
    # Possible workaround: delete the message with the kb and send a new one
    async def action_confirm(self, query, key, **kwargs):
        await query.message.edit_text(text=t(f"settings.action.{key}", **kwargs))
