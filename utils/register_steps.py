import os
import re, requests

from telebot.types import Message, ReactionTypeEmoji, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telebot import TeleBot

from utils.mesage_template import *
from utils.database_utils import *
from utils.redis import *


def ask_missing_information(message: Message, bot: TeleBot) -> bool:
    user_id = message.chat.id
    if is_registrated(user_id):
        bot.send_message(message.chat.id, SUCCESS_REGISTRATION, message_effect_id='5046509860389126442',
                         parse_mode="MarkdownV2")
        return True

    if not get_policy(user_id):
        ask_policy(message, bot)
        return False

    if not check_telegram_username(user_id):
        try:
            add_telegram_username(message.from_user.username, user_id)
        except Exception as e:
            print(e)
        ask_missing_information(message, bot)
        return False

    if not check_name(user_id):
        ask_info(message, bot, add_user_name, is_valid_name, format_and_clean_name, ENTER_NAME)
        return False

    if not check_platform(user_id):
        ask_info_with_callback(message, bot, 0, get_platforms(), ENTER_PLATFORM)
        return False

    if not check_ea_id(user_id):
        ask_info(message, bot, add_ea_id, is_valid_ea_id, format_and_clean_ea_id, ENTER_EA_ID)
        return False

    confirm_information(message, bot)
    return False


def ask_info(message: Message, bot: TeleBot, event_listener: callable, data_validator: callable,
             preprocess_data: callable, enter_info: str) -> None:
    bot.send_message(message.chat.id, enter_info, parse_mode="MarkdownV2")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_info, bot, event_listener,
                                              data_validator, preprocess_data)


def get_info(message: Message, bot: TeleBot, event_listener: callable, data_validator: callable,
             preprocess_data: callable) -> None:
    if message.text is None:
        bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👎")])
        bot.send_message(message.chat.id, INCORRECT_INPUT, parse_mode="MarkdownV2")
        bot.register_next_step_handler_by_chat_id(message.chat.id, get_info, bot, event_listener,
                                                  data_validator, preprocess_data)

        return
    name = preprocess_data(message.text)
    if (fail_message := data_validator(name)) is True:
        bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👍")])
        event_listener(data=name, user_id=message.chat.id)
        ask_missing_information(message, bot)
    else:
        bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👎")])
        bot.send_message(message.chat.id, fail_message, parse_mode="MarkdownV2")
        bot.register_next_step_handler_by_chat_id(message.chat.id, get_info, bot, event_listener,
                                                  data_validator, preprocess_data)


# --== {Принятие политики} ==--
def ask_policy(message: Message, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="✅ Согласен", callback_data="policy:accept"),
                 InlineKeyboardButton(text="❌ Не согласен", callback_data="policy:decline"))
    bot.send_message(message.chat.id, ASK_POLICY, reply_markup=keyboard, parse_mode="MarkdownV2")
    bot.register_callback_query_handler(policy_callback, lambda call: call.data.startswith(
        "policy:") and call.from_user.id == message.chat.id, pass_bot=True)


def policy_callback(call: CallbackQuery, bot: TeleBot) -> None:
    if call.data == "policy:accept":
        set_policy(call.from_user.id)
        bot.edit_message_text(ASK_POLICY + ACCEPT_POLICY, call.from_user.id, call.message.message_id,
                              parse_mode="MarkdownV2")
        ask_missing_information(call.message, bot)
    elif call.data == "policy:decline":
        bot.edit_message_text(ASK_POLICY + DENY_POLICY, call.from_user.id, call.message.message_id,
                              parse_mode="MarkdownV2")


# --== {ПОДТВЕРЖДЕНИЕ ИНФОРМАЦИИ} ==--
def render_confirm_information(user_id: int) -> str:
    user: UserORM = get_user_info(user_id)
    return USER_INFO.format(escape_markdown(user.telegram_username), escape_markdown(user.name),
                            escape_markdown(get_platform_by_id(user.platform).name), escape_markdown(user.ea_id))


def confirm_information(message: Message, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm:yes"),
                 InlineKeyboardButton(text="📝 Изменить", callback_data="confirm:edit"))
    bot.send_message(message.chat.id, render_confirm_information(user_id=message.chat.id), parse_mode="MarkdownV2",
                     reply_markup=keyboard)
    bot.register_callback_query_handler(confirm_callback, lambda call: call.data.startswith(
        "confirm:") and call.from_user.id == message.chat.id, pass_bot=True)


