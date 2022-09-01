import os
import shutil

from dotenv import load_dotenv
import telebot
from telebot import types
import img2pdf
from loguru import logger

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('OK')
    bot.send_message(message.chat.id, "<b>Отправьте фотографии для конвертации и нажмите OK</b>\n"
                                      "(Отправляйте фотографии по отдельности, иначе они перемешаются)",
                     reply_markup=markup, parse_mode="HTML")


@bot.message_handler(content_types=['photo', 'document'])
def photo(message: types.Message):
    try:
        if not os.path.exists(str(message.from_user.id)):
            os.mkdir(str(message.from_user.id))

        file_info = bot.get_file(message.photo[-1].file_id)
        # print(file_info.file_path.split('/')[1])
        logger.success(f'Файл {file_info.file_path.split("/")[1]} добавлен. '
                       f'Отправитель: {message.from_user.first_name}')
        downloaded_file = bot.download_file(file_info.file_path)

        with open(f'{str(message.from_user.id)}/{file_info.file_path.split("/")[1]}', 'wb') as new_file:
            new_file.write(downloaded_file)
    except Exception as ex:
        logger.exception(ex)


@bot.message_handler(content_types=['text'])
def text_ok(message: types.Message):
    try:
        if message.text.lower() == 'ok' or message.text.lower() == 'ок':
            markup_remove = types.ReplyKeyboardRemove()

            if os.path.exists(f'{str(message.from_user.id)}'):
                img_list = [f'{str(message.from_user.id)}/{img}' for img in
                            os.listdir(f'{str(message.from_user.id)}')]

                with open(f'{str(message.from_user.id)}.pdf', 'wb') as file:
                    file.write(img2pdf.convert(img_list))

                with open(f'{str(message.from_user.id)}.pdf', 'rb') as file:
                    bot.send_document(message.chat.id, file, reply_markup=markup_remove)
                    logger.success(f'Файл {str(message.from_user.id)}.pdf отправлен. '
                                   f'Получатель: {message.from_user.first_name}')

            if os.path.exists(directory := str(message.from_user.id)):
                shutil.rmtree(directory)

            if os.path.exists(file := f'{str(message.from_user.id)}.pdf'):
                os.remove(file)
    except Exception as ex:
        logger.exception(ex)


if __name__ == '__main__':
    bot.infinity_polling()
