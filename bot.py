import os
import pdfplumber
import pandas as pd
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Функция для извлечения данных из PDF
def extract_relevant_data_from_pdf(pdf_file_path):
    results = []

    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    price_candidates = [cell for cell in row if re.search(r'\d{2,}', str(cell).replace(" ", ""))]
                    if price_candidates:
                        price_per_unit = price_candidates[-1]
                        quantity = next((cell for cell in row if str(cell).isdigit()), None)
                        unit = next((cell for cell in row if isinstance(cell, str) and len(cell) <= 3), None)
                        name = next((cell for cell in row if isinstance(cell, str) and len(cell) > 3), None)

                        total = None
                        if quantity and price_per_unit:
                            try:
                                total = int(str(quantity).replace(" ", "")) * float(str(price_per_unit).replace(" ", "").replace(",", "."))
                            except ValueError:
                                total = None

                        if name and quantity and price_per_unit:
                            results.append({
                                "Наименование": name,
                                "Кол-во": quantity,
                                "Ед. изм.": unit,
                                "Цена за ед.": price_per_unit,
                                "Итого": total
                            })

    df = pd.DataFrame(results)
    df = df.dropna(subset=["Наименование", "Кол-во", "Цена за ед."])

    # Сохраняем данные в формате CSV или возвращаем таблицу как строку
    return df.to_string(index=False)

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    keyboard = [[{"text": "Загрузить ПДФ"}]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("Добро пожаловать! Нажмите кнопку ниже для загрузки PDF.", reply_markup=reply_markup)

# Обработчик получения файла PDF
def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    file_path = f"./{file.file_name}"

    # Скачиваем файл на сервер
    file.download(file_path)

    # Обрабатываем PDF и извлекаем данные
    result = extract_relevant_data_from_pdf(file_path)

    # Отправляем результат обратно пользователю
    update.message.reply_text("Вот обработанные данные из вашего PDF:\n\n" + result)

# Основная функция для запуска бота
def main():
    updater = Updater("7939209383:AAGLF2H2ZqG8S_aTHOKbNOKw3NDUNbV2DU8", use_context=True)  # Добавлен ваш токен
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_pdf))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()