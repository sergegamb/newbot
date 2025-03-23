from telegram import Update
from telegram.ext import ContextTypes

import logging

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
        return await func(update, context)
    return wrapper

def log_query(func):
    """
    Decorator to log incoming queries before calling the handler function.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        logger.info(f"Received query: '{query.data}' from chat ID: {update.effective_chat.id}")
        return await func(update, context)
    return wrapper
    