from aiogram import types, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from .filters import *
from json import load, dump
from asyncio import run, sleep
from aiogram.fsm.state import State, StatesGroup
from aiogram import exceptions
from io import BytesIO


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def simple_command(self, message: types.Message, state: FSMContext):
        print(message)
        cfg = load(open('./config.json', 'r', encoding='utf-8'))
        for command in cfg['simple_commands']:
            if message.text.replace('/', '') == command['name'].replace('/', ''):
                await message.delete()
                if 'image' in command.keys() and command['image'] != "":
                    await self.bot.send_photo(message.chat.id, command['image'], command['answer'])
                else:
                    await self.bot.send_message(message.chat.id, command['answer'])
                break

    def setup(self, dp: Dispatcher):
        dp.message.register(self.simple_command, UpdateUser(), StateFilter(None))
