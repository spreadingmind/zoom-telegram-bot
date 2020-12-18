from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, ForeignKey('users.telegram_id'))
    name = Column(String)
    link = Column(String)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer)
    redirect_hash = Column(String)
    telegram_id = Column(Integer, primary_key=True)
    telegram_username = Column(String)
    zoom_access_token = Column(String)
    meetings = relationship('Meeting')
