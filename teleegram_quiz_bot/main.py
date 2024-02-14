import os
import telebot
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from mesages import start_message, help_message
from quiz_data import question_list, option_list

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(TOKEN)

user_states = {}
user_scores = {}


@bot.message_handler(commands=["start"])
def start_command_handler(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=start_message
    )


@bot.message_handler(commands=["help"])
def help_command_handler(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=help_message
    )


@bot.message_handler(commands=["start_quiz"])
def start_quiz_command_handler(message: Message):
    user_states[message.chat.id] = 0
    user_scores[message.chat.id] = {'correct': 0,
                                    'incorrect': 0}

    question_data = question_list[user_states[message.chat.id]]
    q_text = f"{user_states[message.chat.id] + 1}. {question_data['question']}"
    markup = InlineKeyboardMarkup(row_width=2)
    btns = []

    for i, option in enumerate(question_data['options']):
        btn = InlineKeyboardButton(text=option, callback_data=option_list[i])
        btns.append(btn)

    markup.add(*btns)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Викторина начинается!"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=q_text,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in option_list)
def callback_handler(call: CallbackQuery):
    question_number = user_states.get(call.message.chat.id)

    if question_number is None:
        return

    question_data = question_list[question_number]

    if question_data['correct_option'] == call.data:
        bot.answer_callback_query(callback_query_id=call.id, text="Правильно!")
        user_scores[call.message.chat.id]['correct'] += 1
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Не правильно!")
        user_scores[call.message.chat.id]['incorrect'] += 1

    user_states[call.message.chat.id] += 1

    if user_states[call.message.chat.id] >= len(question_list):
        correct_count = user_scores[call.message.chat.id]['correct']
        incorrect_count = user_scores[call.message.chat.id]['incorrect']

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Конец. Правильных ответов: {correct_count}, Неправильных ответов: {incorrect_count}",
        )

        del user_states[call.message.chat.id]
        del user_scores[call.message.chat.id]

        return

    question_data = question_list[user_states[call.message.chat.id]]
    q_text = f"{user_states[call.message.chat.id] + 1}. {question_data['question']}"
    markup = InlineKeyboardMarkup(row_width=2)
    btns = []

    for i, option in enumerate(question_data['options']):
        btn = InlineKeyboardButton(text=option, callback_data=option_list[i])
        btns.append(btn)

    markup.add(*btns)

    bot.send_message(
        chat_id=call.message.chat.id,
        text=q_text,
        reply_markup=markup
    )


bot.polling()
