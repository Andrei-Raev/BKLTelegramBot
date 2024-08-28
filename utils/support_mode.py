from random import randint

from telebot import TeleBot
from telebot.formatting import escape_markdown
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from utils.database import Session, UserORM, MatchORM
from utils.database_utils import get_user_info_by_telegram_id, get_support_log_by_telegram_id, \
    create_empty_support_log_if_not_exist, get_id_by_telegram_id, add_text_to_support_log, get_support_log, \
    get_user_id_by_id, get_all_users
from utils.mesage_template import ENABLE_SUPPORT, SEND_SUPPORT
from utils.redis import set_support_mode

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


def ask_message(message: Message, bot: TeleBot, user_id: int) -> None:
    print(message)
    print(user_id)
    if message.reply_to_message.text in [f'/msg {user_id}', '/msg@' + bot.get_me().username + f' {user_id}',
                                         'Любое следующее сообщение, являющиеся ответом на команду /msg будет отправлено']:
        bot.send_message(user_id, message.text)

        bot.send_message(message.chat.id, "Сообщение доставлено.")
        set_support_mode(user_id)
    else:
        bot.send_message(message.chat.id, "Ошибка отправки сообщения. Повторите попытку.")
        # bot.register_next_step_handler_by_chat_id(message.chat.id, ask_message, bot, user_id)


def send_init_support_mode(user_id: int, bot: TeleBot) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="Отключить", callback_data="sm:off"))

    bot.send_message(user_id, ENABLE_SUPPORT, parse_mode="MarkdownV2", reply_markup=keyboard)


def send_init_validate_mode(user_id: int, bot: TeleBot) -> None:
    bot.send_message(user_id, "Теперь отправьте скриншот")


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

        try:
            with Session() as session:
                query = session.query(MatchORM).filter(
                    (MatchORM.player_a_id == user.id) | (MatchORM.player_b_id == user.id)
                ).filter(
                    MatchORM.is_completed == False
                )

                actual_match: MatchORM = query.first()

                if actual_match.player_a_id == user.id:
                    tt = f'Оппонент: `{actual_match.player_b.ea_id}`'
                else:
                    tt = f'Оппонент: `{actual_match.player_a.ea_id}`'

        except Exception as e:
            tt = ''

        msg = f'''📨 Новое сообщение\\!

👤 Пользователь: {user_name} \\(@{user_telegram}, id: `{user_telegram_id}`\\)
🔢 EA ID: `{user_ea_id}`
{tt}

🔽 Сообщение 🔽
'''
        bot.send_message(support_chat, msg, parse_mode="MarkdownV2")

        bot.forward_message(support_chat, message.chat.id, message.message_id)


def add_message_to_support_log(message: Message, tg_id: int = None) -> bool:
    def check_user_exist(user_id: int) -> bool:
        with Session() as session:
            user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
            return user is not None

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
    cc = -1
    for user in users:
        cc += 1
        if not randint(0, 8):
            try:
                bot.edit_message_text(f'Отправка: {cc}/{len(users)} ({round(cc / len(users) * 100, 2)}%)',
                                      message_text.chat.id, message_text.message_id)
            except Exception:
                pass
        try:
            bot.send_message(user.telegram_id, message.text)
        except Exception as e:
            try:
                bot.send_message(support_chat,
                                 f'При отправке сообщения возникла ошибка: {e}\ntg id: {user.telegram_id}')
            except Exception:
                pass

    bot.edit_message_text('Отправка завершена', message_text.chat.id, message_text.message_id)


def send_win_msg(bot: TeleBot, user_ea_id: str) -> None:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(ea_id=user_ea_id).first()
        try:
            bot.send_message(user.telegram_id, f'Поздравляем с победой!', message_effect_id='5046509860389126442')
        except Exception:
            pass
