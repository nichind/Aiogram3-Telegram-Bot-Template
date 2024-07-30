from aiogram import types, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from .filters import *
from json import load
from asyncio import run
from aiogram.fsm.state import State, StatesGroup
from aiogram import exceptions


class SendStates(StatesGroup):
    wait_for_message = State()
    confirmation = State()


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
        await self.bot.send_message(message.from_user.id, stats_text)

    async def send(self, message: types.Message, state: FSMContext):
        await message.delete()
        await state.set_state(SendStates.wait_for_message)
        text = f"Send message you want to send to all users."
        answer = await self.bot.send_message(message.from_user.id, text)
        await state.update_data(answer_id=answer.message_id)

    async def send_message(self, message: types.Message, state: FSMContext):
        copy = message.model_copy()
        await self.bot.delete_message(message.from_user.id, (await state.get_data())['answer_id'])
        await state.set_state(None)
        keyboard = [
            [InlineKeyboardButton(text="✅ Send", callback_data='send:yes')],
            [InlineKeyboardButton(text="🗑️ No", callback_data='send:no')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        text = "Are you sure you want to send this message to all users?"
        answer = await self.bot.send_message(message.from_user.id, text, reply_markup=markup)
        await state.update_data(answer_id=answer.message_id, copy=copy)

    async def send_callback(self, call: CallbackQuery, state: FSMContext):
        answer_id = (await state.get_data())['answer_id']
        action = call.data[5:]
        if action == 'yes':
            await call.message.delete()

            copy: Message = (await state.get_data())['copy']
            photo = copy.photo[-1] if copy.photo else None
            document = copy.document if copy.document else None
            text = copy.text if copy.text else None
            caption = copy.caption if copy.caption else None
            sticker = copy.sticker if copy.sticker else None
            voice = copy.voice if copy.voice else None

            users = await User.get_all()
            bots = {}

            with open('./config.json') as cfg:
                tokens = load(cfg)['bots']
            for token in tokens:
                bots[int(token.split(":")[0])] = Bot(token=token)

            success = 0
            status_message = await self.bot.send_message(call.from_user.id, "Starting sending...", reply_to_message_id=copy.message_id)

            for index, user in enumerate(users):
                bot = bots.get(user.current_bot)

                # if user blocked bot
                if user.blocked_bot:
                    continue

                # if bot not found
                if not bot:
                    continue

                # send message
                try:
                    if photo:
                        await bot.send_photo(user.user_id, photo.file_id, caption=caption)
                    elif document:
                        await bot.send_document(user.user_id, document.file_id, caption=caption)
                    elif text:
                        await bot.send_message(user.user_id, text)
                    elif sticker:
                        await bot.send_sticker(user.user_id, sticker.file_id)
                    elif voice:
                        await bot.send_voice(user.user_id, voice.file_id)
                    success += 1
                except exceptions.TelegramForbiddenError:
                    await User.update(user.user_id, blocked_bot=True)
                except exceptions.TelegramNotFound:
                    await User.update(user.user_id, blocked_bot=True)

                if index % 100 == 0:
                    await status_message.edit_text(f"Sending... {index}/{len(users)} - Success: {success}")

            for bot in bots.values():
                await bot.session.close()

            await status_message.edit_text(f"Finished. Success: {success} / {len(users)}")

        elif action == 'no':
            await self.bot.delete_message(call.from_user.id, call.message.message_id)

    def setup(self, dp: Dispatcher):
        dp.message.register(self.stats, IsAdmin(), UpdateUser(self.bot_id), StateFilter(None), Command('stats'))
        dp.message.register(self.send, IsAdmin(), UpdateUser(self.bot_id), StateFilter(None), Command('send'))
        dp.message.register(self.send_message, IsAdmin(), UpdateUser(self.bot_id),
                            StateFilter(SendStates.wait_for_message))
        dp.callback_query.register(self.send_callback, IsAdmin(), UpdateUser(self.bot_id), F.data[:5] == 'send:')
