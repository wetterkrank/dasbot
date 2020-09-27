#TODO: add hint button; if /start is sent several times -- don't send many questions

import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import random
from dictionary import Dictionary
from database import Database
import config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize bot, dispatcher, and session states
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
dictionary = Dictionary(config.DICT_FILE)
db = Database(config.DB_ADDRESS, config.DB_NAME)


# /help handler
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply('Type /start to start the quiz.')

# /start handler
@dp.message_handler(commands=['start'])
async def process_word_command(message: types.Message):
    logger.debug('/start received: %s', message)

    chat_id = message.chat.id

    # Get the first question
    quiz_entry = next_question()

    # Ask it
    msg_text = f"1/{config.QUIZ_LEN}. What's the article for {quiz_entry['question']}?"
    await bot.send_message(chat_id, msg_text, reply_markup=keyboard())

    # Set initial chat state
    db.save_chat(chat_id, {'quiz_pos': 2, 'question': quiz_entry['question'], 'answer': quiz_entry['answer']})

# generic handler -- deals with incoming answers
@dp.message_handler()
async def any_msg_handler(message: types.Message):
    logger.debug('generic message received: %s', message)

    chat_id = message.chat.id
    chat_state = db.get_chat(chat_id)
    logger.debug('quiz state retrieved: %s', chat_state)

    answer_data = message.text.strip().lower()

    # If the quiz is active and we recognize the input, check the answer
    if (answer_data in ['der', 'die', 'das']) and chat_state:
        # Tell results
        possible_answers = chat_state['answer'].split(",")
        if answer_data in possible_answers:
            result_message = f"Correct: {chat_state['answer']} {chat_state['question']}"
        else:
            result_message = f"Incorrect: {chat_state['answer']} {chat_state['question']}"
        await bot.send_message(chat_id, result_message)
        # If the quiz is active and we still have questions to ask
        if chat_state:
            if chat_state['quiz_pos'] <= config.QUIZ_LEN:
                # Ask next question
                quiz_entry = next_question()
                msg_text = f"{chat_state['quiz_pos']}/{config.QUIZ_LEN}. What's the article for {quiz_entry['question']}?"
                await bot.send_message(chat_id, msg_text, reply_markup=keyboard())
                # Save chat state
                db.save_chat(chat_id, {'quiz_pos': chat_state['quiz_pos'] + 1, 'question': quiz_entry['question'], 'answer': quiz_entry['answer']})
            else:
                # The quiz has ended, remove keyboard
                msg_text = 'Thank you! To start over, type /start, or /help for more info.'
                await message.answer(msg_text, reply_markup=types.ReplyKeyboardRemove())
    else:
        # If the message is something unexpected or we don't have the active quiz
        msg_text = "I didn't get it. Type /start to start over, /help for more info."
        await message.answer(msg_text)


def next_question():
    word = random.choice(dictionary.allwords)
    articles = dictionary.articles(word)
    return {'question': word, 'answer': articles}

def keyboard():
    ''' Returns object of ReplyKeyboardMarkup type '''
    labels = ('der', 'die', 'das')
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row_btns = (types.KeyboardButton(text) for text in labels)
    keyboard_markup.row(*row_btns)
    return keyboard_markup


if __name__ == '__main__':
    executor.start_polling(dp)
