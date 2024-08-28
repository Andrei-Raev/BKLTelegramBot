from telebot import TeleBot
from telebot.formatting import escape_markdown
from telebot.types import Message

from utils.database import UserORM, Session, PlatformORM, SupportLogORM, MatchORM
from utils.redis import get_next_emoji, clear_tournament


def send_loss_msg(bot: TeleBot, user_ea_id: str) -> None:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(ea_id=user_ea_id).first()
        try:
            bot.send_message(user.telegram_id, f'К сожалению, вам не удалось одержать победу!')
        except Exception:
            pass


def add_user_if_not_exist(user_id: int) -> bool:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        if user is None:
            user = UserORM(telegram_id=user_id)
            session.add(user)
            session.commit()
            return False
        else:
            return True


def set_telegram_id_by_telegram_id(user_id: int, telegram_id: int) -> None:
    with Session() as session:
        if session.query(UserORM).filter_by(telegram_id=telegram_id).first() is not None:
            return

        user: UserORM = session.query(UserORM).filter_by(id=user_id).first()
        user.telegram_id = telegram_id
        session.commit()


def get_user_id_by_id(user_id: int) -> UserORM:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(id=user_id).first()
        return user


def get_user_info_by_telegram_id(user_id: int) -> UserORM:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        return user


def get_platform_by_id(platform_id: int) -> PlatformORM:
    with Session() as session:
        platform: PlatformORM = session.query(PlatformORM).filter_by(id=platform_id).first()
        return platform


def get_id_by_telegram_id(telegram_id: int) -> int:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=telegram_id).first()
        return user.id


"""def template_database_setter(data: str, user_id: int) -> None:
    ..."""


def add_user_name(data: str, user_id: int) -> None:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        user.name = data
        session.commit()


def add_ea_id(data: str, user_id: int) -> None:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        user.ea_id = data
        session.commit()


def add_platform(data: str, user_id: int) -> None:
    with Session() as session:
        platform: PlatformORM = session.query(PlatformORM).filter_by(name=data).first()
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        user.platform = platform.id
        session.commit()


def get_platforms() -> list:
    with Session() as session:
        platforms: list[PlatformORM] = session.query(PlatformORM).all()
        return [platform.name for platform in platforms]


def add_telegram_username(data: str, user_id: int) -> None:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        user.telegram_username = data
        session.commit()


# --== {ЧЕКЕРЫ} ==--
"""def checker(user_id: int) -> bool:
    ..."""


def check_user_prop(user_id: int, _type: str) -> bool:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        return user.__dict__[_type] is not None


def check_name(user_id: int) -> bool:
    return check_user_prop(user_id, 'name')


def check_ea_id(user_id: int) -> bool:
    return check_user_prop(user_id, 'ea_id')


def check_platform(user_id: int) -> bool:
    return check_user_prop(user_id, 'platform')


def check_telegram_username(user_id: int) -> bool:
    return check_user_prop(user_id, 'telegram_username')


# --== {Support Log} ==--

def create_empty_support_log_if_not_exist(user_id: int) -> None:
    with Session() as session:
        if session.query(SupportLogORM).filter_by(user_id=user_id).first() is not None:
            return

        support_log = SupportLogORM(user_id=user_id, emoji=get_next_emoji(), message='')
        session.add(support_log)
        session.commit()

        return


def get_support_log(user_id: int) -> SupportLogORM:
    with Session() as session:
        support_log: SupportLogORM = session.query(SupportLogORM).filter_by(user_id=user_id).first()
        return support_log


def get_support_log_by_telegram_id(telegram_id: int) -> SupportLogORM:
    with Session() as session:
        user_id: int = session.query(UserORM).filter_by(telegram_id=int(telegram_id)).first().id
    return get_support_log(user_id)


def add_text_to_support_log(user_id: int, text: str) -> None:
    '''
    :param user_id: Это id юзера, не телеграм id
    :param text: Текст сообщения
    '''
    text += '\n' if text[-1] != '\n' else ''

    with Session() as session:
        support_log: SupportLogORM = session.query(SupportLogORM).filter_by(user_id=int(user_id)).first()
        support_log.message += text
        session.commit()


def get_all_users() -> list:
    with Session() as session:
        users: list[UserORM] = session.query(UserORM).all()
        return users


