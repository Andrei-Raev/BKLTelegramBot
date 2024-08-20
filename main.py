from utils.mesage_template import DISABLE_SUPPORT
from utils.register_steps import TeleBot, add_user_if_not_exist, ask_missing_information, confirm_callback_edit, \
    EMPTY_INVITE, get_user_id_by_invoice, set_telegram_id_by_user_id, ENABLE_SUPPORT
from utils.redis import *
from utils.support_mode import send_init_support_mode, send_message_support_mode

TOKEN = '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'  # '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'  #
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    clear_support_mode(message.chat.id)

    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        invoice = args[1].strip()

        user_id = get_user_id_by_invoice(invoice)
        if user_id is not None:
            set_telegram_id_by_user_id(user_id, message.chat.id)

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


@bot.message_handler(func=lambda message: get_support_mode(message.chat.id))
def pass_to_support(message):
    send_message_support_mode(message, bot)


if __name__ == '__main__':
    bot.infinity_polling()
