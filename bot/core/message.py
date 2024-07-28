from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from .filters import *
from .translator import translate as tr


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def start(self, message: types.Message, state: FSMContext):
        user = await User.get(user_obj=message.from_user, user_id=message.from_user.id)
        await message.answer(tr(user.language, "TEXT_MENU"))

    def setup(self, dp: Dispatcher):
        dp.message.register(self.start, UpdateUser(self.bot_id), Command('start'))