def confirm_callback_edit(call: CallbackQuery, bot: TeleBot) -> None:
    print(call.data)
    if call.data == "confirm:edit:back":
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm:yes"),
                     InlineKeyboardButton(text="📝 Изменить", callback_data="confirm:edit"))
        bot.edit_message_text(render_confirm_information(user_id=call.from_user.id), call.from_user.id,
                              call.message.message_id, parse_mode="MarkdownV2", reply_markup=keyboard)
        bot.register_callback_query_handler(confirm_callback, lambda call: call.data.startswith(
            "confirm:") and call.from_user.id == call.message.chat.id, pass_bot=True)
    elif call.data == "confirm:edit:name":
        bot.edit_message_text(render_confirm_information(user_id=call.from_user.id), call.from_user.id,
                              call.message.message_id, parse_mode="MarkdownV2")
        ask_info(call.message, bot, add_user_name, is_valid_name, format_and_clean_name, ENTER_NAME)
    elif call.data == "confirm:edit:platform":
        bot.edit_message_text(render_confirm_information(user_id=call.from_user.id), call.from_user.id,
                              call.message.message_id, parse_mode="MarkdownV2")
        ask_info_with_callback(call.message, bot, 0, get_platforms(), ENTER_PLATFORM)
    elif call.data == "confirm:edit:ea_id":
        bot.edit_message_text(render_confirm_information(user_id=call.from_user.id), call.from_user.id,
                              call.message.message_id, parse_mode="MarkdownV2")
        ask_info(call.message, bot, add_ea_id, is_valid_ea_id, format_and_clean_ea_id, ENTER_EA_ID)


def confirm_callback(call: CallbackQuery, bot: TeleBot) -> None:
    if call.data == "confirm:yes":
        bot.edit_message_text(render_confirm_information(user_id=call.message.chat.id) + CONFIRM_ACCEPT,
                              call.from_user.id, call.message.message_id, parse_mode="MarkdownV2")
        set_registrated(call.from_user.id)
        ask_missing_information(call.message, bot)
    elif call.data == "confirm:edit":
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text="Имя", callback_data="confirm:edit:name"),
                     InlineKeyboardButton(text="Платформа", callback_data="confirm:edit:platform"),
                     InlineKeyboardButton(text="EA ID", callback_data="confirm:edit:ea_id"))
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="confirm:edit:back"))
        bot.edit_message_text(render_confirm_information(user_id=call.message.chat.id), call.from_user.id,
                              call.message.message_id, reply_markup=keyboard, parse_mode="MarkdownV2")

    # inner_call.data.startswith("confirm:edit:") and inner_call.from_user.id == call.message.chat.id


# --== {КОНКРЕТНЫЕ ФУНКЦИИ} ==--
def is_valid_name(name):
    pattern = r"^[A-ZА-ЯЁ][a-zа-яё'-]{1,} [A-ZА-ЯЁa-zа-яё'-]{1,}$"
    if re.match(pattern, name) is not None:
        return True
    else:
        return INCORRECT_NAME


def format_and_clean_name(name):
    name = ' '.join(word.capitalize() for word in name.split())
    return name


def is_valid_ea_id(ea_id: str) -> bool:
    tmp_cookie = get_temp_ea_cookie()
    url = 'https://signin.ea.com/p/ajax/user/checkOriginId?originId={}'.format(ea_id)
    headers = {
        "Cookie": tmp_cookie,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        if not json_response['status'] and json_response['message'] == 'origin_id_duplicated':
            return True
        if json_response['status'] or json_response['message'] in ['origin_id_not_allowed', 'origin_id_too_long',
                                                                   'origin_id_too_short']:
            return EA_ID_IS_NOT_EXIST
    elif response.status_code == 403:
        set_temp_ea_cookie(response.headers['set-cookie'].replace('SameSite=None, ', ''))
        return is_valid_ea_id(ea_id)
    return True


def format_and_clean_ea_id(ea_id):
    return ea_id.strip()


# --== {CALLBACK ФУНКЦИИ} ==--

def ask_info_with_callback(message: Message, bot: TeleBot, event_listener_id: int,
                           callback_data: list[str], enter_info: str) -> None:
    keyboard = InlineKeyboardMarkup()
    for data in callback_data:
        keyboard.add(InlineKeyboardButton(text=data, callback_data=f'cb_ask:{event_listener_id}:' + data))

    bot.send_message(message.chat.id, enter_info, reply_markup=keyboard, parse_mode="MarkdownV2")
    bot.register_callback_query_handler(get_callback_info, lambda call: call.data.startswith(
        'cb_ask:') and call.from_user.id == message.chat.id, pass_bot=True)


def get_callback_info(call: CallbackQuery, bot: TeleBot) -> None:
    message = call.message
    event_listener_id, data = call.data.split(':', maxsplit=2)[1:]
    EVENT_LISTENERS_CALLBACK_LIST[int(event_listener_id)](data=data, user_id=message.chat.id)
    print(message.text + SELECTED_VALUE.format(data))
    bot.edit_message_text(text=message.text + SELECTED_VALUE.format(data), chat_id=message.chat.id,
                          message_id=message.message_id, parse_mode="MarkdownV2", reply_markup=None)

    ask_missing_information(message, bot)


EVENT_LISTENERS_CALLBACK_LIST = [add_platform]
