import pymysql

from utils.register_steps import TeleBot, add_user_if_not_exist, ask_missing_information, confirm_callback_edit, \
    EMPTY_INVITE, get_user_id_by_invoice, set_telegram_id_by_user_id, set_policy

TOKEN = '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        invoice = args[1].strip()

        user_id = get_user_id_by_invoice(invoice)
        if user_id is not None:
            try:
                set_telegram_id_by_user_id(user_id, message.chat.id)
                # set_policy(message.chat.id)
            except EMPTY_INVITE:
                bot.send_message(message.chat.id, "Вы уже зарегистрированы", parse_mode="MarkdownV2")
            ask_missing_information(message, bot)
            return

    is_user_exist = add_user_if_not_exist(message.chat.id)
    if not is_user_exist:
        bot.send_message(message.chat.id, EMPTY_INVITE, parse_mode="MarkdownV2")

    ask_missing_information(message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm:edit:"))
def confirm_callback_edit_wrapper(call):
    confirm_callback_edit(call, bot)


if __name__ == '__main__':
    bot.infinity_polling()
