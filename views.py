from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes

import sc


def create_keyboard(requests, filter="all"):
    keyboard = []
    keyboard.append(InlineKeyboardButton(f"Filter: {filter}", callback_data="filter"))
    for request in requests:
        keyboard.append(InlineKeyboardButton(f"{request.id} - {request.subject}", callback_data=f"request_{request.id}"))
    #TODO: add pagination
    return InlineKeyboardMarkup.from_column(keyboard)


async def index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_requests = sc.index()
    requests_keyboard = create_keyboard(last_requests)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!",
        reply_markup=requests_keyboard
    )


async def general_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filter = context.user_data.get("filter", "all")
    if filter == "all":
        last_requests = sc.index()
    elif filter == "my":
        last_requests = sc.list_technician(update.effective_chat.id)
    elif filter == "all_my_groups":
        last_requests = sc.list_technician_group(update.effective_chat.id)
    requests_keyboard = create_keyboard(last_requests, filter)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello. Morning!",
        reply_markup=requests_keyboard
    )
