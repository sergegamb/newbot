from telegram import Update
from telegram.ext import ContextTypes

import logging

from admin import ADMIN_ID
from admin import TECHNICIANS

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def log_message(func):
    """
    Decorator to log incoming messages before calling the handler function.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Received message: '{update.message.text}' from chat ID: {update.effective_chat.id}")
        if update.effective_chat.id != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Received message: '{update.message.text}' from {update.effective_user.username}")
        return await func(update, context)
    return wrapper

def log_query(func):
    """
    Decorator to log incoming queries before calling the handler function.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        logger.info(f"Received query: '{query.data}' from chat ID: {update.effective_chat.id}")
        if update.effective_chat.id != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Received query: '{query.data}' from {update.effective_user.username}")
        return await func(update, context)
    return wrapper
    