from asyncio import run, sleep, create_task, gather
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time
from json import load, decoder
from bot import create_dp
from loguru import logger


print(f'\n\n{"="*90}\nBot Template made by @nichind, https://github.com/nichind/Python-Telegram-Bot-Template')
print(f'Donate $TON: UQDyPKaSUOIPnWVdxRQhk0tEZaSG6cQcOfZVdAnPqlI-T8Ot')
print(f'My telegram channel: https://t.me/nichindpf\n{"="*90}\n')
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
    for token in tokens:
        if token not in bots.running:
            logger.info(f'Trying to start bot with id {token.split(":")[0]}')
            bots.running += [token]
            dp = await create_dp(token)
            if dp:
                tasks += [create_task(dp)]

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
            run(run_bots(self.bots))


if __name__ == '__main__':
    bots = Bots()
    event_handler = ChangeConfigHandler(bots)
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)
    observer.start()
    run(run_bots(bots))
