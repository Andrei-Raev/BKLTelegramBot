import locale
import re
from datetime import datetime

from telebot.formatting import escape_markdown
from telebot.types import Message, BotCommand, BotCommandScopeChat

from utils.database_utils import end_match_early, send_val_info, validate_chat_mm
from utils.mesage_template import DISABLE_SUPPORT, FAIL_SUPPORT_NOT_REGISTER, ADMINS_ANSWER_PREFIX
from utils.register_steps import TeleBot, add_user_if_not_exist, ask_missing_information, confirm_callback_edit, \
    EMPTY_INVITE, get_user_id_by_invoice, set_telegram_id_by_telegram_id, ENABLE_SUPPORT
from utils.redis import *
from utils.support_mode import send_init_support_mode, send_message_support_mode, send_info_message_into_admin_chat, \
    add_message_to_support_log, support_chat, get_support_log_text, month_genitive, send_users_status, broadcast, \
    ask_message, send_init_validate_mode, send_win_msg

TEST = False
TOKEN = '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes' if TEST else '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'
# '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'  тест
# '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'  прод
bot = TeleBot(TOKEN)

common_users_ids = [
    support_chat,
    780828132
]

validate_chat = -1002223147233


@bot.message_handler(commands=['start'])
def start(message):
    clear_support_mode(message.chat.id)

    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        invoice = args[1].strip()

        user_id = get_user_id_by_invoice(invoice)
        if user_id is not None:
            set_telegram_id_by_telegram_id(user_id, message.chat.id)

            ask_missing_information(message, bot)
            return

    is_user_exist = add_user_if_not_exist(message.chat.id)
    if not is_user_exist:
        bot.send_message(message.chat.id, EMPTY_INVITE, parse_mode="MarkdownV2")

    ask_missing_information(message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm:edit:"))
def confirm_callback_edit_wrapper(call):
    confirm_callback_edit(call, bot)


@bot.message_handler(commands=['support'])
def support(message):
    user_id = message.chat.id
    set_support_mode(user_id)
    clear_validate_mode(user_id)

    send_init_support_mode(user_id, bot)


@bot.callback_query_handler(func=lambda call: call.data == "sm:off")
def disable_support_mode(call):
    user_id = call.message.chat.id
    clear_support_mode(user_id)

    bot.edit_message_text(DISABLE_SUPPORT, call.message.chat.id, call.message.message_id, parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: get_support_mode(message.chat.id),
                     content_types=['*', 'sticker', 'photo', 'audio', 'video', 'video_note', 'voice', 'location',
                                    'contact', 'text'])
def pass_to_support(message):
    res = add_message_to_support_log(message)
    if not res:
        bot.send_message(message.chat.id, FAIL_SUPPORT_NOT_REGISTER, parse_mode="MarkdownV2")
        return
    send_info_message_into_admin_chat(message, bot)
    send_message_support_mode(message, bot)


@bot.message_handler(func=lambda message: message.chat.id in common_users_ids, commands=['status'])
def support_status(message):
    send_users_status(message.chat.id, bot)


@bot.message_handler(func=lambda message: message.chat.id == support_chat, commands=['log'])
def support_log(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            tg_id = int(args[1].strip())
        except ValueError:
            bot.send_message(support_chat, "Неверный формат ID пользователя\\!", parse_mode="MarkdownV2")
            return

        bot.send_message(support_chat, get_support_log_text(tg_id))
    else:
        bot.send_message(support_chat, "Введите команду в виде:\n`/log user_tg_id`", parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.chat.id == support_chat)
def support_reply(message: Message):
    if message.content_type == 'text':
        tg_id = (lambda m: m.group(1) if m else None)(re.search(r"id: (\d+)\)", message.reply_to_message.text))
        if tg_id:
            tg_id = int(tg_id)

            try:
                bot.send_message(tg_id, ADMINS_ANSWER_PREFIX + escape_markdown(message.text), parse_mode="MarkdownV2")
                # print(datetime.now().strftime("%H:%M:%S %d %B"))
                bot.edit_message_text(
                    message.reply_to_message.text + f'\n\n --- ✅ Отвечено (@{message.from_user.username}:'
                                                    f' {datetime.now().strftime("%H:%M:%S, %d ") +
                                                        month_genitive[datetime.now().strftime("%B").lower()]})! ---',
                    message.chat.id, message.reply_to_message.message_id)

                add_message_to_support_log(message, tg_id)

                bot.send_message(message.chat.id, "Доставлено ✅", parse_mode="MarkdownV2")
            except Exception as e:
                bot.send_message(message.chat.id,
                                 "*Не удалось отправить ответ\\!*\n\nПричина:\n```\n" +
                                 escape_markdown(str(e)) + "\n```",
                                 parse_mode="MarkdownV2")

        else:
            bot.send_message(message.chat.id,
                             "Отвечайте на сообщение бота *\\(не пересланное или какое либо иное\\)*\\!",
                             parse_mode="MarkdownV2")

    else:
        bot.send_message(message.chat.id, "*Ответом может быть только текстовое сообщение\\!*",
                         parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.chat.id == support_chat, commands=['broadcast'])
