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
from task import task_handler


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


def create_request_keyboard(request):
    keyboard = []
    keyboard.append([InlineKeyboardButton("Description", callback_data=f"description")])
        #TODO: add quick actions
        #TODO: add assign dialog
        #TODO: add reply option
        #TODO: add edit menu
        #TODO: add add note dialog
        #TODO: add menu
            #TODO: add Properties
            #TODO: add Resolution
            #TODO: add Time entry
            #TODO: add Conversations
            #TODO: add History
            #TODO: add Tasks
            #TODO: add Approvals
    request_conversations = sc.get_request_conversation(request.id)
    for conversation in request_conversations:
        keyboard.append([InlineKeyboardButton(f"{conversation.from_.name}  {conversation.sent_time.display_value}", callback_data=f"conversation_{conversation.id}")])
    
    keyboard.append([InlineKeyboardButton("Add task" , callback_data="add_task")])
    keyboard.append([InlineKeyboardButton("<- Back", callback_data="back"),
        InlineKeyboardButton(f"Open #{request.id} in browser", url=request.url)])
    return InlineKeyboardMarkup(keyboard)

        
def construct_request_text(request):
    text = f"*{request.subject}*\n"
    if request.status:
        text += f"Status: {request.status.name}\n"
    if request.technician:
        text += f"Technician: {request.technician.name}\n"
    if request.priority:
        text += f"Priority: {request.priority.name}\n"
    #TODO: add due date, contract & account
    if request.description:
        description = request.description
        description = description.replace("<br />", "\n")
        soup = BeautifulSoup(description, 'html.parser')
        description = soup.get_text()
        text += f"\n{description}"
    return text


@log_message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await views.index(update, context)


@log_query
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(query.data)
    request_id = query.data.split("_")[1]
    context.user_data["request_id"] = request_id
    request = sc.show(request_id)
    request_text = construct_request_text(request)
    request_keyboard = create_request_keyboard(request)
    await query.edit_message_text(
        text=request_text,
        reply_markup=request_keyboard,
        parse_mode="Markdown"
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
    request = sc.show(request_id)
    request_keyboard = create_request_keyboard(request)
    notification = sc.view_notification(request_id, conversation_id)
    await query.edit_message_text(
        text=notification.text[:2048],
        reply_markup=request_keyboard,
    )


@log_query
async def description_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(query.data)
    request_id = context.user_data.get("request_id")
    request = sc.show(request_id)
    request_keyboard = create_request_keyboard(request)
    request_texts = construct_request_text(request)
    await query.edit_message_text(
        text=request_texts,
        reply_markup=request_keyboard,
        parse_mode= "Markdown"
    )


def main():
    application = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(button, pattern="request_")
    back_button_handler = CallbackQueryHandler(back_button, pattern="back")
    refresh_button_handler = CallbackQueryHandler(refresh_button, pattern="refresh")
    next_button_handler = CallbackQueryHandler(next_button, pattern="next")
    previous_button_handler = CallbackQueryHandler(previous_button, pattern="previous")
    conversation_handler = CallbackQueryHandler(conversation_button, pattern="conversation_")
    description_button_handler = CallbackQueryHandler(description_button, pattern="description")
    
    # application.add_handler(echo_handler)
    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(back_button_handler)
    application.add_handler(filters_handler)
    application.add_handler(refresh_button_handler)
    application.add_handler(next_button_handler)
    application.add_handler(previous_button_handler)
    application.add_handler(conversation_handler)
    application.add_handler(description_button_handler)
    application.add_handler(task_handler)
    
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