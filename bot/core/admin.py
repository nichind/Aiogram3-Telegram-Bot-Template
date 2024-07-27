from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from .database import *
from aiogram.filters import *
from .filters import *
from json import load
from .translator import translate as t


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token

    async def stats(self, message: types.Message, state: FSMContext):
        stats_dict = {
            "total": 0,
            "new": {"month": 0, "week": 0, "day": 0, "hour": 0},
            "active": {"month": 0, "week": 0, "day": 0, "hour": 0},
            "blocked": 0,
            "bots": {}
        }

        bot_ids = [int(x.split(':')[0]) for x in load(open('./config.json', 'r', encoding='utf-8'))['bots']]
        for bot_id in bot_ids:
            stats_dict['bots'][bot_id] = {
                "total": 0,
                "new": {"month": 0, "week": 0, "day": 0, "hour": 0},
                "active": {"month": 0, "week": 0, "day": 0, "hour": 0},
                "blocked": 0
            }

        users = await User.get_all()
        stats_dict['total'] = len(users)
        for user in users:
            if user.blocked_bot:
                stats_dict['blocked'] += 1
            if user.current_bot in bot_ids:
                stats_dict['bots'][user.current_bot]['total'] += 1
                if user.active_at >= time() - 60 * 60 * 24 * 30:
                    stats_dict['bots'][user.current_bot]['active']['month'] += 1
                    if user.active_at >= time() - 60 * 60 * 24 * 7:
                        stats_dict['bots'][user.current_bot]['active']['week'] += 1
                        if user.active_at >= time() - 60 * 60 * 24:
                            stats_dict['bots'][user.current_bot]['active']['day'] += 1
                            if user.active_at >= time() - 60 * 60:
                                stats_dict['bots'][user.current_bot]['active']['hour'] += 1
                if user.blocked_bot:
                    stats_dict['bots'][user.current_bot]['blocked'] += 1
                if user.joined_at >= time() - 60 * 60 * 24 * 30:
                    stats_dict['bots'][user.current_bot]['new']['month'] += 1
                    if user.joined_at >= time() - 60 * 60 * 24 * 7:
                        stats_dict['bots'][user.current_bot]['new']['week'] += 1
                        if user.joined_at >= time() - 60 * 60 * 24:
                            stats_dict['bots'][user.current_bot]['new']['day'] += 1
                            if user.joined_at >= time() - 60 * 60:
                                stats_dict['bots'][user.current_bot]['new']['hour'] += 1

            if user.active_at >= time() - 60 * 60 * 24 * 30:
                stats_dict['active']['month'] += 1
                if user.active_at >= time() - 60 * 60 * 24 * 7:
                    stats_dict['active']['week'] += 1
                    if user.active_at >= time() - 60 * 60 * 24:
                        stats_dict['active']['day'] += 1
                        if user.active_at >= time() - 60 * 60:
                            stats_dict['active']['hour'] += 1
            if user.blocked_bot:
                stats_dict['blocked'] += 1
            if user.joined_at >= time() - 60 * 60 * 24 * 30:
                stats_dict['new']['month'] += 1
                if user.joined_at >= time() - 60 * 60 * 24 * 7:
                    stats_dict['new']['week'] += 1
                    if user.joined_at >= time() - 60 * 60 * 24:
                        stats_dict['new']['day'] += 1
                        if user.joined_at >= time() - 60 * 60:
                            stats_dict['new']['hour'] += 1

        stats_text = f"""
Total users: <code>{stats_dict['total']}</code>, Blocked: <code>{stats_dict['blocked']}</code>
New users: (Month, Week, Day, Hour)
<code>{stats_dict['new']['month']}</code>, <code>{stats_dict['new']['week']}</code>, <code>{stats_dict['new']['day']}</code>, <code>{stats_dict['new']['hour']}</code>
Active users: (Month, Week, Day, Hour)
<code>{stats_dict['active']['month']}</code>, <code>{stats_dict['active']['week']}</code>, <code>{stats_dict['active']['day']}</code>, <code>{stats_dict['active']['hour']}</code>
"""
        for bot_id in bot_ids:
            stats_text += f"""
Bot: <code>{bot_id}</code>
Total: <code>{stats_dict['bots'][bot_id]['total']}</code>, Blocked: <code>{stats_dict['bots'][bot_id]['blocked']}</code>
New users: <code>{stats_dict['bots'][bot_id]['new']['month']}</code>, <code>{stats_dict['bots'][bot_id]['new']['week']}</code>, <code>{stats_dict['bots'][bot_id]['new']['day']}</code>, <code>{stats_dict['bots'][bot_id]['new']['hour']}</code>
Active users: <code>{stats_dict['bots'][bot_id]['active']['month']}</code>, <code>{stats_dict['bots'][bot_id]['active']['week']}</code>, <code>{stats_dict['bots'][bot_id]['active']['day']}</code>, <code>{stats_dict['bots'][bot_id]['active']['hour']}</code>
"""
        await message.answer(stats_text)

    def setup(self, dp: Dispatcher):
        dp.message.register(self.stats, IsAdmin(), UpdateUser(self.bot_id), StateFilter(None), Command('stats'))
