from utils.register_steps import *

TOKEN = '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'
TELEGRAM_CHAT_ID = 780828132
bot = TeleBot(TOKEN)

clear_registrated(TELEGRAM_CHAT_ID)


@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        invoice = args[1].strip()

    else:
        is_user_exist = add_user_if_not_exist(message.chat.id)

        if not is_user_exist:
            bot.send_message(message.chat.id, EMPTY_INVITE, parse_mode="MarkdownV2")

        ask_missing_information(message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm:edit:"))
def confirm_callback_edit_wrapper(call):
    confirm_callback_edit(call, bot)


if __name__ == '__main__':
    bot.infinity_polling()
