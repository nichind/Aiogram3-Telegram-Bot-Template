from aiogram.filters import Filter
from aiogram import types
from .database import User
from json import load
from time import time


class IsAdmin(Filter):
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


class UpdateUser(Filter):
    def __init__(self, bot_id: int):
        self.bot_id = bot_id

    async def __call__(self, action: types.Message | types.CallbackQuery) -> bool:
        user = await User.get(user_obj=action.from_user, user_id=action.from_user.id)
        await User.update(
            user.user_id, current_bot=self.bot_id, name=action.from_user.full_name,
            username=action.from_user.username, is_premium=action.from_user.is_premium,
            language=action.from_user.language_code, active_at=time(),
            blocked_bot=False
        )
        return True
