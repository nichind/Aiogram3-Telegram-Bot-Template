import os
import sys
from asyncio import run, sleep, create_task, gather, Task, new_event_loop, exceptions, get_event_loop
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time
from json import load, decoder
from bot import create_dp
from loguru import logger
from datetime import datetime, timedelta
from bot.core.other.database import DatabaseBackups, db_backup_folder
from cryptography.fernet import Fernet


print(f'\n\n{"="*90}')
print(f'Bot Template made by @nichind, https://github.com/nichind/Aiogram3-Telegram-Bot-Template')
print(f'Donate $TON: UQDyPKaSUOIPnWVdxRQhk0tEZaSG6cQcOfZVdAnPqlI-T8Ot')
print(f'My telegram channel: https://t.me/nichindpf')
print(f'My telegram blog: https://t.me/no_money_baby')
print(f'{"="*90}\n')
# don't edit this lines ^-^ or I will find you :D


class Bots:
    def __init__(self):
        self.running = {}


async def run_bots(bots: Bots = Bots()):
    tasks = []
    try:
        tokens = load(open('./config.json', 'r', encoding='utf-8'))['bots']
    except decoder.JSONDecodeError:
        return logger.error('Invalid config.json, please fix it and try again')
    except FileNotFoundError:
        logger.error('config.json not found, creating it for you...')
        with open('./example-config.json', 'r', encoding='utf-8') as f:
            with open('./config.json', 'w', encoding='utf-8') as cfg:
                cfg.write(f.read())
        return await run_bots(bots)
    
    for token in tokens:
        if token not in bots.running.keys():
            if len(token) <= 15 or ':' not in token:
                logger.error(f'Invalid bot token: "{token}", skipping it')
                continue
            logger.info(f'Trying to start bot with id {token.split(":")[0]}')
            dp = await create_dp(token)
            if dp:
                bots.running[token] = create_task(dp)
                tasks.append(bots.running[token])
            else:
                bots.running[token] = None

    to_pop = []
    for token, task in bots.running.items():
        if token not in tokens and task is not None:
            logger.info(f'Stopping bot with id {token.split(":")[0]}')
            try:
                task.cancel()
            except exceptions.CancelledError:
                pass
            except Exception as exc:
                logger.error(f'Failed to cancel task: {exc}')
            to_pop += [token] 
    
    for token in to_pop:
        bots.running.pop(token)
        logger.info(f'Bot with id {token.split(":")[0]} was stopped')

    if len(bots.running) == 0:
        logger.error('No bots were started, add valid bot token to config.json')
        logger.info('Restarting in 10 seconds...')
        event_handler.last_edit = time() + 10
        await sleep(10)
        return await run_bots(bots)        

    try:
        await gather(*tasks)
    except Exception as exc:
        logger.error(f'Failed to gather: {exc}')


async def sheduled_backup() -> None:
    logger.info(f'Sheduled database backup every 6 hours from now on, if you wish to backup manually, do "python main.py backup"')
    while True:
        logger.info(f'Next backup at {datetime.now() + timedelta(hours=6)}')
        await sleep(60 * 60 * 6)
        await DatabaseBackups.backup_db()


class ChangeConfigHandler(FileSystemEventHandler):
    def __init__(self, running_bots: Bots = Bots()):
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
            new_event_loop().run_until_complete(run_bots(self.bots))
        return


if __name__ == '__main__':
    logger.add("./logs/{time:YYYY}-{time:MM}-{time:DD}.log", rotation="00:00", level="INFO")
    if '.env' not in os.listdir():
        with open('./.env', 'w', encoding='utf-8') as f:
            f.write(f'DB_CRYPT_KEY={Fernet.generate_key().decode("utf-8")}')
        logger.warning('Created .env file with DB_CRYPT_KEY')
    
    if 'backup' in sys.argv:
        filename = new_event_loop().run_until_complete(DatabaseBackups.backup_db())
        logger.success(f'Database was backed up to {db_backup_folder}{filename}')
        logger.info('Start the bots? (y/n)')
        if input("> ") != 'y':
            sys.exit(0)
    
    elif 'restore' in sys.argv:
        replace_existing = 'replace' in sys.argv or input('Replace existing database? (y/n) ') == 'y'
        filename = new_event_loop().run_until_complete(DatabaseBackups.decrypt_db(replace_existing and input('Replacing means currently existing database will be gone. Are you sure? (y/n) ') == 'y'))
        logger.success(f'Database was restored from {db_backup_folder}{filename}')
        logger.info('Start the bots? (y/n)')
        if input("> ") != 'y':
            sys.exit(0)
    
    bots = Bots()
    
    tasks = [sheduled_backup(), run_bots(bots)]
    get_event_loop().run_until_complete(gather(*tasks))
    
    event_handler = ChangeConfigHandler(bots)
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)
    observer.start()
