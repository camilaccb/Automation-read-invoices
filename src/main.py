import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pathlib import Path
from uuid import uuid4
from dotenv.main import load_dotenv
import os

load_dotenv('.env')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, send your invoice!")

async def invoice_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   photo_file_id = update.message.photo[-1].file_id
   new_photo = await context.bot.get_file(photo_file_id)
   unique_id = uuid4()
   file_name = "Invoice_" + str(unique_id) + ".jpg"
   current_path = Path(Path("main.py").parent, "Documents", file_name)
   await new_photo.download_to_drive(custom_path=current_path)
   await context.bot.send_message(chat_id=update.effective_chat.id, text="We receive your Invoice and its going to be processed")
 

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    #Answer in Telegram
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    #Download photo file
    receive_documents_handler = MessageHandler(filters.PHOTO,invoice_received)
    application.add_handler(receive_documents_handler) 
    
    # Run the bot until the user presses Ctrl+C
    application.run_polling()

  