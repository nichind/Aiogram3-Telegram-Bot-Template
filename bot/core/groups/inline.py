from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from ..other import *


class CurrentInst:
    def __init__(self, bot: Bot):
        
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def inline_query(self, query: InlineQuery, state: FSMContext):
        print(query)

    def setup(self, dp: Dispatcher):
        dp.inline_query.register(self.inline_query)
