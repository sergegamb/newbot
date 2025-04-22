import logging
import os
import sys
import urllib3
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
    CallbackQueryHandler,
)
from bs4 import BeautifulSoup
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import sc
from filters import filters_handler
from decorators import log_message, log_query
import views
from task import task_add_handler, task_description_handler
from worklog_dialog import worklog_add_handler


# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get the httpx logger and set its level to WARNING or higher
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)  # Or logging.ERROR if you want to suppress even more


@log_message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await views.index(update, context)


@log_query
async def request_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(query.data)
    request_id = query.data.split("_")[1]
    context.user_data["request_id"] = request_id
    request = sc.get_request(request_id)
    await query.edit_message_text(
        text=request.text,
        reply_markup=request.keyboard,
        parse_mode="Markdown"
    )

@log_query
async def show_conversations_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    request_id = query.data.split("_")[2]
    request = sc.get_request(request_id)
    await query.edit_message_text(
        text="Conversations:",
        reply_markup=request.conversations_keyboard,
    )
    
@log_query
async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    await views.general_view(update, context)
    
@log_query
async def refresh_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    await views.refresh(update, context)


@log_query
async def next_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    page = context.user_data.get("page", 0)
    last = context.user_data.get("last", False)
    if not last:
        context.user_data["page"] = page + 1
    await views.general_view(update, context)


@log_query
async def previous_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    page = context.user_data.get("page", 0)
    context.user_data["page"] = max(page - 1, 0)
    await views.general_view(update, context)


@log_query
async def conversation_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    conversation_id = query.data.split("_")[1]
    request_id = context.user_data.get("request_id")
    request = sc.get_request(request_id)
    notification = sc.view_notification(request_id, conversation_id)
    await query.edit_message_text(
        text=notification.text[:2048],
        reply_markup=request.conversations_keyboard,
    )


@log_query
async def description_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    request_id = context.user_data.get("request_id")
    request = sc.get_request(request_id)
    await query.edit_message_text(
        text=request.texts,
        reply_markup=request.keyboard,
        parse_mode= "Markdown"
    )


@log_query
async def request_task_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    task_id = query.data.split("_")[2]
    request_id = query.data.split("_")[1]
    task = sc.get_request_task(request_id, task_id)
    context.user_data["task_id"] = task_id
    context.user_data["request_id"] = request_id
    await query.edit_message_text(
        text=task.text,
        reply_markup=task.keyboard,
        parse_mode="Markdown"
    )


@log_query
async def show_worklogs_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    request_id = query.data.split("_")[2]
    request = sc.get_request(request_id)
    await query.edit_message_text(
        text="Worklogs:",
        reply_markup=request.worklogs_keyboard,
    )

@log_query
async def worklog_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    worklog_id = query.data.split("_")[1]
    request_id = context.user_data.get("request_id")
    worklogs = sc.list_request_worklogs(request_id)
    worklog = None
    for w in worklogs:
        if w.id == int(worklog_id):
            worklog = w
            break
    if worklog:
        keyboard = [InlineKeyboardButton("Back", callback_data=f"show_worklogs_{request_id}")]
        await query.edit_message_text(
            text=worklog.text,
            reply_markup=InlineKeyboardMarkup([keyboard]),
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            text="Worklog not found.",
        )


def main():
    application = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(request_button, pattern="request_")
    show_conversations_handler = CallbackQueryHandler(show_conversations_button, pattern="show_conversations_")
    back_button_handler = CallbackQueryHandler(back_button, pattern="back")
    refresh_button_handler = CallbackQueryHandler(refresh_button, pattern="refresh")
    next_button_handler = CallbackQueryHandler(next_button, pattern="next")
    previous_button_handler = CallbackQueryHandler(previous_button, pattern="previous")
    conversation_handler = CallbackQueryHandler(conversation_button, pattern="conversation_")
    description_button_handler = CallbackQueryHandler(description_button, pattern="description")
    request_task_button_handler = CallbackQueryHandler(request_task_button, pattern="requesttask_")
    show_worklogs_handler = CallbackQueryHandler(show_worklogs_button, pattern="show_worklogs_")
    worklog_handler = CallbackQueryHandler(worklog_button, pattern="worklog_")
    
    # application.add_handler(echo_handler)
    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(show_conversations_handler)
    application.add_handler(back_button_handler)
    application.add_handler(filters_handler)
    application.add_handler(refresh_button_handler)
    application.add_handler(next_button_handler)
    application.add_handler(previous_button_handler)
    application.add_handler(conversation_handler)
    application.add_handler(description_button_handler)
    application.add_handler(task_add_handler)
    application.add_handler(request_task_button_handler)
    application.add_handler(task_description_handler)
    application.add_handler(show_worklogs_handler)
    application.add_handler(worklog_add_handler)
    application.add_handler(worklog_handler)
    
    application.run_polling()


class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
    
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\nFile changed: {event.src_path}. Restarting...")
            self.restart_script()
    
    def restart_script(self):
        try:
            # Stop the current observer
            observer.stop()
            observer.join()
        except:
            pass
        
        # Restart the script
        os.execv(sys.executable, ['python'] + [self.script_path])


if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    
    event_handler = RestartHandler(script_path)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        main()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()