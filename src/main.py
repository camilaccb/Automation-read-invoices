import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pathlib import Path
from uuid import uuid4
from dotenv.main import load_dotenv
import os
import re

# Authentication in Telegram API and Google Vision

load_dotenv('.env')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:     
        print('\n"{}"'.format(text.description))
        reg_pattern =  '\d{44}|(\d{4}\s){11}'
        texto_encontrado = re.search(reg_pattern, text.description)

        if texto_encontrado != None:
            invoice_no = texto_encontrado.group()
            bot_return_message = f'Invoice number founded {invoice_no}'
            break
        else:
            bot_return_message = "Invoice number was not founded"
    
    print(bot_return_message)
    return bot_return_message

        #vertices = (['({},{})'.format(vertex.x, vertex.y)
                    #for vertex in text.bounding_poly.vertices])

        #print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, send your invoice!")

async def invoice_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   photo_file_id = update.message.photo[-1].file_id
   new_photo = await context.bot.get_file(photo_file_id)
   unique_id = uuid4()
   file_name = "Invoice_" + str(unique_id) + ".jpg"    # sugestão marcação timestamp
   current_path = Path(Path("main.py").parent, "Documents", file_name) # ajustar de acordo com teste.py
   await new_photo.download_to_drive(custom_path=current_path)
   await context.bot.send_message(chat_id=update.effective_chat.id, text="We receive your document and its going to be processed")
   bot_return_message = detect_text(path=current_path) # Formatar melhor a mensagem de saida
   await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_return_message)


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
  