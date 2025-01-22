import os
import pdfplumber
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import Updater
from pdf_to_excel2 import process_pdf  # импортируем функцию для обработки PDF

# Токен вашего бота
TOKEN = '7939209383:AAGLF2H2ZqG8S_aTHOKbNOKw3NDUNbV2DU8'

# Создаем приложение
application = Application.builder().token(TOKEN).build()

# Функция для начала работы с ботом
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f'Привет, {user.mention_html()}! Отправь мне PDF файл, и я помогу тебе его обработать.',
    )

# Функция для обработки PDF
async def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)
    file_path = 'temp.pdf'
    await new_file.download_to_drive(file_path)

    # Обработка PDF через функцию из другого файла
    try:
        df = process_pdf(file_path)  # обработка PDF и создание DataFrame
        excel_file = "output.xlsx"
        df.to_excel(excel_file, index=False)  # Сохраняем в Excel
        await update.message.reply_document(document=open(excel_file, 'rb'))
        os.remove(file_path)  # удаляем временный PDF файл
        os.remove(excel_file)  # удаляем Excel файл
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Добавление обработчиков команд
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

# Запуск бота
application.run_polling()