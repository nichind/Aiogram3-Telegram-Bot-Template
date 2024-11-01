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
from dotenv import load_dotenv
from datetime import datetime
from cryptography.fernet import Fernet
import os


db_backup_folder = './backups/'
engine = create_async_engine('sqlite+aiosqlite:///./bot.sqlite?check_same_thread=False')
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class DatabaseBackups:
    def __init__(self):
        pass
    
    @classmethod
    async def backup_db(self):        
        load_dotenv()
        CRYPT_KEY = os.getenv('DB_CRYPT_KEY')
        if not os.path.exists(db_backup_folder):
            os.mkdir(db_backup_folder)
        files = os.listdir(db_backup_folder)
        if len(files) > 4:
            files.sort()
            for f in files[:-4]:
                os.remove(db_backup_folder + f)
        with open('./bot.sqlite', 'rb') as f:
            name = f'crypted_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
            with open(db_backup_folder + name, 'wb') as f2:
                f2.write(Fernet(CRYPT_KEY.encode('utf-8')).encrypt(f.read()))
        return name

    @classmethod
    async def decrypt_db(self, replace_existing: bool = False):
        load_dotenv()
        CRYPT_KEY = os.getenv('DB_CRYPT_KEY')
        files = os.listdir(db_backup_folder)
        if len(files) == 0:
            return
        files.sort()
        with open(db_backup_folder + files[-1], 'rb') as f:
            with open('./bot.sqlite' if replace_existing else './decrypted_bot.sqlite', 'wb') as f2:
                f2.write(Fernet(CRYPT_KEY.encode('utf-8')).decrypt(f.read()))
        return files[-1]


class User(Base):
    __tablename__: str = 'users'

    user_id = Column(Integer, primary_key=True, unique=True)
    username = Column(String)
    name = Column(String)
    
    is_premium = Column(Boolean)
    access = Column(Boolean)
    ref = Column(String)
    
    current_bot = Column(Integer)
    
    language = Column(String)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    active_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    is_admin = Column(Boolean)
    is_deleted = Column(Boolean)
    
    data = Column(JSON)

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
