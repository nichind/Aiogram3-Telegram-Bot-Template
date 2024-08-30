from aiogram import types, Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from .filters import *
from json import load, dump
from bot.core.translator import translate as tr


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def simple_command(self, message: types.Message, state: FSMContext):
        cfg = load(open('./config.json', 'r', encoding='utf-8'))
        for command in cfg['simple_commands']:
            if message.text.replace('/', '') == command['name'].replace('/', ''):
                if tr(message.from_user.language_code, command['answer']) != command['answer']:
                    command['answer'] = tr(message.from_user.language_code, command['answer'])
                await message.delete()
                if 'image' in command.keys() and command['image'] != "":
                    await self.bot.send_photo(message.chat.id, command['image'], command['answer'])
                else:
                    await self.bot.send_message(message.chat.id, command['answer'])
                break

    def setup(self, dp: Dispatcher):
        dp.message.register(self.simple_command, UpdateUser(), StateFilter(None))
