import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
===== НАСТРОЙКИ =====
TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"  # 8909119386:AAGK9hTizA7n1pvrrwLmR2ew63Nf7Hh_VZg
logging.basicConfig(level=logging.INFO)
===== ИНИЦИАЛИЗАЦИЯ =====
bot = Bot(token=TOKEN)
dp = Dispatcher()
Создаём папку для загрузок
UPLOAD_DIR = "downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
===== КОМАНДЫ =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Отправь мне любой файл (фото, видео, документ), и я сохраню его."
    )
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📌 Как пользоваться:\n"
        "Просто отправь мне файл\n"
        "Я принимаю фото, видео и документы"
    )
===== ОБРАБОТЧИКИ ФАЙЛОВ =====
Документы
@dp.message(lambda msg: msg.document)
async def handle_document(message: types.Message):
    file = message.document
    await download_file(message, file.file_id, file.file_name)
Фото (берём самое качественное)
@dp.message(lambda msg: msg.photo)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    file_name = f"photo_{message.from_user.id}_{photo.file_id[:8]}.jpg"
    await download_file(message, photo.file_id, file_name)
Видео
@dp.message(lambda msg: msg.video)
async def handle_video(message: types.Message):
    video = message.video
    file_name = video.file_name or f"video_{message.from_user.id}.mp4"
    await download_file(message, video.file_id, file_name)
===== ФУНКЦИЯ СКАЧИВАНИЯ =====
async def download_file(message: types.Message, file_id: str, file_name: str):
    try:
        # Получаем файл от Telegram
        file = await bot.get_file(file_id)
        file_path = os.path.join(UPLOAD_DIR, file_name)
    # Скачиваем
    await bot.download_file(file.file_path, file_path)

    await message.answer(f"✅ Файл сохранён: {file_name}")
    print(f"Скачан файл: {file_name} от {message.from_user.id}")

except Exception as e:
    await message.answer(f"❌ Ошибка: {str(e)}")

===== ЗАПУСК =====
async def main():
    print("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)
if name == "main":
    asyncio.run(main())