def end_match_early(bot: TeleBot, ea_id: str, target_chat: int) -> None:
    with Session() as session:
        user = session.query(UserORM).filter(UserORM.ea_id == ea_id).first()

        query = session.query(MatchORM).filter(
            (MatchORM.player_a_id == user.id) | (MatchORM.player_b_id == user.id)
        ).filter(
            MatchORM.is_completed == False
        )

        actual_match: MatchORM = query.first()

        pl_win_id = 0 if actual_match.player_a_id == user.id else 1
        actual_match.is_completed = True
        actual_match.winner_id = pl_win_id

        if pl_win_id == 0:
            opponent_id = actual_match.player_b_id
        else:
            opponent_id = actual_match.player_a_id
        if opponent_id is not None:
            opponent = session.query(UserORM).filter(UserORM.id == opponent_id).first()
            send_loss_msg(bot, opponent.ea_id)

        if actual_match.match_number % 2:
            session.query(MatchORM).filter_by(round=actual_match.round - 1,
                                              match_number=actual_match.match_number // 2).update(
                {'player_b_id': user.id})
        else:
            session.query(MatchORM).filter_by(round=actual_match.round - 1,
                                              match_number=actual_match.match_number // 2).update(
                {'player_a_id': user.id})

        session.commit()

        clear_tournament()

        bot.send_message(target_chat, f'Вы завершили матч {actual_match.id} досрочно!\nПобедил {ea_id}!')


def send_validate_message(bot: TeleBot, message: Message) -> None:
    bot.send_message(message.chat.id, 'Результаты матча направлены на валидацию!', parse_mode="MarkdownV2")


def send_val_info(bot: TeleBot, user_id: int, target_chat: int) -> None:
    with Session() as session:
        user = session.query(UserORM).filter_by(telegram_id=user_id).first()
        query = session.query(MatchORM).filter(
            (MatchORM.player_a_id == user.id) | (MatchORM.player_b_id == user.id)
        ).filter(
            MatchORM.is_completed == False
        )

        actual_match: MatchORM = query.first()

        if actual_match is None:
            bot.send_message(target_chat, 'Что то пошло не так\\!', parse_mode="MarkdownV2")
            return
        temp = f'''Матч {escape_markdown(str(actual_match.id))}: r{escape_markdown(str(actual_match.round))} m{escape_markdown(str(actual_match.match_number))} \\({escape_markdown(str(actual_match.datetime.strftime("%d.%m.%Y %H:%M")))}\\)
Игрок 1: `{escape_markdown(str(actual_match.player_a.ea_id if actual_match.player_a else 'Отсутствует'))}` \\({escape_markdown(str(actual_match.player_a.name if actual_match.player_a else 'Отсутствует'))} @{escape_markdown(str(actual_match.player_a.telegram_username if actual_match.player_a else 'Отсутствует'))}, tg id: `{escape_markdown(str(actual_match.player_a.telegram_id if actual_match.player_a else 'Отсутствует'))}`\\)
Игрок 2: `{escape_markdown(str(actual_match.player_b.ea_id if actual_match.player_b else 'Отсутствует'))}` \\({escape_markdown(str(actual_match.player_b.name if actual_match.player_b else 'Отсутствует'))} @{escape_markdown(str(actual_match.player_b.telegram_username if actual_match.player_b else 'Отсутствует'))}, tg id: `{escape_markdown(str(actual_match.player_b.telegram_id if actual_match.player_b else 'Отсутствует'))}`\\)
'''
        bot.send_message(target_chat, temp, parse_mode="MarkdownV2")


def validate_chat_mm(match_id, score_player_a, score_player_b, bot: TeleBot, target_chat) -> None:
    with Session() as session:
        actual_match: MatchORM = session.query(MatchORM).filter_by(id=match_id).first()

        pl_win_id = int(score_player_a < score_player_b)
        actual_match.is_completed = True
        actual_match.winner_id = pl_win_id

        print(actual_match)
        actual_match.score_player_a = score_player_a

        actual_match.score_player_b = score_player_b

        # session.query(MatchORM).filter_by(id=match_id).update(
        #     {'is_completed': True, 'winner_id': pl_win_id, 'player_a_score': score_player_a,
        #      'player_b_score': score_player_b})
        print(121212121212112)

        session.commit()

        if pl_win_id == 0:
            opponent_id = actual_match.player_b_id
            winner = actual_match.player_a
        else:
            opponent_id = actual_match.player_a_id
            winner = actual_match.player_b
        if opponent_id is not None:
            opponent = session.query(UserORM).filter(UserORM.id == opponent_id).first()
            send_loss_msg(bot, opponent.ea_id)
        bot.send_message(winner.telegram_id, f'Поздравляем с победой!', message_effect_id='5046509860389126442')

        session.commit()

        if actual_match.match_number % 2:
            session.query(MatchORM).filter_by(round=actual_match.round - 1,
                                              match_number=actual_match.match_number // 2).update(
                {'player_b_id': winner.id})
        else:
            session.query(MatchORM).filter_by(round=actual_match.round - 1,
                                              match_number=actual_match.match_number // 2).update(
                {'player_a_id': winner.id})

        session.commit()

        clear_tournament()

        bot.send_message(target_chat, f'Вы завершили матч {actual_match.id}!\nПобедил {winner.ea_id}!')
