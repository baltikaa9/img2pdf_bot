import os
import shutil

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram import types
import img2pdf

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)

username_exist = {}


@dp.message_handler(commands='start')
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('OK')
    await bot.send_message(message.chat.id, "<b>Отправьте фотографии для конвертации и нажмите OK</b>",
                           reply_markup=markup, parse_mode="HTML")


@dp.message_handler(content_types=['photo', 'document'])
async def photo(message: types.Message):
    global username_exist

    if message.from_user.username is not None:
        if not os.path.exists(message.from_user.username):
            os.mkdir(message.from_user.username)
        await message.photo[-1].download(destination_dir=message.from_user.username)

        username_exist[str(message.from_user.id)] = True
    else:
        if not os.path.exists(str(message.from_user.id)):
            os.mkdir(str(message.from_user.id))
        await message.photo[-1].download(destination_dir=str(message.from_user.id))

        username_exist[str(message.from_user.id)] = False


@dp.message_handler(lambda message: message.text and 'ok' or 'ок' in message.text.lower())
async def text_ok(message: types.Message):
    markup_remove = types.ReplyKeyboardRemove()
    path = {}
    try:
        path[str(message.from_user.id)] = message.from_user.username if username_exist[str(message.from_user.id)] else str(message.from_user.id)

        if os.path.exists(f'{path[str(message.from_user.id)]}/photos'):
            img_list = [f'{path[str(message.from_user.id)]}/photos/{img}' for img in
                        os.listdir(f'{path[str(message.from_user.id)]}/photos')]

            with open(f'{path[str(message.from_user.id)]}.pdf', 'wb') as file:
                file.write(img2pdf.convert(img_list))

            with open(f'{path[str(message.from_user.id)]}.pdf', 'rb') as file:
                await bot.send_document(message.chat.id, file, reply_markup=markup_remove)

        if os.path.exists(directory := path[str(message.from_user.id)]):
            shutil.rmtree(directory)

        if os.path.exists(file := f'{path[str(message.from_user.id)]}.pdf'):
            os.remove(file)

        username_exist.pop(str(message.from_user.id))
    except KeyError:
        path = None


if __name__ == '__main__':
    executor.start_polling(dp)
