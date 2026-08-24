import asyncio
import random
from datetime import datetime, timedelta
import aiosqlite

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ---------------- КОНФИГУРАЦИЯ ----------------
# Замените на ваш актуальный токен от BotFather
BOT_TOKEN = "8909119386:AAGK9hTizA7n1pvrrwLmR2ew63Nf7Hh_VZg"

COOLDOWN_MINUTES = 120  # Кулдаун 2 часа

# Полная база данных самокатов
SCOOTER_DATABASE = [
    # --- Обычные (Common) ---
    {"id": 1, "name": "Ninebot KickScooter ES1", "rarity": "⚪ Обычный", "speed": 20, "weight": 4, "price": 5000},
    {"id": 2, "name": "Xiaomi Electric Scooter Essential", "rarity": "⚪ Обычный", "speed": 20, "weight": 4, "price": 5500},
    {"id": 3, "name": "Ninebot KickScooter E22", "rarity": "⚪ Обычный", "speed": 20, "weight": 4, "price": 6000},
    {"id": 4, "name": "Kugoo Kirin Mini 2", "rarity": "⚪ Обычный", "speed": 25, "weight": 4, "price": 6500},
    {"id": 5, "name": "Acer Series 1", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 7000},
    {"id": 6, "name": "Ninebot KickScooter E25", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 7200},
    {"id": 7, "name": "Xiaomi Electric Scooter 3 Lite", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 7500},
    {"id": 8, "name": "Ninebot KickScooter D18W", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 7800},
    {"id": 9, "name": "Joyor A3", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 8000},
    {"id": 10, "name": "Hiper Slim", "rarity": "⚪ Обычный", "speed": 22, "weight": 3, "price": 8200},
    {"id": 11, "name": "Halten Tony", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 8500},
    {"id": 12, "name": "Kugoo S1", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 8700},
    {"id": 13, "name": "Okai Neon Lite", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 9000},
    {"id": 14, "name": "Ninebot KickScooter F20A", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 9200},
    {"id": 15, "name": "Xiaomi Mi Electric Scooter 1S", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 9500},
    {"id": 16, "name": "Acer ES Series 3", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 9700},
    {"id": 17, "name": "Kugoo Kirin S3 Pro", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 10000},
    {"id": 18, "name": "GT Sonic", "rarity": "⚪ Обычный", "speed": 22, "weight": 3, "price": 10200},
    {"id": 19, "name": "Ninebot KickScooter E2 Plus", "rarity": "⚪ Обычный", "speed": 25, "weight": 3, "price": 10500},
    {"id": 20, "name": "Xiaomi Electric Scooter 4 Go", "rarity": "⚪ Обычный", "speed": 20, "weight": 3, "price": 11000},

    # --- Редкие (Rare) ---
    {"id": 21, "name": "Xiaomi Mi Electric Scooter Pro 2", "rarity": "🔵 Редкий", "speed": 25, "weight": 2, "price": 15000},
    {"id": 22, "name": "Ninebot KickScooter Max G30LP", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 18000},
    {"id": 23, "name": "Ninebot KickScooter Max G30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 22000},
    {"id": 24, "name": "Kugoo M4 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 25000},
    {"id": 25, "name": "Kugoo Kirin G2 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 28000},
    {"id": 26, "name": "Ninebot KickScooter F30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 30000},
    {"id": 27, "name": "Ninebot KickScooter F40", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 32000},
    {"id": 28, "name": "Xiaomi Electric Scooter 4 Pro", "rarity": "🔵 Редкий", "speed": 25, "weight": 2, "price": 35000},
    {"id": 29, "name": "Joyor Y8-S", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 38000},
    {"id": 30, "name": "Halten Cross V3", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 40000},

    # --- Эпические (Epic) ---
    {"id": 31, "name": "KuKirin G3 Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 60000},
    {"id": 32, "name": "Kugoo Kirin G4", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 70000},
    {"id": 33, "name": "Ultron T118", "rarity": "🟣 Эпический", "speed": 85, "weight": 1, "price": 80000},
    {"id": 34, "name": "Vsett 9+", "rarity": "🟣 Эпический", "speed": 55, "weight": 1, "price": 85000},
    {"id": 35, "name": "Vsett 10+", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 90000},

    # --- Легендарные (Legendary) ---
    {"id": 36, "name": "Dualtron Thunder 3", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 150000},
    {"id": 37, "name": "Dualtron X-Limited", "rarity": "🟡 Легендарный", "speed": 110, "weight": 0.2, "price": 200000},
    {"id": 38, "name": "Kaabo Wolf King GT Pro", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 220000},
    {"id": 39, "name": "Nami Burn-E 2 Max", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2, "price": 250000},

    # --- Ультра (Ultra) ---
    {"id": 40, "name": "Kugoo Max Speed", "rarity": "💎 Ультра", "speed": 130, "weight": 0.08, "price": 400000},
    {"id": 41, "name": "Ninebot S3 Pro", "rarity": "💎 Ультра", "speed": 135, "weight": 0.07, "price": 450000},
    {"id": 42, "name": "Kugoo F3", "rarity": "💎 Ультра", "speed": 140, "weight": 0.06, "price": 500000},
    {"id": 43, "name": "Kugoo G5", "rarity": "💎 Ультра", "speed": 150, "weight": 0.05, "price": 550000},
    {"id": 44, "name": "Hyperion Quantum X-9000", "rarity": "💎 Ультра", "speed": 165, "weight": 0.04, "price": 700000},
    {"id": 45, "name": "Cyberway Apex Prototype", "rarity": "💎 Ультра", "speed": 180, "weight": 0.03, "price": 850000},
    {"id": 46, "name": "Stellar Phantom V", "rarity": "💎 Ультра", "speed": 200, "weight": 0.02, "price": 1000000},
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
                registered_at TEXT,
                watts INTEGER DEFAULT 0,
                volts INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scooter_id INTEGER,
                model_name TEXT,
                rarity TEXT,
                speed INTEGER,
                tuning TEXT DEFAULT 'Нет'
            )
        """)
        await db.commit()

# ---------------- КЛАВИАТУРЫ ----------------
def get_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Выбить самокат", callback_data="action_get")
    kb.button(text="🛵 Мой гараж", callback_data="action_garage")
    kb.button(text="👤 Мой профиль", callback_data="action_profile")
    kb.button(text="🏦 Банк (1000W = 1V)", callback_data="action_bank")
    kb.button(text="🇪🇺 Европейский рынок", callback_data="action_eu_market")
    kb.button(text="🔧 Мастерская тюнинга", callback_data="action_tuning")
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
            "INSERT OR IGNORE INTO users (user_id, username, registered_at, watts, volts) VALUES (?, ?, ?, 0, 0)",
            (user_id, username, now_iso)
        )
        await db.commit()

    text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "⚡ Добро пожаловать в E-ScooterCards!\n"
        "Собирайте редкие самокаты, зарабатывайте Ватты и Вольты, покупайте технику на рынке и прокачивайте свой гараж!\n\n"
        "Короткие команды:\n"
        "• /getS — Выбить самокат\n"
        "• /garageS — Мой гараж\n"
        "• /profileS — Мой профиль"
    )
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "action_menu")
async def cb_menu(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("🛴 Главное меню:", reply_markup=get_main_menu())
    await callback.answer()

# ---------------- ДРОП САМОКАТОВ ----------------
@dp.callback_query(F.data == "action_get")
@dp.message(Command("get", "getS"))
async def handle_drop(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    now = datetime.now()

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT last_drop, registered_at FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            await db.execute("INSERT INTO users (user_id, registered_at, watts, volts) VALUES (?, ?, 0, 0)", (user_id, now.isoformat()))
            await db.commit()
            reg_time = now.isoformat()
            last_drop_str = None
        else:
            last_drop_str, reg_time = row[0], row[1]

        if last_drop_str:
            last_drop = datetime.fromisoformat(last_drop_str)
            cooldown_end = last_drop + timedelta(minutes=COOLDOWN_MINUTES)
            if now < cooldown_end:
                minutes_left = int((cooldown_end - now).total_seconds() // 60)
                msg = f"⏳ Рано! Следующий самокат будет доступен через {minutes_left} мин."
                if isinstance(event, types.CallbackQuery):
                    await event.answer(msg, show_alert=True)
                else:
                    await message.answer(msg)
                return

        weights = [s["weight"] for s in SCOOTER_DATABASE]
        dropped = random.choices(SCOOTER_DATABASE, weights=weights, k=1)[0]

        # Награда в Ваттах при каждом выпадении
        earned_watts = random.randint(50, 200)

        await db.execute(
            "UPDATE users SET last_drop = ?, watts = watts + ? WHERE user_id = ?", 
            (now.isoformat(), earned_watts, user_id)
        )
        await db.execute(
            "INSERT INTO inventory (user_id, scooter_id, model_name, rarity, speed) VALUES (?, ?, ?, ?, ?)",
            (user_id, dropped["id"], dropped["name"], dropped["rarity"], dropped["speed"])
        )
        await db.commit()

    card_text = (
        f"🎉 ВАМ ВЫПАЛ САМОКАТ!\n\n"
        f"🏷 Модель: {dropped['name']}\n"
        f"⭐️ Редкость: {dropped['rarity']}\n"
        f"⚡️ Скорость: {dropped['speed']} км/ч\n"
        f"💰 Награда: +{earned_watts} Ватт!\n\n"
        f"Транспорт добавлен в гараж."
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

# ---------------- ГАРАЖ ----------------
@dp.callback_query(F.data == "action_garage")
@dp.message(Command("garage", "garageS"))
async def handle_garage(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT id, model_name, rarity, speed, tuning FROM inventory WHERE user_id = ?", (user_id,))
        scooters = await cursor.fetchall()
        await cursor.close()

    if not scooters:
        text = "🛵 Ваш гараж пуст.\nНажмите «Выбить самокат», чтобы получить первый транспорт!"
    else:
        text = f"🛵 Ваш гараж (Всего: {len(scooters)} шт.):\n\n"
        for item in scooters[-15:]:
            inv_id, name, rarity, speed, tuning = item
            text += f"ID [{inv_id}] | {rarity} {name} | ⚡️ {speed} км/ч | Тюнинг: {tuning}\n"
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

# ---------------- ПРОФИЛЬ ----------------
@dp.callback_query(F.data == "action_profile")
@dp.message(Command("profile", "profileS"))
async def handle_profile(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    now = datetime.now()

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT registered_at, watts, volts FROM users WHERE user_id = ?", (user_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        cursor = await db.execute("SELECT model_name, rarity, speed FROM inventory WHERE user_id = ?", (user_id,))
        inventory = await cursor.fetchall()
        await cursor.close()

    reg_date = datetime.fromisoformat(user_row[0]) if user_row and user_row[0] else now
    days = (now - reg_date).days
    watts = user_row[1] if user_row else 0
    volts = user_row[2] if user_row else 0

    profile_text = (
        f"👤 Профиль райдера: {event.from_user.full_name}\n"
        f"🆔 ID: {user_id}\n"
        f"📅 В игре: {days} дн.\n\n"
        f"💳 Баланс:\n"
        f"  • ⚡️ Ватты: {watts} W\n"
        f"  • 🔋 Вольты: {volts} V\n\n"
        f"🛵 Всего самокатов: {len(inventory)} шт."
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

# ---------------- БАНК ----------------
@dp.callback_query(F.data == "action_bank")
async def cb_bank(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обменять 1000 Ватт ➡️ 1 Вольт", callback_data="bank_exchange")
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    kb.adjust(1)

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "🏦 Центральный Банк Энергии\n\nЗдесь вы можете конвертировать Ватты в Вольты.\nКурс: 1000 Ватт = 1 Вольт", 
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "bank_exchange")
async def cb_exchange(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row or row[0] < 1000:
            await callback.answer("❌ Недостаточно Ватт! Нужно минимум 1000 W.", show_alert=True)
            return

        await db.execute("UPDATE users SET watts = watts - 1000, volts = volts + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

    await callback.answer("✅ Обмен выполнен! На счете +1 Вольт.", show_alert=True)
    await cb_bank(callback)

# ---------------- ЕВРОПЕЙСКИЙ РЫНОК ----------------
@dp.callback_query(F.data == "action_eu_market")
async def cb_eu_market(callback: types.CallbackQuery):
    text = "🇪🇺 Европейский рынок самокатов\nПокупка техники напрямую за Ватты:\n\n"
    kb = InlineKeyboardBuilder()
    # Показываем варианты покупки моделей до Легендарной редкости
    for scooter in SCOOTER_DATABASE[:6]:
        kb.button(
            text=f"{scooter['name']} — {scooter['price']} W", 
            callback_data=f"buy_eu_{scooter['id']}"
        )

    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    kb.adjust(1)

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(text, reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_eu_"))
async def cb_buy_eu(callback: types.CallbackQuery):
    scooter_id = int(callback.data.split("_")[2])
    scooter = next((s for s in SCOOTER_DATABASE if s["id"] == scooter_id), None)

    if not scooter:
        await callback.answer("❌ Товар не найден.", show_alert=True)
        return

    user_id = callback.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row or row[0] < scooter["price"]:
            await callback.answer(f"❌ Недостаточно Ватт! Цена: {scooter['price']} W", show_alert=True)
            return

        await db.execute("UPDATE users SET watts = watts - ? WHERE user_id = ?", (scooter["price"], user_id))
        await db.execute(
            "INSERT INTO inventory (user_id, scooter_id, model_name, rarity, speed) VALUES (?, ?, ?, ?, ?)",
            (user_id, scooter["id"], scooter["name"], scooter["rarity"], scooter["speed"])
        )
        await db.commit()

    await callback.answer(f"🎉 Вы успешно купили {scooter['name']}!", show_alert=True)
    await cb_eu_market(callback)

# ---------------- ТЮНИНГ ----------------
@dp.callback_query(F.data == "action_tuning")
async def cb_tuning(callback: types.CallbackQuery):
    text = (
        "🔧 Мастерская Тюнинга\n\n"
        "Совместимость комплектующих:\n"
        "• ❄️ Кулер — устанавливается на Легендарные и 💎 Ультра\n"
        "• ⚡️ Vesc — устанавливается на Эпические\n"
        "• ⚙️ Fardriver — устанавливается на Редкие и Обычные\n\n"
        "Чтобы установить тюнинг, отправьте команду:\n"
        "/tune [ID самоката из гаража]"
    )
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(text, reply_markup=get_back_btn())
    await callback.answer()

@dp.message(Command("tune"))
async def handle_tuning_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Укажите ID самоката из гаража. Пример: /tune 1")
        return

    try:
        scooter_inv_id = int(args[1])
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
        return

    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT rarity, model_name FROM inventory WHERE id = ? AND user_id = ?", (scooter_inv_id, user_id))
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            await message.answer("❌ Самокат с таким ID не найден в вашем гараже.")
            return

        rarity, model_name = row[0], row[1]

        if rarity in ["🟡 Легендарный", "💎 Ультра"]:
            kit = "Кулер ❄️"
        elif rarity == "🟣 Эпический":
            kit = "Vesc ⚡️"
        else:
            kit = "Fardriver ⚙️"

        await db.execute("UPDATE inventory SET tuning = ? WHERE id = ?", (kit, scooter_inv_id))
        await db.commit()

    await message.answer(f"✅ На самокат {model_name} (ID: {scooter_inv_id}) успешно установлен {kit}!")

# ---------------- ЗАПУСК ----------------
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"🚀 Бот @{me.username} успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())