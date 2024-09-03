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
        if 'simple_commands' not in cfg.keys():
            return
        for command in cfg['simple_commands']:
            if message.text.replace('/', '') == command['name'].replace('/', ''):
                user = await User.get(user_obj=message.from_user, user_id=message.from_user.id)
                if tr(user.language, command['answer']) != command['answer']:
                    command['answer'] = tr(user.language, command['answer'])
                await message.delete()
                if 'image' in command.keys() and command['image'] != "":
                    try:
                        await self.bot.send_photo(message.chat.id, command['image'], command['answer'])
                        break
                    except:
                        pass
                await self.bot.send_message(message.chat.id, command['answer'])
                break

    def setup(self, dp: Dispatcher):
        dp.message.register(self.simple_command, StateFilter(None))
