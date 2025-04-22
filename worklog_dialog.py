# worklog_dialog.py

import time
import logging
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
TYPING_WORKLOG_DESCRIPTION, TYPING_WORKLOG_HOURS, TYPING_WORKLOG_MINUTES = range(3)


@log_query
async def add_worklog_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the worklog creation process."""
    await update.callback_query.edit_message_text(
        "Please send the worklog description:"
    )
    return TYPING_WORKLOG_DESCRIPTION


@log_message
async def worklog_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the worklog description and asks for the hours."""
    worklog_description = update.message.text
    context.user_data["worklog_description"] = worklog_description
    await update.message.reply_text(
        text=f"Worklog description set to '{worklog_description}'. Now, please send the hours spent."
    )
    return TYPING_WORKLOG_HOURS


@log_message
async def worklog_hours_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the hours and asks for the minutes."""
    try:
        worklog_hours = int(update.message.text)
        context.user_data["worklog_hours"] = worklog_hours
        await update.message.reply_text(
            text=f"Hours set to '{worklog_hours}'. Now, please send the minutes spent."
        )
        return TYPING_WORKLOG_MINUTES
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a number of hours.")
        return TYPING_WORKLOG_HOURS


@log_message
async def worklog_minutes_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the minutes and creates the worklog."""
    try:
        worklog_minutes = int(update.message.text)
        context.user_data["worklog_minutes"] = worklog_minutes

        worklog_description = context.user_data.get("worklog_description")
        worklog_hours = context.user_data.get("worklog_hours")
        worklog_minutes = context.user_data.get("worklog_minutes")
        request_id = context.user_data.get("request_id")
        owner = TECHNICIANS.get(update.effective_chat.id)

        worklog = sc.add_worklog(request_id, owner, worklog_description, worklog_hours, worklog_minutes)

        keyboard = [InlineKeyboardButton("Back", callback_data=f"show_worklogs_{request_id}")]
        await update.message.reply_text(
            f"Worklog added: {worklog_description} - {worklog_hours}:{worklog_minutes}",
            reply_markup=InlineKeyboardMarkup([keyboard]),
        )
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a number of minutes.")
        return TYPING_WORKLOG_MINUTES


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Worklog creation cancelled.")
    return ConversationHandler.END


# Create the conversation handler
worklog_add_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_worklog_button, pattern="add_worklog")],
    states={
        TYPING_WORKLOG_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, worklog_description_received)],
        TYPING_WORKLOG_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, worklog_hours_received)],
        TYPING_WORKLOG_MINUTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, worklog_minutes_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
