from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from ..other import *


class CurrentInst:
    def __init__(self, bot: Bot):
        
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def start(self, message: Message, state: FSMContext):
        user = await User.get(user_id=message.from_user.id)
        await message.delete()
        await message.answer(text=self.bot.tr(user.language, "TEXT_START"))

    def setup(self, dp: Dispatcher):
        dp.message.register(self.start, IsPrivate(), Command('start'))
