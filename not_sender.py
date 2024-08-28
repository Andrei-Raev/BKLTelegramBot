from telebot import TeleBot
from telebot.formatting import escape_markdown

from utils.database import *

from utils.database import Session

TEST = False
TOKEN = '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes' if TEST else '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'
# '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'  тест
# '7353252847:AAFUtaMO5pKvJd8katYrDpNHim5J-eJuahs'  прод
bot = TeleBot(TOKEN)

a = '''Ваш матч состоится в *18:30 28\\.08*

🆔 EA ID соперника: `{}`
💬 Telegram соперника: @{}
''' + escape_markdown('''
Если время матча не подходит, свяжитесь с оппонентом для договорённости и отправьте в поддержку скриншот, подтверждающий изменение.

Пожалуйста, убедитесь, что сможете принять участие. В противном случае, свяжитесь с /support.

После завершения матча вам необходимо воспользоваться командой /validate и отправить скриншот с результатами.''')

FIFTEEN_MINUTES = '''Ваш матч начнётся *через 15 минут* ⌛️

🆔 EA ID соперника: `{}`
💬 Контакты соперника: @{}
''' + escape_markdown('''
📹 Если подозреваете нечестную игру, начните запись и отправьте в /support.
📶 При проблемах с интернет-соединением обращайтесь в поддержку.

📸 После матча обе стороны обязаны отправить скриншоты или фото результатов в чат (включив режим валидации /validate). 
Текстовые результаты не принимаются.''')

from utils.database import MatchORM
cc = 0
with Session() as session:
    users_pairs = session.query(MatchORM.player_a_id, MatchORM.player_b_id).filter(
        MatchORM.is_completed == False).filter(MatchORM.round == 5).all()
    for user1, user2 in users_pairs:
        print(user1, user2)
        if cc < 32:
            cc += 1
            continue
        user1_obj = session.query(UserORM).filter(UserORM.id == user1).first()
        user2_obj = session.query(UserORM).filter(UserORM.id == user2).first()

        message1 = FIFTEEN_MINUTES.format(escape_markdown(user2_obj.ea_id),
                                          escape_markdown(user2_obj.telegram_username))
        message2 = FIFTEEN_MINUTES.format(escape_markdown(user1_obj.ea_id),
                                          escape_markdown(user1_obj.telegram_username))

        try:
            bot.send_message(user1_obj.telegram_id, message1, parse_mode='MarkdownV2')
        except Exception as e:
            print(user1_obj.ea_id)

        try:
            bot.send_message(user2_obj.telegram_id, message2, parse_mode='MarkdownV2')
        except Exception as e:
            print(user2_obj.ea_id)
        cc += 1