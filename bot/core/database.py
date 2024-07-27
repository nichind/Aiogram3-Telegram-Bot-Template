from aiogram import types
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from time import time

engine = create_engine('sqlite:///./bot.sqlite?check_same_thread=False', pool_size=10, max_overflow=30)
Base = declarative_base()


class Session(sessionmaker):
    def __new__(cls):
        """Session generator for database operations"""
        return (sessionmaker(bind=engine))()


class User(Base):
    __tablename__: str = 'users'

    # Required fields - do not edit or something will break, you don't want it to happen, do you?

    user_id = Column(Integer, primary_key=True)
    username = Column(String, default=None)
    name = Column(String, default=None)
    is_premium = Column(Boolean, default=False)
    access = Column(Boolean, default=False)
    ref = Column(String, default=None)
    current_bot = Column(Integer)
    language = Column(String, default='en')
    joined_at = Column(Float)
    active_at = Column(Integer, default=0)
    edit_at = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    blocked_bot = Column(Boolean, default=False)

    # Optional fields - feel free to add more fields or remove if you don't need them

    balance_usd = Column(Float, default=0.0)

    @classmethod
    async def add(cls, user_obj: types.User, **kwargs) -> bool:
        """Add User object to database"""
        session = Session()
        user = session.query(User).filter_by(user_id=user_obj.id).first()
        if user is not None:
            return False
        user = User(
            user_id=user_obj.id,
            username=user_obj.username,
            name=user_obj.full_name,
            is_premium=user_obj.is_premium,
            language=user_obj.language_code,
            joined_at=time(),
            **kwargs
        )
        session.add(user)
        session.commit()
        session.close()
        return True

    @classmethod
    async def get(cls, user_obj=None, user_id: int = None, **kwargs):
        """Get User object from database"""
        if user_obj is not None:
            await cls.add(user_obj)
        session = Session()
        user = session.query(User).filter_by(user_id=user_id, **kwargs).first()
        session.close()
        return user

    @classmethod
    async def get_all(cls, **kwargs) -> list:
        """Get all User objects from database"""
        session = Session()
        users = session.query(User).filter_by(**kwargs).all()
        return users

    @classmethod
    async def update(cls, user_id: int, **kwargs):
        """Update User object in database"""
        session = Session()
        user = session.query(User).filter_by(user_id=user_id).first()
        for key, value in kwargs.items():
            setattr(user, key, value)
        setattr(user, 'edit_at', time())
        session.commit()
        session.close()
        return user


Base.metadata.create_all(engine)
