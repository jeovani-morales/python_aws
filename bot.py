import boto3
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BUCKET_NAME = 'edutrack-demo-db'
DB_FILE = '/DB/EDUtrack_Test.db'

s3 = boto3.client('s3')

def download_db():
    try:
        s3.download_file(BUCKET_NAME, 'EDUtrack_Test.db', DB_FILE)
    except Exception as e:
        print(f"Error downloading database: {e}")

def upload_db():
    try:
        s3.upload_file(DB_FILE, BUCKET_NAME, 'EDUtrack_Test.db')
    except Exception as e:
        print(f"Error uploading database: {e}")

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello, World!')

def lambda_handler(event, context):
    # Obtener el token del bot desde las variables de entorno
    #telegram_token = os.environ.get('TOKEN')
    telegram_token = "6457745105:AAFzyEQvFydljxpUsS02YaQLazY3kHNV-H4"
    #mode = os.environ.get("mode")

    # Descargar la base de datos
    download_db()

    # Inicializar el bot de Telegram
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    # Configurar el comando /start
    dp.add_handler(CommandHandler("start", start))

    # Iniciar el bot
    updater.start_polling()
    updater.idle()

    # Subir la base de datos actualizada
    upload_db()