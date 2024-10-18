from aiogram import types
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON, DateTime, func, BINARY, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from asyncio import create_task, get_event_loop, new_event_loop
from time import time
from typing import Self, List
from loguru import logger

# Feel free to change this to postgresql or any other database.
engine = create_async_engine('sqlite+aiosqlite:///./bot.sqlite?check_same_thread=False')
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class User(Base):
    __tablename__: str = 'users'

    user_id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, default=None)
    name = Column(String, default=None)
    
    is_premium = Column(Boolean, default=None)
    access = Column(Boolean, default=None)
    ref = Column(String, default=None)
    
    current_bot = Column(Integer, default=None)
    
    language = Column(String, default=None)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    active_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    is_admin = Column(Boolean, default=None)
    is_deleted = Column(Boolean, default=None)
    
    data = Column(JSON, default=None)

    def __repr__(self):
        return f'User({self.user_id}, {self.username})'

    @classmethod
    async def add(cls, **kwargs) -> bool:
        async with async_session() as session:
            if (await session.execute(select(User).filter_by(**kwargs))).scalar() is None:
                user = User(
                    **kwargs
                )
                session.add(user)
                await session.commit()
        return await cls.get(user_id=user.user_id)

    @classmethod
    async def get(cls, **kwargs) -> Self:
        async with async_session() as session:
            user = (await session.execute(select(User).filter_by(**kwargs))).scalar()
            if user is None and 'user_id' in kwargs:
                await cls.add(user_id=kwargs['user_id'])
        return user

    @classmethod
    async def get_all(cls, **kwargs) -> List[Self]:
        async with async_session() as session:
            users = (await session.execute(select(User).filter_by(**kwargs))).scalars().all()
        return users

    @classmethod
    async def update(cls, user_id: int, **kwargs) -> Self:
        async with async_session() as session:
            user = await cls.get(user_id=user_id)
            for key, value in kwargs.items():
                setattr(user, key, value)
            await session.commit()
        return await cls.get(user_id=user_id)
    

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if get_event_loop() is None:
    loop = new_event_loop()
    loop.run_until_complete(create_tables())
else:
    get_event_loop().run_until_complete(create_tables())
