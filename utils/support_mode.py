from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from utils.mesage_template import ENABLE_SUPPORT, SEND_SUPPORT

support_chat = 780828132


def send_init_support_mode(user_id: int, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Отключить", callback_data="sm:off"))

    bot.send_message(user_id, ENABLE_SUPPORT, parse_mode="MarkdownV2", reply_markup=keyboard)


def send_message_support_mode(message: Message, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Отключить", callback_data="sm:off"))

    bot.reply_to(message, SEND_SUPPORT, parse_mode="MarkdownV2", reply_markup=keyboard)

    bot.forward_message(support_chat, message.chat.id, message.message_id)
