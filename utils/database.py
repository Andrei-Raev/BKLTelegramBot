from datetime import datetime

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

    def __str__(self):
        return f'Match {self.id} (N{self.match_number} T{self.round}): {self.player_a} VS {self.player_b} at {self.datetime}: {self.score_player_a}/{self.score_player_b}'

    def __repr__(self):
        return self.__str__()

    # @staticmethod
    # def new(session, datetime, player_a_id, player_b_id, _round, match_number, is_completed=False, winner_id=None):
    #     match = MatchORM(
    #         datetime=datetime,
    #         player_a_id=player_a_id,
    #         player_b_id=player_b_id,
    #         round=_round,
    #         match_number=match_number,
    #         is_completed=is_completed,
    #         winner_id=winner_id
    #     )
    #     session.add(match)
    #     session.commit()
    #     return match

    def end_match(self, score_player_a, score_player_b):
        self.score_player_a = int(score_player_a)
        self.score_player_b = int(score_player_b)

        if self.score_player_a > self.score_player_b:
            self.winner_id = self.player_a_id
        else:
            self.winner_id = self.player_b_id

        self.is_completed = True

        with Session() as session:
            session.merge(self)
            session.commit()

    @property
    def status(self):
        if self.player_a_id is None and self.player_b_id is None:
            return 0
        elif self.is_completed == 1:
            return 4
        elif self.player_a_id is None or self.player_b_id is None:
            return 1

        elif self.datetime:
            if self.datetime <= datetime.now():
                return 3
            else:
                return 2
        elif self.player_a_id and self.player_b_id:
            return 2
        else:
            return 5
