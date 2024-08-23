import locale
import re
from datetime import datetime

from telebot.formatting import escape_markdown
from telebot.types import Message

from utils.mesage_template import DISABLE_SUPPORT, FAIL_SUPPORT_NOT_REGISTER, ADMINS_ANSWER_PREFIX
from utils.register_steps import TeleBot, add_user_if_not_exist, ask_missing_information, confirm_callback_edit, \
    EMPTY_INVITE, get_user_id_by_invoice, set_telegram_id_by_telegram_id, ENABLE_SUPPORT
from utils.redis import *
from utils.support_mode import send_init_support_mode, send_message_support_mode, send_info_message_into_admin_chat, \
    add_message_to_support_log, support_chat, get_support_log_text, month_genitive, send_users_status

TEST = False
TOKEN = '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes' if TEST else '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'
# '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'  тест
# '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'  прод
bot = TeleBot(TOKEN)

common_users_ids = [
    support_chat,
    780828132
]


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


# print('--- --- ---')
# print(message.reply_to_message.text)
# print(message.reply_to_message.from_user)
# print(message)
# print('--- --- ---')


if __name__ == '__main__':
    bot.infinity_polling()
