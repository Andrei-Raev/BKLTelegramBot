from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('mysql+mysqldb://XPEvent:px9TWv5uQI&2@copenakum.beget.app:3306/XPEvent', pool_pre_ping=True,
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
