import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import load_dotenv


load_dotenv()

storage = RedisStorage2('localhost', 6379, db=1)

TOKEN_BOT = os.getenv('B_TOKEN')
chief = os.getenv('chief_admin')
URL_APP = ''

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot, storage=storage)
