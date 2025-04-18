import time
import logging
import os
import datetime

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from admin import TECHNICIANS
from decorators import log_message, log_query
import sc


# Conversation states
SELECTING_TECHNICIAN, TYPING_TASK_TITLE, TYPING_DUE_DATE, TYPING_TASK_DESCRIPTION = range(4)


@log_query
async def add_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the task creation process."""
    keyboard = [
        [InlineKeyboardButton(name, callback_data=str(user_id))]
        for user_id, name in TECHNICIANS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Please select a technician to assign the task to:", reply_markup=reply_markup
    )
    return SELECTING_TECHNICIAN


@log_query
async def technician_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected technician and asks for the task title."""
    query = update.callback_query
    await query.answer()
    technician_id = int(query.data)
    technician_name = TECHNICIANS.get(technician_id)
    if technician_name:
        context.user_data["technician_id"] = technician_id
        context.user_data["technician_name"] = technician_name
        await query.edit_message_text(
            text=f"You selected {technician_name}. Now, please send the task title."
        )
        return TYPING_TASK_TITLE
    else:
        await query.edit_message_text(text="Invalid technician selected.")
        return ConversationHandler.END


@log_message
async def task_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the task title and asks for the due date."""
    task_title = update.message.text
    context.user_data["task_title"] = task_title
    await update.message.reply_text(
        text=f"Task title set to '{task_title}'. Now, please send the due date in days."
    )
    return TYPING_DUE_DATE


@log_message
async def due_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the due date and creates the task."""
    try:
        due_date_days = int(update.message.text)
        if due_date_days <= 0:
            await update.message.reply_text("Due date must be a positive number of days.")
            return TYPING_DUE_DATE
        context.user_data["due_date_days"] = due_date_days

        task_title = context.user_data.get("task_title")
        technician_id = context.user_data.get("technician_id")
        technician_name = context.user_data.get("technician_name")

        days = context.user_data.get("due_date_days", 0)
        now = datetime.datetime.now()
        due_date = now + datetime.timedelta(days=days)
        due_date = time.mktime(due_date.timetuple())
        due_date = int(due_date * 1000)

        request_id = context.user_data.get("request_id")
        task = sc.add_task(request_id, technician_name, task_title, due_date)

        await update.message.reply_text(
            f"Task '{task_title}' assigned to {technician_name} (ID: {technician_id}).",
            reply_markup=task.keyboard
        )
        context.user_data.clear()
        context.user_data["task_id"] = task.id
        context.user_data["request_id"] = request_id
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a number of days.")
        return TYPING_DUE_DATE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Task creation cancelled.")
    return ConversationHandler.END


# Create the conversation handler
task_add_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_task_button, pattern="add_task")],
    states={
        SELECTING_TECHNICIAN: [
            CallbackQueryHandler(technician_selected, pattern=r"^\d+$")
        ],
        TYPING_TASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_title_received)],
        TYPING_DUE_DATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, due_date_received)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


@log_query
async def add_task_description_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the task description adding process."""
    query = update.callback_query
    await query.answer(query.data)
    await update.callback_query.edit_message_text(
        "Please send the task description:"
    )
    return TYPING_TASK_DESCRIPTION


@log_message
async def task_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the task description and ends the conversation."""
    task_description = update.message.text
    task_id = context.user_data.get("task_id")
    request_id = context.user_data.get("request_id")

    task = sc.add_task_description(request_id, task_id, task_description)

    await update.message.reply_text(
        text=task.text,
        reply_markup=task.keyboard,
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


task_description_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_task_description_button, pattern="task_description_add")],
    states={
        TYPING_TASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_description_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
