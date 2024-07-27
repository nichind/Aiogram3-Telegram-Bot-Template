from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from .core import *
from loguru import logger
import asyncio


async def create_dp(token: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError:
        logger.error(f"Invalid token: {token}")
        return
    dp = Dispatcher(storage=MemoryStorage())
    await bot.set_my_commands([
        BotCommand(command='start', description='Start the bot.'),
    ])

    Admin(bot).setup(dp)
    # Messages(bot_id).setup(dp)
    # Callbacks(bot_id).setup(dp)
    # dp.setup_middleware(ThrottlingMiddleware())
    # dp.setup_middleware(IsSubbed())

    logger.success(f"Created Dispatcher for @{(await bot.get_me()).username}, starting polling...")
    return dp.start_polling(bot)
