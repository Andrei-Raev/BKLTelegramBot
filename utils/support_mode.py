from telebot import TeleBot
from telebot.formatting import escape_markdown
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from utils.mesage_template import ENABLE_SUPPORT, SEND_SUPPORT
from utils.database_utils import *

support_chat = -4578482154
month_genitive = {
    'january': 'января',
    'february': 'февраля',
    'march': 'марта',
    'april': 'апреля',
    'may': 'мая',
    'june': 'июня',
    'july': 'июля',
    'august': 'августа',
    'september': 'сентября',
    'october': 'октября',
    'november': 'ноября',
    'december': 'декабря',
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
    add_text_to_support_log(get_id_by_telegram_id(message.chat.id) if not tg_id else get_id_by_telegram_id(tg_id),
                            '[@' + user_name + ']: ' + str(message.text))
    return True


def get_support_log_text(telegram_id: int) -> str:
    support_log = get_support_log(get_id_by_telegram_id(telegram_id))
    user = get_user_id_by_id(support_log.user_id)
    return f'📨 Сообщение от пользователя {user.name} (@{user.telegram_username}):\n\n' + support_log.message


def send_users_status(chat_id: int, bot: TeleBot) -> None:
    users = get_all_users()
    msg = '👥 Статистика пользователей \\(всего: *' + str(len(users)) + '*\\)\n\n' + '*Список:*\n'
    for user in users[:50]:
        msg += '    \\- ' + escape_markdown(str(user.name)) + ' \\(@' + escape_markdown(
            str(user.telegram_username)) + ' ea\\_id: `' + escape_markdown(str(user.ea_id)) + '`\\)\n'

    if len(users) > 50:
        msg += '    \\- и еще ' + str(len(users) - 50) + ' пользователей'

    bot.send_message(chat_id, msg, parse_mode="MarkdownV2")


def broadcast(bot: TeleBot, message: Message) -> None:
    users = get_all_users()
    bot.send_message(support_chat,
                     f'Введите сообщение, которое будет отправлено всем пользователям: {len(users)}\nДля отмены впишите "Отмена"')

    bot.register_next_step_handler_by_chat_id(message.chat.id, broadcast_send, bot, message.from_user.id)


def broadcast_send(message: Message, bot: TeleBot, user_id: int) -> None:
    if message.from_user.id != user_id:
        bot.send_message(message.chat.id, "Вы не можете это сделать", parse_mode="MarkdownV2")
        bot.register_next_step_handler_by_chat_id(message.chat.id, broadcast_send, bot, user_id)
        return

    if message.text is None:
        bot.send_message(message.chat.id, "Вы ввели не текст", parse_mode="MarkdownV2")
        return

    message_text = bot.send_message(support_chat, 'Отправка...')
    users = get_all_users()
    cc = 0
    for user in users:
        bot.edit_message_text(f'Отправка: {cc}/{len(users)} ({round(cc / len(users) * 100, 2)}%))',
                              message_text.chat.id, message_text.message_id)
        try:
            bot.send_message(user.telegram_id, message.text)
        except Exception as e:
            bot.send_message(support_chat, f'При отправке сообщения возникла ошибка: {e}')
        cc += 1

    bot.edit_message_text('Отправка завершена', message_text.chat.id, message_text.message_id)
