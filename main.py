import asyncio
from datetime import datetime, timedelta
import random
import aiosqlite

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ---------------- КОНФИГУРАЦИЯ ----------------
BOT_TOKEN = "8909119386:AAGK9hTizA7n1pvrrwLmR2ew63Nf7Hh_VZg"

COOLDOWN_MINUTES = 120  # КД на дроп: 2 часа

# Карта специальных администраторов
ADMIN_MAP = {
    8597571970: {"custom_id": "0000000001", "role": "👑 [ADMIN]"},
    5318117285: {"custom_id": "0000000002", "role": "👑 [ADMIN]"},
    7978928618: {"custom_id": "0000000003", "role": "👑 [ADMIN]"},
    7490453666: {"custom_id": "0000000004", "role": "👑 [ADMIN]"},
}

REVERSE_ADMIN_MAP = {v["custom_id"]: k for k, v in ADMIN_MAP.items()}
ACTIVE_TRADES = {}

SCOOTER_DATABASE = [
    # Обычные
    {"id": 1, "name": "Ninebot KickScooter ES1", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4, "price": 5000},
    {"id": 2, "name": "Xiaomi Electric Scooter Essential", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4, "price": 5500},
    {"id": 3, "name": "Ninebot KickScooter E22", "rarity": "⚪️ Обычный", "speed": 20, "weight": 4, "price": 6000},
    {"id": 4, "name": "Kugoo Kirin Mini 2", "rarity": "⚪️ Обычный", "speed": 25, "weight": 4, "price": 6500},
    {"id": 5, "name": "Acer Series 1", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 7000},
    {"id": 6, "name": "Ninebot KickScooter E25", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 7200},
    {"id": 7, "name": "Xiaomi Electric Scooter 3 Lite", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 7500},
    {"id": 8, "name": "Ninebot KickScooter D18W", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 7800},
    {"id": 9, "name": "Joyor A3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 8000},
    {"id": 10, "name": "Hiper Slim", "rarity": "⚪️ Обычный", "speed": 22, "weight": 3, "price": 8200},
    {"id": 11, "name": "Halten Tony", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 8500},
    {"id": 12, "name": "Kugoo S1", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 8700},
    {"id": 13, "name": "Okai Neon Lite", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 9000},
    {"id": 14, "name": "Ninebot KickScooter F20A", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 9200},
    {"id": 15, "name": "Xiaomi Mi Electric Scooter 1S", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 9500},
    {"id": 16, "name": "Acer ES Series 3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 9700},
    {"id": 17, "name": "Kugoo Kirin S3 Pro", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 10000},
    {"id": 18, "name": "GT Sonic", "rarity": "⚪️ Обычный", "speed": 22, "weight": 3, "price": 10200},
    {"id": 19, "name": "Ninebot KickScooter E2 Plus", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 10500},
    {"id": 20, "name": "Xiaomi Electric Scooter 4 Go", "rarity": "⚪️ Обычный", "speed": 20, "weight": 3, "price": 11000},

    # Редкие
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

    # Эпические
    {"id": 31, "name": "KuKirin G3 Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 60000},
    {"id": 32, "name": "Kugoo Kirin G4", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 70000},
    {"id": 33, "name": "Ultron T118", "rarity": "🟣 Эпический", "speed": 85, "weight": 1, "price": 80000},
    {"id": 34, "name": "Vsett 9+", "rarity": "🟣 Эпический", "speed": 55, "weight": 1, "price": 85000},
    {"id": 35, "name": "Vsett 10+", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 90000},

    # Легендарные
    {"id": 36, "name": "Dualtron Thunder 3", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 150000},
    {"id": 37, "name": "Dualtron X-Limited", "rarity": "🟡 Легендарный", "speed": 110, "weight": 0.2, "price": 200000},
    {"id": 38, "name": "Kaabo Wolf King GT Pro", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 220000},
    {"id": 39, "name": "Nami Burn-E 2 Max", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2, "price": 250000},

    # Ультра
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

def get_user_display_info(user_id: int, original_name: str):
    if user_id in ADMIN_MAP:
        adm = ADMIN_MAP[user_id]
        return f"{adm['role']} {original_name}", adm["custom_id"]
    return original_name, str(user_id)

async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS avito_market (
                lot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                seller_username TEXT,
                model_name TEXT,
                rarity TEXT,
                speed INTEGER,
                tuning TEXT,
                price INTEGER,
                created_at TEXT
            )
        """)
        await db.commit()

# --- РЕГИСТРАЦИЯ МЕНЮ TELEGRAM ---
async def set_main_menu(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="🏠 Главное меню"),
        types.BotCommand(command="get", description="🎁 Выбить самокат"),
        types.BotCommand(command="garage", description="🛵 Мой гараж"),
types.BotCommand(command="profile", description="👤 Мой профиль"),
        types.BotCommand(command="avito", description="📦 Авито рынок"),
        types.BotCommand(command="bank", description="🏦 Банк (обмен валюты)"),
        types.BotCommand(command="market", description="🇪🇺 Европейский рынок"),
        types.BotCommand(command="tune", description="🔧 Тюнинг самоката")
    ]
    await bot.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())

def get_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Выбить самокат (/get)", callback_data="action_get")
    kb.button(text="🛵 Мой гараж (/garage)", callback_data="action_garage")
    kb.button(text="👤 Мой профиль (/profile)", callback_data="action_profile")
    kb.button(text="📦 Авито Рынок (/avito)", callback_data="action_avito")
    kb.button(text="🏦 Банк (/bank)", callback_data="action_bank")
    kb.button(text="🇪🇺 Рынок Магазин (/market)", callback_data="action_eu_market")
    kb.button(text="🔧 Тюнинг (/tune)", callback_data="action_tuning")
    kb.adjust(1)
    return kb.as_markup()

def get_back_btn():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    return kb.as_markup()

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    username = (message.from_user.username or "Rider").lower()
    first_name = message.from_user.first_name
    now_iso = datetime.now().isoformat()

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, registered_at, watts, volts) VALUES (?, ?, ?, ?, 0, 0)",
            (user_id, username, first_name, now_iso)
        )
        await db.execute(
            "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?", 
            (username, first_name, user_id)
        )
        await db.commit()

    display_name, custom_id = get_user_display_info(user_id, first_name)
    text = (
        f"👋 Привет, {display_name}! (ID: {custom_id})\n\n"
        "⚡ Добро пожаловать в E-ScooterCards!\n"
        "Собирайте редкие самокаты, торгуйте на Авито, обменивайтесь и улучшайте транспорт!"
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

@dp.callback_query(F.data == "action_get")
@dp.message(Command("get", "getS"))
async def handle_drop(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    now = datetime.now()

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT last_drop FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, registered_at, watts, volts) VALUES (?, ?, ?, ?, 0, 0)",
                (user_id, (event.from_user.username or "Rider").lower(), event.from_user.first_name, now.isoformat())
            )
            await db.commit()
            last_drop_str = None
        else:
            last_drop_str = row[0]

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
        f"⭐ Редкость: {dropped['rarity']}\n"
        f"⚡ Скорость: {dropped['speed']} км/ч\n"
        f"💰 Награда: +{earned_watts} Ватт!\n\n"
        f"Транспорт добавлен в ваш гараж."
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
@dp.message(Command("garage", "garageS"))
async def handle_garage(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT id, model_name, rarity, speed, tuning FROM inventory WHERE user_id = ?", (user_id,))
        scooters = await cursor.fetchall()
        await cursor.close()

    if not scooters:
        text = "🛵 Ваш гараж пуст.\nНажмите «Выбить самокат» или введите /get, чтобы получить первый транспорт!"
    else:
        text = f"🛵 Ваш гараж (Всего: {len(scooters)} шт.):\n\n"
        for item in scooters[-15:]:
            inv_id, name, rarity, speed, tuning = item
            text += f"🔹 ID [{inv_id}] | {rarity} {name} | ⚡ {speed} км/ч | Мод: {tuning}\n"

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
@dp.message(Command("profile", "profileS"))
async def handle_profile(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    now = datetime.now()
    target_user_id = event.from_user.id

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT user_id, username, first_name, registered_at, watts, volts FROM users WHERE user_id = ?", (target_user_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        if not user_row:
            if isinstance(event, types.CallbackQuery):
                await event.answer("❌ Профиль не найден", show_alert=True)
            else:
                await message.answer("❌ Профиль не найден")
            return

        u_id, u_name, f_name, reg_at, watts, volts = user_row
        cursor = await db.execute("SELECT COUNT(*) FROM inventory WHERE user_id = ?", (u_id,))
        count_row = await cursor.fetchone()
        await cursor.close()

    reg_date = datetime.fromisoformat(reg_at) if reg_at else now
    days = (now - reg_date).days
    scooters_count = count_row[0] if count_row else 0
    display_name, custom_id = get_user_display_info(u_id, f_name or u_name or "Rider")

    profile_text = (
        f"👤 Профиль райдера: {display_name}\n"
        f"🆔 ID: {custom_id}\n"
        f"📅 В игре: {days} дн.\n\n"
        f"💳 Баланс:\n"
        f"  • ⚡ Ватты: {watts} W\n"
        f"  • 🔋 Вольты: {volts} V\n\n"
        f"🛵 Всего самокатов в гараже: {scooters_count} шт."
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

@dp.message(Command("sell"))
async def handle_sell_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Использование: /sell [ID_гаража] [Цена_W]")
        return
    try:
        inv_id, price = int(args[1]), int(args[2])
    except ValueError:
        await message.answer("❌ Ошибочные данные.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT model_name, rarity, speed, tuning FROM inventory WHERE id = ? AND user_id = ?", (inv_id, user_id))
        scooter = await cursor.fetchone()
        await cursor.close()

        if not scooter:
            await message.answer("❌ Самокат не найден в вашем гараже.")
            return

        name, rarity, speed, tuning = scooter
        await db.execute("DELETE FROM inventory WHERE id = ?", (inv_id,))
        await db.execute("""
            INSERT INTO avito_market (seller_id, seller_username, model_name, rarity, speed, tuning, price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, name, rarity, speed, tuning, price, datetime.now().isoformat()))
        await db.commit()

    await message.answer(f"✅ Успешно выставили {rarity} {name} на Авито за {price} W!")

@dp.callback_query(F.data == "action_avito")
@dp.message(Command("avito"))
async def handle_avito_market(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT lot_id, seller_username, model_name, rarity, speed, tuning, price FROM avito_market ORDER BY lot_id DESC LIMIT 10")
        lots = await cursor.fetchall()
        await cursor.close()

    if not lots:
        text = "📦 Авито пуст. Используйте /sell для продажи."
        kb = get_back_btn()
    else:
        text = "📦 Авито — Рынок объявлений:\n\n"
        kb_builder = InlineKeyboardBuilder()
        for lot in lots:
            lot_id, seller_u, name, rarity, speed, tuning, price = lot
            text += f"🔹 Лот #{lot_id}: {rarity} {name} | ⚡ {speed} км/ч\n   💰 Цена: {price} W | @{seller_u}\n\n"
            kb_builder.button(text=f"Купить #{lot_id} ({price} W)", callback_data=f"buy_avito_{lot_id}")
        kb_builder.button(text="⬅️ В главное меню", callback_data="action_menu")
        kb_builder.adjust(1)
        kb = kb_builder.as_markup()

    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_avito_"))
async def cb_buy_avito(callback: types.CallbackQuery):
    lot_id = int(callback.data.replace("buy_avito_", ""))
    buyer_id = callback.from_user.id

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT seller_id, model_name, rarity, speed, tuning, price FROM avito_market WHERE lot_id = ?", (lot_id,))
        lot = await cursor.fetchone()
        await cursor.close()

        if not lot:
            await callback.answer("❌ Лот уже продан.", show_alert=True)
            return

        seller_id, name, rarity, speed, tuning, price = lot
        if seller_id == buyer_id:
            await callback.answer("Это ваш собственный лот!", show_alert=True)
            return

        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (buyer_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        if not user_row or user_row[0] < price:
            await callback.answer("❌ Недостаточно Ватт!", show_alert=True)
            return

        await db.execute("UPDATE users SET watts = watts - ? WHERE user_id = ?", (price, buyer_id))
        await db.execute("UPDATE users SET watts = watts + ? WHERE user_id = ?", (price, seller_id))
        await db.execute("DELETE FROM avito_market WHERE lot_id = ?", (lot_id,))
        await db.execute("INSERT INTO inventory (user_id, model_name, rarity, speed, tuning) VALUES (?, ?, ?, ?, ?)", (buyer_id, name, rarity, speed, tuning))
        await db.commit()

    await callback.answer(f"🎉 Вы купили {name}!", show_alert=True)
    await handle_avito_market(callback)

@dp.callback_query(F.data == "action_bank")
@dp.message(Command("bank"))
async def cb_bank(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обменять 1000 Ватт ➡️ 1 Вольт", callback_data="bank_exchange")
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    kb.adjust(1)
    text = "🏦 Центральный Банк\nКурс: 1000 Ватт = 1 Вольт"
    
    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=kb.as_markup())
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "bank_exchange")
async def cb_exchange(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row or row[0] < 1000:
            await callback.answer("❌ Нужно минимум 1000 W.", show_alert=True)
            return

        await db.execute("UPDATE users SET watts = watts - 1000, volts = volts + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

    await callback.answer("✅ Обмен выполнен (+1 Вольт)!", show_alert=True)
    await cb_bank(callback)

@dp.callback_query(F.data == "action_eu_market")
@dp.message(Command("market"))
async def cb_eu_market(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    text = "🇪🇺 Европейский рынок\nПокупка техники за Ватты:\n\n"
    kb = InlineKeyboardBuilder()
    for scooter in SCOOTER_DATABASE[:6]:
        kb.button(text=f"{scooter['name']} — {scooter['price']} W", callback_data=f"buy_eu_{scooter['id']}")
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    kb.adjust(1)

    if isinstance(event, types.CallbackQuery):
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=kb.as_markup())
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("buy_eu_"))
async def cb_buy_eu(callback: types.CallbackQuery):
    scooter_id = int(callback.data.split("_")[2])
    scooter = next((s for s in SCOOTER_DATABASE if s["id"] == scooter_id), None)
    if not scooter:
        return

    user_id = callback.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()

        if not row or row[0] < scooter["price"]:
            await callback.answer("❌ Недостаточно Ватт!", show_alert=True)
            return
            await db.execute("UPDATE users SET watts = watts - ? WHERE user_id = ?", (scooter["price"], user_id))
        await db.execute("INSERT INTO inventory (user_id, scooter_id, model_name, rarity, speed) VALUES (?, ?, ?, ?, ?)", (user_id, scooter["id"], scooter["name"], scooter["rarity"], scooter["speed"]))
        await db.commit()

    await callback.answer(f"🎉 Вы купили {scooter['name']}!", show_alert=True)
    await cb_eu_market(callback)

@dp.callback_query(F.data == "action_tuning")
async def cb_tuning(callback: types.CallbackQuery):
    text = "🔧 Мастерская Тюнинга\nИспользуйте команду: /tune [ID самоката]"
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
        await message.answer("⚠️ Укажите ID: /tune [ID]")
        return
    try:
        scooter_inv_id = int(args[1])
    except ValueError:
        return

    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT rarity, model_name FROM inventory WHERE id = ? AND user_id = ?", (scooter_inv_id, user_id))
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            await message.answer("❌ Самокат не найден.")
            return

        rarity, model_name = row[0], row[1]
        kit = "Кулер ❄️" if rarity in ["🟡 Легендарный", "💎 Ультра"] else ("Vesc ⚡" if rarity == "🟣 Эпический" else "Fardriver ⚙️")
        await db.execute("UPDATE inventory SET tuning = ? WHERE id = ?", (kit, scooter_inv_id))
        await db.commit()

    await message.answer(f"✅ Установлен тюнинг {kit} на {model_name}!")

# --- АДМИНСКАЯ КОМАНДА ДЛЯ ID 0000000001 ---
@dp.message(Command("admin"))
async def handle_admin_panel(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, главный ли это администратор (с кастомным ID 0000000001)
    if user_id not in ADMIN_MAP or ADMIN_MAP[user_id]["custom_id"] != "0000000001":
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    args = message.text.split()
    if len(args) < 4:
        help_text = (
            "🛠 Панель администратора (ID: 0000000001):\n\n"
            "1️⃣ Выдать Ватты:\n"
            "/admin money [ID_игрока] [сумма]\n"
            "Пример: /admin money 0000000002 50000\n\n"
            "2️⃣ Выдать самокат по ID из базы:\n"
            "/admin scooter [ID_игрока] [ID_самоката_из_базы]\n"
            "Пример: /admin scooter 0000000002 36 (выдаст Dualtron Thunder 3)"
        )
        await message.answer(help_text, parse_mode="Markdown")
        return

    action = args[1]
    target_raw_id = args[2]

    # Определяем реальный ID (поддерживает кастомные ID типа 000000000X)
    target_user_id = REVERSE_ADMIN_MAP.get(target_raw_id)
    if not target_user_id:
        try:
            target_user_id = int(target_raw_id)
        except ValueError:
            await message.answer("❌ Неверный формат ID пользователя.")
            return

    async with aiosqlite.connect("bot_database.db") as db:
        if action == "money":
            try:
                amount = int(args[3])
            except ValueError:
                await message.answer("❌ Сумма должна быть числом.")
                return

            await db.execute("UPDATE users SET watts = watts + ? WHERE user_id = ?", (amount, target_user_id))
            await db.commit()
            await message.answer(f"✅ Успешно выдано {amount} Ватт игроку с ID {target_raw_id}!")

        elif action == "scooter":
            try:
                scooter_id = int(args[3])
            except ValueError:
                await message.answer("❌ ID самоката должен быть числом.")
                return

            scooter = next((s for s in SCOOTER_DATABASE if s["id"] == scooter_id), None)
            if not scooter:
                await message.answer("❌ Самокат с таким ID не найден в базе данных.")
                return

            await db.execute(
                "INSERT INTO inventory (user_id, scooter_id, model_name, rarity, speed) VALUES (?, ?, ?, ?, ?)",
                (target_user_id, scooter["id"], scooter["name"], scooter["rarity"], scooter["speed"])
            )
            await db.commit()
            await message.answer(f"✅ Успешно выдан самокат {scooter['rarity']} {scooter['name']} игроку с ID {target_raw_id}!", parse_mode="Markdown")
        else:
            await message.answer("❌ Неизвестное действие. Используйте money или scooter.")

@dp.message(Command("trade"))
async def handle_trade_cmd(message: types.Message):
    await message.answer("🤝 Система трейдов активна.")

@dp.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer("ℹ️ Используйте кнопку Menu слева для быстрого управления ботом.")

async def main():
    await init_db()
    # Регистрируем меню в Telegram перед стартом
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"🚀 Бот @{me.username} успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())