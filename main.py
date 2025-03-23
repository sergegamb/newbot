import logging
import os
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
import sc
from filters import filters_handler
from decorators import log_message, log_query
from views import index



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
    keyboard = [
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
        InlineKeyboardButton(f"Open #{request.id} in browser", url=request.url),
        InlineKeyboardButton("<- Back", callback_data="back")]
    return InlineKeyboardMarkup.from_column(keyboard)

        
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
    await index(update, context)


@log_query
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(query.data)
    request_id = query.data.split("_")[1]
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
    await index(update, context)
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(button, pattern="request_")
    back_button_handler = CallbackQueryHandler(back_button, pattern="back")
    
    # application.add_handler(echo_handler)
    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(back_button_handler)
    application.add_handler(filters_handler)
    
    application.run_polling()
