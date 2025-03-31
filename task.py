import logging
import os

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
SELECTING_TECHNICIAN, TYPING_TASK_TITLE = range(2)


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
    """Stores the task title and ends the conversation."""
    task_title = update.message.text
    technician_id = context.user_data.get("technician_id")
    technician_name = context.user_data.get("technician_name")

    request_id = context.user_data.get("request_id")
    task = sc.add_task(request_id, technician_name, task_title)
    task_id = task.get("task").get("id")
    link = f"https://support.agneko.com/ui/tasks?mode=detail&from=showAllTasks&module=request&taskId={task_id}&moduleId={request_id}"
    button = InlineKeyboardButton("Open in browser", url=link)
    keyboard = InlineKeyboardMarkup([[button]])
    
    # Here you would typically save the task to a database or send it to an API
    await update.message.reply_text(
        f"Task '{task_title}' assigned to {technician_name} (ID: {technician_id}).",
        reply_markup=keyboard
    )
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Task creation cancelled.")
    return ConversationHandler.END


# Create the conversation handler
task_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_task_button, pattern="add_task")],
    states={
        SELECTING_TECHNICIAN: [
            CallbackQueryHandler(technician_selected, pattern=r"^\d+$")
        ],
        TYPING_TASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_title_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
