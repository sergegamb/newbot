import datetime

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes

import sc


def create_keyboard(requests, filter="All requests"):
    keyboard = []
    # TODO: Add task filters
    # TODO: Add me button
    keyboard.append([InlineKeyboardButton(f"Filter: {filter}", callback_data="filter")])
    for request in requests:
        keyboard.append([InlineKeyboardButton(f"{request.id} {request.emoji} {request.subject}", callback_data=f"request_{request.id}")])
    keyboard.append([InlineKeyboardButton("Refresh", callback_data="refresh"),
                     InlineKeyboardButton("<<", callback_data="previous"),
                     InlineKeyboardButton(">>", callback_data="next")])
    return InlineKeyboardMarkup(keyboard)


async def index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_requests = sc.index()
    requests_keyboard = create_keyboard(last_requests)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!",
        reply_markup=requests_keyboard
    )


async def get_by_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filter = context.user_data.get("filter", "all_requests")
    page = context.user_data.get("page", 0)
    last_requests = []
    if filter == "all_requests":
        last_requests = sc.list_last(page)
    elif filter == "my_requests":
        last_requests = sc.list_technician(update.effective_chat.id, page)
    elif filter == "all_my_groups_requests":
        last_requests = sc.list_technician_group(update.effective_chat.id, page)
    last_requests = list(last_requests)
    if len(last_requests) < sc.ROW_COUNT:
        context.user_data["last"] = True
    return last_requests


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_requests = await get_by_filter(update, context)
    requests_keyboard = create_keyboard(last_requests, context.user_data.get("filter", "All requests"))
    await update.callback_query.edit_message_text(
        text=f"{datetime.datetime.now()}",
        reply_markup=requests_keyboard)


async def general_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_requests = await get_by_filter(update, context)
    requests_keyboard = create_keyboard(last_requests, context.user_data.get("filter", "All requests"))
    await update.callback_query.edit_message_text(
        text="Hello. Morning!",
        reply_markup=requests_keyboard
    )
