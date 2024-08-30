from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from bot.core.filters import *
from bot.core.translator import translate as tr


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def start(self, message: types.Message, state: FSMContext):
        user = await User.get(user_obj=message.from_user, user_id=message.from_user.id)
        await message.delete()
        await self.bot.send_message(message.chat.id, tr(user.language, "TEXT_START"))

    def setup(self, dp: Dispatcher):
        dp.message.register(self.start, UpdateUser(), IsPrivate(), Command('start'))
