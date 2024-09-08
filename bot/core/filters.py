from aiogram.filters import Filter
from .database import *
from json import load
from time import time
from loguru import logger


class IsAdmin(Filter):
    """Check if user is admin. Returns True if user is admin"""
    def __init__(self):
        pass

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        with open('./config.json') as cfg:
            admins = load(cfg)['admins']
        user = await User.get(user_obj=action.from_user, user_id=action.from_user.id)
        if user.user_id in admins and not user.is_admin:
            await User.update(user.user_id, is_admin=True)
        elif user.is_admin and user.user_id not in admins:
            await User.update(user.user_id, is_admin=False)
        return (await User.get(user_id=user.user_id)).is_admin


class IsPrivate(Filter):
    """Check if current chat is private. Returns True if chat is private"""
    def __init__(self):
        pass

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        return action.chat.type == 'private'


class IsGroup(Filter):
    """Check if current chat is group. Returns True if chat is group"""
    def __init__(self):
        pass

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        return action.chat.type == 'group'


class UpdateUser(Filter):
    """Filter used to keep new user data about in the database. Returns True and updates user data"""
    def __init__(self):
        pass

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        user = await User.get(user_obj=action.from_user, user_id=action.from_user.id)
        await User.update(
            user.user_id, current_bot=int(action.bot.token.split(':')[0]), name=action.from_user.full_name,
            username=action.from_user.username, is_premium=action.from_user.is_premium,
            language=action.from_user.language_code, active_at=time(),
            blocked_bot=False
        )
        logger.info(f'{user} got {"Message" if isinstance(action, types.Message) else "Callback"}: '
                    f'"{action.text if action.text else action.data}"')
        return True


class UpdateGroup(Filter):
    """Filter used to keep new group data about in the database. Returns True and updates group data"""
    def __init__(self):
        pass

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        group = await Group.get(group_obj=action.chat, group_id=action.chat.id)
        await Group.update(
            group.group_id, current_bot=int(action.bot.token.split(':')[0]), name=action.chat.title,
            link=action.chat.invite_link, active_at=time(), blocked_bot=False,
            members_count=await action.bot.get_chat_member_count(action.chat.id),
            description=action.chat.description, is_forum=action.chat.is_forum,
        )
        return True
