import asyncio
import random
from datetime import datetime, timedelta
import aiosqlite

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ---------------- КОНФИГУРАЦИЯ ----------------
# Вставьте сюда ваш токен, который сработал в test.py
BOT_TOKEN = "8909119386:AAGK9hTizA7n1pvrrwLmR2ew63Nf7Hh_VZg"

COOLDOWN_MINUTES = 120  # Кулдаун 2 часа

DEFAULT_IMG = "https://images.unsplash.com/photo-1598971861713-54ad16a7e72e"

# База из 50 самокатов
SCOOTER_DATABASE = [
    # Обычные (Common) - 20 шт.
    {"id": 1, "name": "Ninebot KickScooter ES1", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4},
    {"id": 2, "name": "Xiaomi Electric Scooter Essential", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4},
    {"id": 3, "name": "Ninebot KickScooter E22", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4},
    {"id": 4, "name": "Kugoo Kirin Mini 2", "rarity": "⚪️ Обычный", "speed": 25, "weight": 4},
    {"id": 5, "name": "Acer Series 1", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 6, "name": "Ninebot KickScooter E25", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 7, "name": "Xiaomi Electric Scooter 3 Lite", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 8, "name": "Ninebot KickScooter D18W", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 9, "name": "Joyor A3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 10, "name": "Hiper Slim", "rarity": "⚪️ Обычный", "speed": 22, "weight": 3},
    {"id": 11, "name": "Halten Tony", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 12, "name": "Kugoo S1", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 13, "name": "Okai Neon Lite", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 14, "name": "Ninebot KickScooter F20A", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 15, "name": "Xiaomi Mi Electric Scooter 1S", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 16, "name": "Acer ES Series 3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 17, "name": "Kugoo Kirin S3 Pro", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 18, "name": "GT Sonic", "rarity": "⚪️ Обычный", "speed": 22, "weight": 3},
    {"id": 19, "name": "Ninebot KickScooter E2 Plus", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3},
    {"id": 20, "name": "Xiaomi Electric Scooter 4 Go", "rarity": "⚪️ Обычный", "speed": 20, "weight": 3},

    # Редкие (Rare) - 15 шт.
    {"id": 21, "name": "Xiaomi Mi Electric Scooter Pro 2", "rarity": "🔵 Редкий", "speed": 25, "weight": 2},
    {"id": 22, "name": "Ninebot KickScooter Max G30LP", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},
    {"id": 23, "name": "Ninebot KickScooter Max G30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},
    {"id": 24, "name": "Kugoo M4 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2},
    {"id": 25, "name": "Kugoo Kirin G2 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2},
    {"id": 26, "name": "Ninebot KickScooter F30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},
    {"id": 27, "name": "Ninebot KickScooter F40", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},
    {"id": 28, "name": "Xiaomi Electric Scooter 4 Pro", "rarity": "🔵 Редкий", "speed": 25, "weight": 2},
    {"id": 29, "name": "Joyor Y8-S", "rarity": "🔵 Редкий", "speed": 35, "weight": 2},
    {"id": 30, "name": "Halten Cross V3", "rarity": "🔵 Редкий", "speed": 40, "weight": 2},
    {"id": 31, "name": "Ultron T103", "rarity": "🔵 Редкий", "speed": 45, "weight": 2},
    {"id": 32, "name": "Speedway Mini 4 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2},
    {"id": 33, "name": "Ninebot KickScooter Max G2", "rarity": "🔵 Редкий", "speed": 35, "weight": 2},
    {"id": 34, "name": "Acer ES Series 5", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},
    {"id": 35, "name": "Okai Neon Pro", "rarity": "🔵 Редкий", "speed": 30, "weight": 2},

    # Эпические (Epic) - 10 шт.
    {"id": 36, "name": "KuKirin G3 Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1},
    {"id": 37, "name": "Kugoo Kirin G4", "rarity": "🟣 Эпический", "speed": 70, "weight": 1},
    {"id": 38, "name": "Ultron T118", "rarity": "🟣 Эпический", "speed": 85, "weight": 1},
    {"id": 39, "name": "Vsett 9+", "rarity": "🟣 Эпический", "speed": 55, "weight": 1},
    {"id": 40, "name": "Vsett 10+", "rarity": "🟣 Эпический", "speed": 80, "weight": 1},
    {"id": 41, "name": "Dualtron Spider II", "rarity": "🟣 Эпический", "speed": 70, "weight": 1},
    {"id": 42, "name": "Dualtron Victor", "rarity": "🟣 Эпический", "speed": 80, "weight": 1},
    {"id": 43, "name": "Kaabo Mantis 10 Pro", "rarity": "🟣 Эпический", "speed": 60, "weight": 1},
    {"id": 44, "name": "Kaabo Wolf Warrior X", "rarity": "🟣 Эпический", "speed": 70, "weight": 1},
    {"id": 45, "name": "Nanrobot D4+ 3.0", "rarity": "🟣 Эпический", "speed": 65, "weight": 1},

    # Легендарные (Legendary) - 5 шт.
    {"id": 46, "name": "Dualtron Thunder 3", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3},
    {"id": 47, "name": "Dualtron X-Limited", "rarity": "🟡 Легендарный", "speed": 110, "weight": 0.2},
    {"id": 48, "name": "Kaabo Wolf King GT Pro", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3},
    {"id": 49, "name": "Nami Burn-E 2 Max", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2},
    {"id": 50, "name": "Rion Curve Tron", "rarity": "🟡 Легендарный", "speed": 125, "weight": 0.1}
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- БАЗА ДАННЫХ ----------------
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                last_drop TEXT,
                registered_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scooter_id INTEGER,
                model_name TEXT,
                rarity TEXT,
                speed INTEGER
            )
        """)
        await db.commit()

# ---------------- КЛАВИАТУРЫ ----------------
def get_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Выбить самокат", callback_data="action_get")
    kb.button(text="🛵 Мой гараж", callback_data="action_garage")
    kb.button(text="👤 Мой профиль", callback_data="action_profile")
    kb.adjust(1)
    return kb.as_markup()

def get_back_btn():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    return kb.as_markup()

# ---------------- ХЕНДЛЕРЫ ----------------
@dp.message(CommandStart())
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Rider"
    now_iso = datetime.now().isoformat()

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, registered_at) VALUES (?, ?, ?)",
            (user_id, username, now_iso)
        )
        await db.commit()

    text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в E-ScooterCards!\n"
        "В игре доступно 50 моделей электросамокатов.\n"
        "Испытай удачу и собери самый мощный гараж!"
    )
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "action_menu")
async def cb_menu(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    text = "🛴 Главное меню. Выберите действие:"
    await callback.message.answer(text, reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(F.data == "action_get")
@dp.message(Command("get"))
async def handle_drop(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    now = datetime.now()
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT last_drop, registered_at FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        reg_time = row[1] if row and row[1] else now.isoformat()

        if row and row[0]:
            last_drop = datetime.fromisoformat(row[0])
            cooldown_end = last_drop + timedelta(minutes=COOLDOWN_MINUTES)
            if now < cooldown_end:
                minutes_left = int((cooldown_end - now).total_seconds() // 60)
                if isinstance(event, types.CallbackQuery):
                    await event.answer(f"⏳ Рано! Жди ещё {minutes_left} мин.", show_alert=True)
                else:
                    await message.answer(f"⏳ Рано! Следующий самокат доступен через {minutes_left} мин.")
                return

        weights = [s["weight"] for s in SCOOTER_DATABASE]
        dropped = random.choices(SCOOTER_DATABASE, weights=weights, k=1)[0]

        await db.execute(
            """INSERT INTO users (user_id, username, last_drop, registered_at) 
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET 
               last_drop=excluded.last_drop, 
               username=excluded.username""",
            (user_id, event.from_user.username or "Rider", now.isoformat(), reg_time)
        )
        await db.execute(
            """INSERT INTO inventory (user_id, scooter_id, model_name, rarity, speed) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, dropped["id"], dropped["name"], dropped["rarity"], dropped["speed"])
        )
        await db.commit()

    card_text = (
        f"🎉 ВАМ ВЫПАЛ НОВЫЙ САМОКАТ!\n\n"
        f"🏷 Модель: {dropped['name']}\n"
        f"⭐ Редкость: {dropped['rarity']}\n"
        f"⚡ Макс. скорость: {dropped['speed']} км/ч\n\n"
        f"Самокат успешно добавлен в гараж!"
    )

    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(card_text, reply_markup=get_back_btn())
        await event.answer()
    else:
        await message.answer(card_text)

@dp.callback_query(F.data == "action_garage")
@dp.message(Command("garage"))
async def handle_garage(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT model_name, rarity, speed FROM inventory WHERE user_id = ?", (user_id,))
        scooters = await cursor.fetchall()
        await cursor.close()

    if not scooters:
        text = "🛵 Ваш гараж пуст.\nНажмите кнопку «Выбить самокат», чтобы получить первый транспорт!"
    else:
        recent = scooters[-15:]
        text = f"🛵 Ваш гараж (Всего: {len(scooters)} шт.):\n\n"
        for idx, (name, rarity, speed) in enumerate(recent, 1):
            text += f"{idx}. {rarity} {name} — {speed} км/ч\n"
        if len(scooters) > 15:
            text += f"\n...и еще {len(scooters) - 15} самокатов"

    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=get_back_btn())
        await event.answer()
    else:
        await message.answer(text)

@dp.callback_query(F.data == "action_profile")
@dp.message(Command("profile"))
async def handle_profile(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    now = datetime.now()

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT registered_at FROM users WHERE user_id = ?", (user_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        cursor = await db.execute("SELECT model_name, rarity, speed FROM inventory WHERE user_id = ?", (user_id,))
        inventory = await cursor.fetchall()
        await cursor.close()

    if user_row and user_row[0]:
        reg_date = datetime.fromisoformat(user_row[0])
        days_in_bot = (now - reg_date).days
    else:
        days_in_bot = 0

    total_scooters = len(inventory)
    unique_models = len(set(item[0] for item in inventory))
    
    if total_scooters > 0:
        fastest_scooter = max(inventory, key=lambda x: x[2])
        fastest_text = f"{fastest_scooter[0]} ({fastest_scooter[2]} км/ч)"
        
        rarities_count = {}
        for item in inventory:
            r = item[1]
            rarities_count[r] = rarities_count.get(r, 0) + 1
        
        rarity_lines = "\n".join([f"  • {r}: {count} шт." for r, count in rarities_count.items()])
    else:
        fastest_text = "Нет самокатов"
        rarity_lines = "  • Гараж пуст"

    user_name = event.from_user.full_name

    profile_text = (
        f"👤 Профиль райдера: {user_name}\n"
        f"🆔 ID: {user_id}\n\n"
        f"📅 В игре: {days_in_bot} дн.\n"
        f"🛴 Всего самокатов: {total_scooters} шт. (Уникальных: {unique_models}/50)\n"
        f"⚡ Самый быстрый: {fastest_text}\n\n"
        f"📊 Коллекция по редкостям:\n{rarity_lines}"
    )

    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(profile_text, reply_markup=get_back_btn())
        await event.answer()
    else:
        await message.answer(profile_text)

# ---------------- ТОЧКА ВХОДА ----------------
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"🚀 Бот @{me.username} успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())