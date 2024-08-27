from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine('mysql+pymysql://XPEvent:px9TWv5uQI&2@copenakum.beget.app:3306/XPEvent', pool_pre_ping=True,
                       pool_recycle=3600)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class PlatformORM(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class UserORM(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    telegram_id = Column(BigInteger, unique=True)
    telegram_username = Column(String(255))
    platform = Column(Integer, ForeignKey('platforms.id'))
    ea_id = Column(String(255))
    in_game = Column(Boolean, default=False)


class SupportLogORM(Base):
    __tablename__ = 'support_log'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    emoji = Column(String(5, 'utf8mb4_bin'))
    message = Column(String(16384, 'utf8mb4_bin'))


class NotificationORM(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String(255))
    date = Column(DateTime)


class MatchORM(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    player_a_id = Column(Integer, ForeignKey('users.id'))
    player_b_id = Column(Integer, ForeignKey('users.id'))
    score_player_a = Column(Integer)
    score_player_b = Column(Integer)
    round = Column(Integer)
    match_number = Column(Integer)
    is_completed = Column(Boolean, default=False)
    winner_id = Column(Integer)

    player_a = relationship("UserORM", foreign_keys=[player_a_id])
    player_b = relationship("UserORM", foreign_keys=[player_b_id])