def support_broadcast(message):
    broadcast(bot, message)


@bot.message_handler(func=lambda message: message.chat.id in [validate_chat, support_chat], commands=['msg'])
def support_msg(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            tg_id = int(args[1].strip())
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат ID пользователя\\!", parse_mode="MarkdownV2")
            return
        bot.send_message(message.chat.id,
                         'Любое следующее сообщение, являющиеся ответом на команду /msg будет отправлено')
        bot.register_next_step_handler_by_chat_id(message.chat.id, ask_message, bot, tg_id)
    else:
        bot.send_message(message.chat.id, "Введите команду в виде:\n`/msg user_tg_id`", parse_mode="MarkdownV2")


@bot.message_handler(commands=['get_id'])
def get_id(message):
    bot.send_message(message.chat.id,
                     f'id текущего чата: `{message.chat.id}`\nid текущего юзера: `{message.from_user.id}`',
                     parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.chat.id == validate_chat, commands=['end_match'])
def end_match(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            ea_id = args[1].strip()
        except ValueError:
            bot.send_message(message.chat.id, "Вы не ввели EA ID победителя\\!", parse_mode="MarkdownV2")
            return

        end_match_early(bot, ea_id, message.chat.id)
        send_win_msg(bot, ea_id)
    else:
        bot.send_message(message.chat.id, "Вы не ввели EA ID победителя\\!", parse_mode="MarkdownV2")
        return


@bot.message_handler(commands=['validate'])
def validate(message):
    user_id = message.chat.id
    set_validate_mode(user_id)
    clear_support_mode(user_id)

    send_init_validate_mode(user_id, bot)


@bot.message_handler(func=lambda message: message.chat.id == validate_chat and bool(
    re.match(r"^\s*1\s*:\s*\d+\s*2\s*:\s*\d+\s*$", message.text)))
def validate_vl(message: Message):
    match_number = re.search(r"Матч (\d+):", message.reply_to_message.text).group(1)
    match = re.search(r"1\s*:\s*(\d+)\s*2\s*:\s*(\d+)", message.text)
    if match:
        number1 = int(match.group(1))
        number2 = int(match.group(2))

        bot.edit_message_text(message.reply_to_message.text + '\n\n✅', message.chat.id,
                              message.reply_to_message.message_id)

        validate_chat_mm(match_number, number1, number2, bot, message.chat.id)


@bot.message_handler(func=lambda message: get_validate_mode(message.chat.id), content_types=['photo'])
def pass_to_validate(message):
    clear_validate_mode(message.chat.id)

    send_val_info(bot, message.chat.id, validate_chat)
    bot.forward_message(validate_chat, message.chat.id, message.message_id)


# send_val_info(bot, 810526171, validate_chat)
# print('--- --- ---')
# print(message.reply_to_message.text)
# print(message.reply_to_message.from_user)
# print(message)
# print('--- --- ---')


if __name__ == '__main__':
    commands = [
        BotCommand("start", "🔄 Запустить бота"),
        BotCommand("support", "💬 Включить режим поддержки"),
        BotCommand("validate", "🏁 Включить режим валидации")
    ]
    bot.set_my_commands(commands)

    support_chat_commands = [
        BotCommand("status", "👥 Статистика"),
        BotCommand("log", "📝 Журнал (после log добавь id пользователя)"),
        BotCommand("broadcast", "📨 Рассылка"),
        BotCommand("msg", "💬 Отправить сообщение (tg id)")
    ]
    bot.set_my_commands(support_chat_commands, scope=BotCommandScopeChat(chat_id=support_chat))

    validate_chat_commands = [
        BotCommand("end_match", "🏁 Завершить матч досрочно (надо ввести ea id победителя)"),
        BotCommand("msg", "💬 Отправить сообщение (tg id)")
    ]
    bot.set_my_commands(validate_chat_commands, scope=BotCommandScopeChat(chat_id=validate_chat))

    bot.infinity_polling()
