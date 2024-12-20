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
        # group = await Group.get(group_obj=message.chat, group_id=message.chat.id)
        await self.bot.send_message(message.chat.id, self.bot.tr(user.language, "TEXT_START_GROUP"),
                                    reply_to_message_id=message.message_id)

    def setup(self, dp: Dispatcher):
        dp.message.register(self.start, IsGroup(), UpdateGroup(), Command('start'))
