import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pathlib import Path
from uuid import uuid4
from dotenv.main import load_dotenv
from datetime import datetime
import os
import re

# Authentication in Telegram API and Google Vision

load_dotenv('.env')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    #bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

    path_gcs = f"gs://{bucket_name}/{destination_blob_name}"
    return path_gcs

def detect_text_uri(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        reg_pattern =  '\d{44}|(\d{4}\s){11}'
        texto_encontrado = re.search(reg_pattern, text.description)

        if texto_encontrado != None:
            invoice_no = texto_encontrado.group().replace(" ", "")
            break
    
    print(invoice_no)
    return invoice_no

        #vertices = (['({},{})'.format(vertex.x, vertex.y)
                    #for vertex in text.bounding_poly.vertices])

        #print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))


def upload_data_bigquery(invoice_number, extraction_date, file_name, requester):

    from google.cloud import bigquery

    # Construct a BigQuery client object.
    client = bigquery.Client()

    table_id = "invoice-reader-374817.invoice_data.EXTRACTED_DATA"

    rows_to_insert = [
        {"Extraction_date": extraction_date, "Requester": requester, "Invoice_number": invoice_number, "File":file_name}
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, send your invoice!")

async def invoice_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   photo_file_id = update.message.photo[-1].file_id
   new_photo = await context.bot.get_file(photo_file_id)
   unique_id = uuid4()
   file_name = "Invoice_" + str(unique_id) + ".jpg" 
   current_path = Path(Path("main.py").parent, "Documents", file_name) # ajustar de acordo com teste.py
   await new_photo.download_to_drive(custom_path=current_path)
   path_gcs = upload_blob(bucket_name="invoice-reader-documents",source_file_name=current_path,destination_blob_name=file_name)
   await context.bot.send_message(chat_id=update.effective_chat.id, text="We receive your document and its going to be processed")
   invoice_no = detect_text_uri(uri=path_gcs)
   
   
   if invoice_no !=None:
    bot_return_message = "Invoice number founded"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_return_message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=invoice_no)
   else:
    bot_return_message = "Invoice number not founded"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_return_message)

   extraction_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
   upload_data_bigquery(invoice_number=invoice_no,extraction_date=extraction_datetime,file_name=file_name,requester="Camila") 
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    #Answer in Telegram
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    #Download photo file and send to Google Cloud Vision API
    receive_documents_handler = MessageHandler(filters.PHOTO,invoice_received)
    application.add_handler(receive_documents_handler) 
    
    # Run the bot until the user presses Ctrl+C
    application.run_polling()
  