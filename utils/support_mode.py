from telebot import TeleBot
from telebot.formatting import escape_markdown
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from utils.mesage_template import ENABLE_SUPPORT, SEND_SUPPORT
from utils.database_utils import *

support_chat = -4578482154
month_genitive = {
    'январь': 'января',
    'февраль': 'февраля',
    'март': 'марта',
    'апрель': 'апреля',
    'май': 'мая',
    'июнь': 'июня',
    'июль': 'июля',
    'август': 'августа',
    'сентябрь': 'сентября',
    'октябрь': 'октября',
    'ноябрь': 'ноября',
    'декабрь': 'декабря',
}


def send_init_support_mode(user_id: int, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Отключить", callback_data="sm:off"))

    bot.send_message(user_id, ENABLE_SUPPORT, parse_mode="MarkdownV2", reply_markup=keyboard)


def send_message_support_mode(message: Message, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Отключить", callback_data="sm:off"))

    bot.reply_to(message, SEND_SUPPORT, parse_mode="MarkdownV2", reply_markup=keyboard)


def send_info_message_into_admin_chat(message: Message, bot: TeleBot) -> None:
    user = get_user_info_by_telegram_id(message.chat.id)
    if user:
        support_log = get_support_log_by_telegram_id(user.telegram_id)
        user_name = escape_markdown(
            str(user.name) + ' ' + support_log.emoji if user.name is not None else 'Неизвестный 👤')
        user_telegram = escape_markdown(
            str(user.telegram_username) if user.telegram_username is not None else 'unknown')
        user_telegram_id = escape_markdown(str(user.telegram_id))
        user_ea_id = escape_markdown(str(user.ea_id) if user.ea_id is not None else 'null')
        msg = f'''📨 Новое сообщение\\!

👤 Пользователь: {user_name} \\(@{user_telegram}, id: `{user_telegram_id}`\\)
🔢 EA ID: `{user_ea_id}`

🔽 Сообщение 🔽
'''
        bot.send_message(support_chat, msg, parse_mode="MarkdownV2")

        bot.forward_message(support_chat, message.chat.id, message.message_id)


def add_message_to_support_log(message: Message, tg_id: int = None) -> bool:
    if message.chat.type == 'private':
        if not check_user_exist(message.chat.id):
            return False
        create_empty_support_log_if_not_exist(get_id_by_telegram_id(message.chat.id))
    user_name = message.from_user.username if message.from_user.username is not None else 'unknown'
    add_text_to_support_log(get_id_by_telegram_id(message.chat.id) if not tg_id else tg_id,
                            '[@' + user_name + ']: ' + str(message.text))
    return True


def get_support_log_text(telegram_id: int) -> str:
    support_log = get_support_log(get_id_by_telegram_id(telegram_id))
    user = get_user_id_by_id(support_log.user_id)
    return f'📨 Сообщение от пользователя {user.name} (@{user.telegram_username}):\n\n' + support_log.message
