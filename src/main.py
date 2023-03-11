""" Process a invoice uploaded in telegram, input extracted data in the system ("Sua Nota tem valor" app) and return execution status to requester

Author: Camila Caldas - 03/2023

"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pathlib import Path
from uuid import uuid4
from dotenv.main import load_dotenv
from datetime import datetime
import os
from gcp import upload_blob, detect_text_uri, upload_data_bigquery


# Google authentication using a service account file
load_dotenv('.env')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"

# Set up logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Answer in telegram after start bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    User_first_name = update.effective_chat.first_name
    first_response_text= f"Hi {User_first_name}, I'm a bot, please send your invoice!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=first_response_text)

# Document processing after upload in telegram
async def invoice_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
   # Inform user that document is going to be processed 
   User_first_name = update.effective_chat.first_name
   await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{User_first_name}, we receive your document and its going to be processed")

   # Download file locally 
   photo_file_id = update.message.photo[-1].file_id
   new_photo = await context.bot.get_file(photo_file_id)
   unique_id = uuid4()
   file_name = "Invoice_" + str(unique_id) + ".jpg" 
   local_path = Path(Path("main.py").parent, "Documents", file_name)
   await new_photo.download_to_drive(custom_path=local_path)
   
   # Send downloaded image to cloud storage
   bucket_name = "invoice-reader-documents"
   gcs_path = upload_blob(bucket_name=bucket_name,source_file_name=local_path,destination_blob_name=file_name)

   # Delete file from local folder
   os.remove(path=local_path)

   # Extract invoice number from image in storage bucket
   invoice_no = detect_text_uri(uri=gcs_path)
   
   # Stream data to big query
   extraction_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
   User_full_name = update.effective_chat.full_name
   upload_data_bigquery(invoice_number=invoice_no,extraction_date=extraction_datetime,file_name=file_name,requester=User_full_name) 

   #Return document processing results to user   
   if invoice_no !=None:
    bot_return_message = "Invoice number founded"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_return_message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=invoice_no)
   else:
    bot_return_message = "Invoice number not founded"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_return_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    #Answer in Telegram after start bot
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    #Process document
    receive_documents_handler = MessageHandler(filters.PHOTO, invoice_processing)
    application.add_handler(receive_documents_handler) 
    
    # Run the bot until the user presses Ctrl+C
    application.run_polling()
  