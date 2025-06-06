from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton

import logging

import sc
import views
from decorators import log_query


logger = logging.getLogger(__name__)
PICK = 0


@log_query
async def filter_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        text="Choose a filter",
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(
                    text="All requests",
                    callback_data="filter_all_requests"
                ),
                InlineKeyboardButton(
                    text="My requests",
                    callback_data="filter_my_requests"
                ),
                InlineKeyboardButton(
                    text="All my groups",
                    callback_data="filter_all_my_groups"
                ),
                InlineKeyboardButton(
                    text="All tasks",
                    callback_data="filter_all_tasks"
                ),
                InlineKeyboardButton(
                    text="My tasks",
                    callback_data="filter_my_tasks"
                ),
            ]
        )
    )
    return PICK


@log_query
async def pick_filter_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Sets context filter option"""
    chosen_filter = update.callback_query.data
    await update.callback_query.answer(chosen_filter)
    if chosen_filter == "filter_all_requests":
        context.user_data["filter"] = "all_requests"
    elif chosen_filter == "filter_my_requests":
        context.user_data["filter"] = "my_requests"
    elif chosen_filter == "filter_all_my_groups":
        context.user_data["filter"] = "all_my_groups_requests"
    elif chosen_filter == "filter_all_tasks":
        context.user_data["filter"] = "all_tasks"
    elif chosen_filter == "filter_my_tasks":
        context.user_data["filter"] = "my_tasks"
    context.user_data["page"] = 0
    context.user_data["last"] = False
    await views.general_view(update, context)
    return ConversationHandler.END

filters_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            filter_action,
            "filter"
        )
    ],
    states={
        PICK: [
            CallbackQueryHandler(
                pick_filter_action
            )
        ]
    },
    fallbacks=[],
    per_message=False,
)

