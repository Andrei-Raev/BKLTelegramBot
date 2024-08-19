from utils.database import UserORM, Session, PlatformORM


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


def set_telegram_id_by_user_id(user_id: int, telegram_id: int) -> None:
    with Session() as session:
        if session.query(UserORM).filter_by(telegram_id=telegram_id).first() is not None:
            return

        user: UserORM = session.query(UserORM).filter_by(id=user_id).first()
        user.telegram_id = telegram_id
        session.commit()


def get_user_info(user_id: int) -> UserORM:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        return user


def get_platform_by_id(platform_id: int) -> PlatformORM:
    with Session() as session:
        platform: PlatformORM = session.query(PlatformORM).filter_by(id=platform_id).first()
        return platform


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


def check_user_exist(user_id: int) -> bool:
    with Session() as session:
        user: UserORM = session.query(UserORM).filter_by(telegram_id=user_id).first()
        return user is not None


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
