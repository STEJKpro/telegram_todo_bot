"""
This example shows how to use webhook on behind of any reverse proxy (nginx, traefik, ingress etc.)
"""
"""
This example shows how to use webhook on behind of any reverse proxy (nginx, traefik, ingress etc.)
"""
from aiogram.utils.markdown import hbold
import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict
from aiohttp import web

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from sqlalchemy import select, create_engine
from db_connection import session
from models import User, Task
import random
import string
from handlers import registration_router, global_router, task_router
from db_connection import session

from bot.middlewares import AlbumMiddleware
from os import environ
from dotenv import load_dotenv


load_dotenv()
TOKEN = getenv("BOT_TOKEN")


# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "127.0.0.1"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8080

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
# WEBHOOK_SECRET = "my-secret"
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = "https://task-bot.pravim.by"

# All handlers should be attached to the Router (or Dispatcher)
router = Router()

router.include_routers(global_router,registration_router,task_router)




# ########Web HOOk#####
# async def on_startup(bot: Bot) -> None:
#     # If you have a self-signed SSL certificate, then you will need to send a public
#     # certificate to Telegram
#     await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")


# def main() -> None:
#     # Dispatcher is a root router
#     dp = Dispatcher()
#     # ... and all other routers should be attached to Dispatcher
#     dp.include_router(router)

#     # Register startup hook to initialize webhook
#     dp.startup.register(on_startup)
#     dp.message.middleware(AlbumMiddleware.webhook_mode())

#     # Initialize Bot instance with a default parse mode which will be passed to all API calls
#     bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

#     # Create aiohttp.web.Application instance
#     app = web.Application()

#     # Create an instance of request handler,
#     # aiogram has few implementations for different cases of usage
#     # In this example we use SimpleRequestHandler which is designed to handle simple cases
#     webhook_requests_handler = SimpleRequestHandler(
#         dispatcher=dp,
#         bot=bot,
#     )
#     # Register webhook handler on application
#     webhook_requests_handler.register(app, path=WEBHOOK_PATH)

#     # Mount dispatcher startup and shutdown hooks to aiohttp application
#     setup_application(app, dp, bot=bot)

#     # And finally start webserver
#     web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
##########################
    
async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.message.middleware(AlbumMiddleware())
    
    dp.include_router(router)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())