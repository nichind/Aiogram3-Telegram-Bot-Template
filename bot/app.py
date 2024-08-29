from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from .core import *
from loguru import logger
from glob import glob
from os.path import dirname, basename, isfile, join, isdir
from os import listdir
import asyncio


async def create_dp(token: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError:
        return logger.error(f"Invalid token: {token}")
    dp = Dispatcher(storage=MemoryStorage())
    await bot.set_my_commands([
        BotCommand(command='start', description='Start the bot.'),
    ])

    Admin(bot).setup(dp)

    for folder in listdir(dirname(__file__) + '/core'):
        if isdir(dirname(__file__) + '/core/' + folder) and folder != '__pycache__':
            module = glob(join(dirname(__file__) + '/core/' + folder, "*.py"))
            __all__ = [basename(f)[:-3] for f in module if isfile(f) and not f.endswith('__init__.py')]
            for file in __all__:
                handler = __import__(f'bot.core.{folder}.{file}',
                                     globals(), locals(), ['CurrentInst'], 0)
                handler.CurrentInst(bot).setup(dp)
    # Callbacks(bot).setup(dp)
    # dp.setup_middleware(ThrottlingMiddleware())
    # dp.setup_middleware(IsSubbed())

    logger.success(f"Created Dispatcher for @{(await bot.get_me()).username}, starting polling...")
    return dp.start_polling(bot)
