from aiogram import types
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from time import time
from typing import Self, List
from loguru import logger

# Feel free to change this to postgresql or any other database.
engine = create_engine('sqlite:///./bot.sqlite?check_same_thread=False', pool_size=20, max_overflow=50)
Base = declarative_base()


class Session(sessionmaker):
    def __new__(cls):
        """Session generator for database operations. Should be closed with `.close()` after usage"""
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
    joined_at = Column(Integer)
    active_at = Column(Integer, default=0)
    edit_at = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    blocked_bot = Column(Boolean, default=False)

    # Optional fields - feel free to add more fields or remove if you don't need them

    balance_usd = Column(Float, default=0.0)

    def __repr__(self):
        return f'User({self.user_id}, {self.username})'

    @classmethod
    async def add(cls, user_obj: types.User, **kwargs) -> bool:
        """Add User object to database. Will fail if user with this id already exists. Returns True if user was added"""
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
        logger.info(f'{user} added to database')
        session.close()
        return True

    @classmethod
    async def get(cls, user_obj=None, user_id: int = None, **kwargs) -> Self:
        """Get User object from database"""
        if user_obj is not None:
            await cls.add(user_obj)
        session = Session()
        user = session.query(User).filter_by(user_id=user_id, **kwargs).first()
        # logger.info(f'{user} got from database')
        session.close()
        return user

    @classmethod
    async def get_all(cls, **kwargs) -> List[Self]:
        """Get all User objects from database"""
        session = Session()
        users = session.query(User).filter_by(**kwargs).all()
        logger.info(f'{users} got from database')
        session.close()
        return users

    @classmethod
    async def update(cls, user_id: int, **kwargs) -> Self:
        """Update User object in database"""
        session = Session()
        user = session.query(User).filter_by(user_id=user_id).first()
        for key, value in kwargs.items():
            setattr(user, key, value)
        setattr(user, 'edit_at', time())
        session.commit()
        logger.info(f'{user} updated in database with {kwargs}')
        session.close()
        return await cls.get(user_id=user_id)


class Group(Base):
    __tablename__: str = 'groups'

    # Required fields - do not edit or something will break, you don't want it to happen, do you?

    group_id = Column(Integer, primary_key=True)
    name = Column(String, default=None)
    link = Column(String, default=None)
    description = Column(String, default=None)
    joined_at = Column(Integer)
    active_at = Column(Integer, default=0)
    edit_at = Column(Integer, default=0)
    current_bot = Column(Integer)
    members_count = Column(Integer, default=0)
    is_forum = Column(Boolean, default=False)
    removed_bot = Column(Boolean, default=False)

    # Optional fields - feel free to add more fields or remove if you don't need them

    def __repr__(self):
        return f'Group({self.group_id}, {self.name})'

    @classmethod
    async def add(cls, group_obj: types.Chat, **kwargs) -> bool:
        """Add Group object to database. Will fail if group with this id already exists. Returns True if group was added
        """
        session = Session()
        group = session.query(Group).filter_by(group_id=group_obj.id).first()
        if group is not None:
            return False
        group = Group(
            group_id=group_obj.id,
            name=group_obj.title,
            link=group_obj.invite_link,
            joined_at=time(),
            is_forum=group_obj.is_forum,
            **kwargs
        )
        session.add(group)
        session.commit()
        logger.info(f'{group} added to database')
        session.close()
        return True

    @classmethod
    async def get(cls, group_obj=None, group_id: int = None, **kwargs) -> Self:
        """Get Group object from database"""
        if group_obj is not None:
            await cls.add(group_obj)
        session = Session()
        group = session.query(Group).filter_by(group_id=group_id, **kwargs).first()
        # logger.info(f'{group} got from database')
        session.close()
        return group

    @classmethod
    async def get_all(cls, **kwargs) -> List[Self]:
        """Get all Group objects from database"""
        session = Session()
        groups = session.query(Group).filter_by(**kwargs).all()
        logger.info(f'{groups} got from database')
        session.close()
        return groups

    @classmethod
    async def update(cls, group_id: int, **kwargs) -> Self:
        """Update Group object in database"""
        session = Session()
        group = session.query(Group).filter_by(group_id=group_id).first()
        for key, value in kwargs.items():
            setattr(group, key, value)
        setattr(group, 'edit_at', time())
        session.commit()
        logger.info(f'{group} updated in database with {kwargs}')
        session.close()
        return await cls.get(group_id=group_id)


class Invoice(Base):
    __tablename__: str = 'invoices'

    invoice_id = Column(Integer, primary_key=True)
    identifier = Column(Integer)
    provider = Column(String)
    amount = Column(Float)
    currency = Column(String, default=None)
    pay_info = Column(String, default=None)
    status = Column(String, default=None)
    created_at = Column(Integer)
    edit_at = Column(Integer, default=0)

    def __repr__(self):
        return f'Invoice({self.invoice_id}, {self.identifier}, {self.provider}, {self.amount}, {self.currency})'

    @classmethod
    async def add(cls, **kwargs) -> bool:
        """Add Invoice object to database. Will fail if invoice with this id already exists.
        Returns True if invoice was added"""
        session = Session()
        invoice = session.query(Invoice).filter_by(invoice_id=kwargs['invoice_id']).first()
        if invoice:
            return False
        invoice = Invoice(
            invoice_id=len(await cls.get_all()) + 1,
            **kwargs
        )
        session.add(invoice)
        session.commit()
        logger.info(f'{invoice} added to database')
        session.close()
        return True

    @classmethod
    async def get(cls, **kwargs) -> Self:
        """Get Invoice object from database"""
        session = Session()
        invoice = session.query(Invoice).filter_by(**kwargs).first()
        logger.info(f'{invoice} got from database')
        session.close()
        return invoice

    @classmethod
    async def get_all(cls, **kwargs) -> List[Self]:
        """Get all Invoice objects from database"""
        session = Session()
        invoices = session.query(Invoice).filter_by(**kwargs).all()
        logger.info(f'{invoices} got from database')
        session.close()
        return invoices

    @classmethod
    async def update(cls, invoice_id, **kwargs) -> Self:
        """Update Invoice object in database"""
        session = Session()
        invoice = session.query(Invoice).filter_by(invoice_id=invoice_id).first()
        for key, value in kwargs.items():
            setattr(invoice, key, value)
        setattr(invoice, 'edit_at', time())
        session.commit()
        logger.info(f'{invoice} updated in database with {kwargs}')
        session.close()
        return await cls.get(**kwargs)


# Create tables
Base.metadata.create_all(engine)
