from asyncio import run, sleep, create_task, gather
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time
from json import load, decoder
from bot import create_dp
from loguru import logger
from threading import Thread

print(f'\n\n{"="*90}')
print(f'Bot Template made by @nichind, https://github.com/nichind/Aiogram3-Telegram-Bot-Template')
print(f'Donate $TON: UQDyPKaSUOIPnWVdxRQhk0tEZaSG6cQcOfZVdAnPqlI-T8Ot')
print(f'My telegram channel: https://t.me/nichindpf')
print(f'My telegram blog: https://t.me/no_money_baby')
print(f'{"="*90}\n')
# don't edit this lines ^-^ or I will find you :D


class Bots:
    def __init__(self):
        self.running = []


async def run_bots(bots: Bots()):
    tasks = []
    try:
        tokens = load(open('./config.json', 'r', encoding='utf-8'))['bots']
    except decoder.JSONDecodeError:
        return logger.error('Invalid config.json, please fix it and try again')
    except FileNotFoundError:
        logger.error('config.json not found, creating it for you...')
        open('./config.json', 'w', encoding='utf-8').write('{\n\t"admins": [\n\t\t1337\n\t],\n\t"bots": [\n\t\t""\n\t]\n}')
        return await run_bots(bots)
    for token in tokens:
        if token not in bots.running:
            if len(token) <= 15 or ':' not in token:
                logger.error(f'Invalid bot token: "{token}", skipping it')
                continue
            logger.info(f'Trying to start bot with id {token.split(":")[0]}')
            bots.running += [token]
            dp = await create_dp(token)
            if dp:
                tasks += [create_task(dp)]

    if len(bots.running) == 0:
        logger.error('No bots were started, please add bot token to config.json and try again')

    await gather(*tasks)


class ChangeConfigHandler(FileSystemEventHandler):
    def __init__(self, running_bots: Bots()):
        self.last_edit = 0
        self.bots = running_bots

    def on_modified(self, event):
        if event.is_directory:
            return None

        elif event.src_path.endswith('/config.json'):
            if time() - self.last_edit < 1:
                return
            self.last_edit = time()
            logger.info('Config file was changed, searching for new bots and starting them')
            Thread(target=run, args=(run_bots(self.bots),)).start()
            return


if __name__ == '__main__':
    bots = Bots()
    event_handler = ChangeConfigHandler(bots)
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)
    observer.start()
    run(run_bots(bots))
