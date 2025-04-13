import datetime

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes

import sc


def create_keyboard(entities, filter="All requests"):
    keyboard = []
    # TODO: Add me button
    filter = filter.replace("_", " ")
    filter = filter.capitalize()
    keyboard.append([InlineKeyboardButton(f"Filter: {filter}", callback_data="filter")])
    for entity in entities:
        keyboard.append([InlineKeyboardButton(f"{entity.id} {entity.emoji} {entity.subject}", callback_data=entity.callback)])
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
    entities = []
    if filter == "all_requests":
        entities = sc.list_all_requests(page)
    elif filter == "my_requests":
        entities = sc.list_technician_pending_requests(update.effective_chat.id, page)
    elif filter == "all_my_groups_requests":
        entities = sc.list_technician_group_requests(update.effective_chat.id, page)
    elif filter == "all_tasks":
        entities = sc.list_all_tasks(page)
    elif filter == "my_tasks":
        entities = sc.list_my_tasks(update.effective_chat.id, page)
    entities = list(entities)
    if len(entities) < sc.ROW_COUNT:
        context.user_data["last"] = True
    return entities


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
