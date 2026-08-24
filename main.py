import asyncio
import random
from datetime import datetime, timedelta
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

# Обратная карта для быстрого поиска по кастомному ID
REVERSE_ADMIN_MAP = {v["custom_id"]: k for k, v in ADMIN_MAP.items()}

# Временное хранилище активных предложений трейда
ACTIVE_TRADES = {}

# База данных самокатов
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

# ---------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------------
def get_user_display_info(user_id: int, original_name: str):
    """Возвращает форматированное имя и отображаемый ID."""
    if user_id in ADMIN_MAP:
        adm = ADMIN_MAP[user_id]
        return f"{adm['role']} {original_name}", adm["custom_id"]
    return original_name, str(user_id)

# ---------------- БАЗА ДАННЫХ ----------------
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
        async with aiosqlite.connect("bot_database.db") as db:
        if target_user_id:
            cursor = await db.execute("SELECT user_id, username, first_name, registered_at, watts, volts FROM users WHERE user_id = ?", (target_user_id,))
        else:
            cursor = await db.execute("SELECT user_id, username, first_name, registered_at, watts, volts FROM users WHERE username = ?", (target_username,))
        
        user_row = await cursor.fetchone()
        await cursor.close()

        if not user_row:
            not_found_msg = "❌ Пользователь не найден в базе данных бота."
            if isinstance(event, types.CallbackQuery):
                await event.answer(not_found_msg, show_alert=True)
            else:
                await message.answer(not_found_msg)
            return

        u_id, u_name, f_name, reg_at, watts, volts = user_row

        cursor = await db.execute("SELECT COUNT(*) FROM inventory WHERE user_id = ?", (u_id,))
        count_row = await cursor.fetchone()
        await cursor.close()

    reg_date = datetime.fromisoformat(reg_at) if reg_at else now
    days = (now - reg_date).days
    scooters_count = count_row[0] if count_row else 0
    display_name, custom_id = get_user_display_info(u_id, f_name or u_name or "Rider")

    is_self = (u_id == event.from_user.id)
    header = "👤 Ваш профиль райдера:" if is_self else "👤 Профиль игрока:"

    profile_text = (
        f"{header} {display_name}\n"
        f"🆔 ID: {custom_id}\n"
        f"🏷 Юзернейм: @{u_name or 'отсутствует'}\n"
        f"📅 В игре: {days} дн.\n\n"
        f"💳 Баланс:\n"
        f"  • ⚡️ Ватты: {watts} W\n"
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

# ---------------- АВИТО (P2P МАРКЕТПЛЕЙС) ----------------
@dp.message(Command("sell"))
async def handle_sell_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "📦 Продажа самоката на Авито:\n"
            "Используйте команду: /sell [ID_из_гаража] [Цена_в_Ваттах]\n\n"
            "Пример: /sell 3 15000 (выставит самокат под ID 3 за 15000 W)"
        )
        return

    try:
        inv_id = int(args[1])
        price = int(args[2])
    except ValueError:
        await message.answer("❌ ID самоката и цена должны быть целыми числами.")
        return

    if price <= 0:
        await message.answer("❌ Цена должна быть больше 0 Ватт.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    async with aiosqlite.connect("bot_database.db") as db:
        # Проверяем наличие самоката в гараже
        cursor = await db.execute(
            "SELECT model_name, rarity, speed, tuning FROM inventory WHERE id = ? AND user_id = ?",
            (inv_id, user_id)
        )
        scooter = await cursor.fetchone()
        await cursor.close()

        if not scooter:
            await message.answer("❌ Этот самокат не найден в вашем гараже.")
            return

        name, rarity, speed, tuning = scooter

        # Удаляем из гаража и выставляем на Авито
        await db.execute("DELETE FROM inventory WHERE id = ?", (inv_id,))
        await db.execute("""
            INSERT INTO avito_market (seller_id, seller_username, model_name, rarity, speed, tuning, price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, name, rarity, speed, tuning, price, datetime.now().isoformat()))
        await db.commit()

    await message.answer(
        f"✅ Вы успешно выставили {rarity} {name} на Авито за {price} W!\n"
        f"Объявление теперь доступно в общем каталоге /avito."
    )

@dp.callback_query(F.data == "action_avito")
@dp.message(Command("avito"))
async def handle_avito_market(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("""
            SELECT lot_id, seller_id, seller_username, model_name, rarity, speed, tuning, price 
            FROM avito_market ORDER BY lot_id DESC LIMIT 10
        """)
        lots = await cursor.fetchall()
        await cursor.close()

    if not lots:
        text = (
            "📦 Авито — Площадка объявлений\n\n"
            "Сейчас нет активных объявлений.\n"
            "Вы можете выставить свой самокат командой:\n"
            "/sell [ID_из_гаража] [Цена_W]"
        )
        kb = get_back_btn()
    else:
        text = (
            "📦 Авито — Площадка объявлений игроков:\n\n"
            "Нажмите на кнопку лота, чтобы купить его или снять с продажи (если он ваш):\n\n"
        )
        kb_builder = InlineKeyboardBuilder()
        for lot in lots:
            lot_id, seller_id, seller_u, name, rarity, speed, tuning, price = lot
            text += f"🔹 Лот #{lot_id}: {rarity} {name} | ⚡️ {speed} км/ч | Мод: {tuning}\n   💰 Цена: {price} W | Продавец: @{seller_u}\n\n"
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
        cursor = await db.execute("""
            SELECT seller_id, seller_username, model_name, rarity, speed, tuning, price 
            FROM avito_market WHERE lot_id = ?
        """, (lot_id,))
        lot = await cursor.fetchone()
        await cursor.close()

        if not lot:
            await callback.answer("❌ Этот лот уже продан или снят с публикации.", show_alert=True)
            return

        seller_id, seller_u, name, rarity, speed, tuning, price = lot

        # Если лот принадлежит самому покупателю — возвращаем в гараж
        if seller_id == buyer_id:
            await db.execute("DELETE FROM avito_market WHERE lot_id = ?", (lot_id,))
            await db.execute("""
                INSERT INTO inventory (user_id, model_name, rarity, speed, tuning)
                VALUES (?, ?, ?, ?, ?)
            """, (buyer_id, name, rarity, speed, tuning))
            await db.commit()
            await callback.answer("✅ Вы сняли свой лот с Авито и вернули самокат в гараж!", show_alert=True)
            await handle_avito_market(callback)
            return

        # Проверяем баланс покупателя
        cursor = await db.execute("SELECT watts FROM users WHERE user_id = ?", (buyer_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        if not user_row or user_row[0] < price:
            await callback.answer(f"❌ Недостаточно Ватт! Требуется {price} W.", show_alert=True)
            return

        # Проводим транзакцию
        await db.execute("UPDATE users SET watts = watts - ? WHERE user_id = ?", (price, buyer_id))
        await db.execute("UPDATE users SET watts = watts + ? WHERE user_id = ?", (price, seller_id))
        await db.execute("DELETE FROM avito_market WHERE lot_id = ?", (lot_id,))
        await db.execute("""
            INSERT INTO inventory (user_id, model_name, rarity, speed, tuning)
            VALUES (?, ?, ?, ?, ?)
        """, (buyer_id, name, rarity, speed, tuning))
        await db.commit()

    await callback.answer(f"🎉 Вы успешно купили {name} на Авито за {price} W!", show_alert=True)

    try:
        await bot.send_message(
            seller_id, 
            f"💰 Ваш товар на Авито продан!\n"
            f"Самокат: {rarity} {name}\n"
            f"Вам начислено: +{price} W"
        )
    except Exception:
        pass

    await handle_avito_market(callback)

# ---------------- БАНК ----------------
@dp.callback_query(F.data == "action_bank")
@dp.message(Command("bank"))
async def cb_bank(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обменять 1000 Ватт ➡️ 1 Вольт", callback_data="bank_exchange")
    kb.button(text="⬅️ В главное меню", callback_data="action_menu")
    kb.adjust(1)

    text = "🏦 Центральный Банк Энергии\n\nЗдесь вы можете конвертировать Ватты в Вольты.\nКурс: 1000 Ватт = 1 Вольт"
    
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
            await callback.answer("❌ Недостаточно Ватт! Нужно минимум 1000 W.", show_alert=True)
            return

        await db.execute("UPDATE users SET watts = watts - 1000, volts = volts + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

    await callback.answer("✅ Обмен выполнен! На счете +1 Вольт.", show_alert=True)
    await cb_bank(callback)

# ---------------- ЕВРОПЕЙСКИЙ РЫНОК ----------------
@dp.callback_query(F.data == "action_eu_market")
@dp.message(Command("market"))
async def cb_eu_market(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    text = "🇪🇺 Европейский рынок самокатов\nПокупка новой техники напрямую за Ватты:\n\n"
    kb = InlineKeyboardBuilder()

    for scooter in SCOOTER_DATABASE[:6]:
        kb.button(
            text=f"{scooter['name']} — {scooter['price']} W", 
            callback_data=f"buy_eu_{scooter['id']}"
        )

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
        "Чтобы установить тюнинг, используйте команду:\n"
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

    await message.answer(f"✅ На самокат {model_name} (ID: {scooter_inv_id}) успешно установлен тюнинг {kit}!")

# ---------------- СИСТЕМА ТРЕЙДИНГА ----------------
@dp.message(Command("trade"))
async def handle_trade_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "⚠️ Формат команды трейда:\n"
            "/trade @username ID_самоката\n\n"
            "Пример: /trade @friend 5 (где 5 — ID самоката из вашего гаража)"
        )
        return

    target_username = args[1].replace("@", "").strip().lower()
    try:
        scooter_inv_id = int(args[2])
    except ValueError:
        await message.answer("❌ ID самоката должен быть числом.")
        return

    sender_id = message.from_user.id
    sender_username = (message.from_user.username or "Rider").lower()

    if target_username == sender_username:
        await message.answer("❌ Вы не можете отправить трейд самому себе.")
        return

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute(
            "SELECT model_name, rarity, speed, tuning FROM inventory WHERE id = ? AND user_id = ?", 
            (scooter_inv_id, sender_id)
        )
        scooter = await cursor.fetchone()
        await cursor.close()

        if not scooter:
            await message.answer("❌ Этот самокат не найден в вашем гараже.")
            return

        cursor = await db.execute("SELECT user_id FROM users WHERE username = ?", (target_username,))
        target_row = await cursor.fetchone()
        await cursor.close()
        if not target_row:
            await message.answer(f"❌ Пользователь @{target_username} еще не запускал этого бота.")
            return

        target_id = target_row[0]

    trade_id = f"tr_{random.randint(100000, 999999)}"
    ACTIVE_TRADES[trade_id] = {
        "sender_id": sender_id,
        "target_id": target_id,
        "scooter_inv_id": scooter_inv_id,
        "scooter_name": scooter[0]
    }

    sender_name, _ = get_user_display_info(sender_id, message.from_user.first_name)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Принять обмен", callback_data=f"trade_accept_{trade_id}")
    kb.button(text="❌ Отклонить", callback_data=f"trade_decline_{trade_id}")
    kb.adjust(2)

    try:
        await bot.send_message(
            chat_id=target_id,
            text=(
                f"🤝 Вам поступило предложение обмена!\n\n"
                f"От: {sender_name} (@{sender_username})\n"
                f"Самокат: {scooter[1]} {scooter[0]}\n"
                f"Скорость: {scooter[2]} км/ч | Мод: {scooter[3]}\n\n"
                f"Хотите принять технику в свой гараж?"
            ),
            reply_markup=kb.as_markup()
        )
        await message.answer(f"📨 Запрос на трейд успешно отправлен пользователю @{target_username}!")
    except Exception:
        await message.answer("❌ Не удалось отправить уведомление получателю (возможно, диалог с ботом заблокирован).")

@dp.callback_query(F.data.startswith("trade_accept_"))
async def cb_trade_accept(callback: types.CallbackQuery):
    trade_id = callback.data.replace("trade_accept_", "")
    trade = ACTIVE_TRADES.get(trade_id)

    if not trade:
        await callback.answer("❌ Трейд устарел или был отменен.", show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    if callback.from_user.id != trade["target_id"]:
        await callback.answer("❌ Это предложение адресовано не вам!", show_alert=True)
        return

    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute(
            "SELECT id FROM inventory WHERE id = ? AND user_id = ?", 
            (trade["scooter_inv_id"], trade["sender_id"])
        )
        exists = await cursor.fetchone()
        await cursor.close()

        if not exists:
            await callback.answer("❌ Самокат больше не принадлежит отправителю.", show_alert=True)
            ACTIVE_TRADES.pop(trade_id, None)
            return

        await db.execute("UPDATE inventory SET user_id = ? WHERE id = ?", (trade["target_id"], trade["scooter_inv_id"]))
        await db.commit()

    ACTIVE_TRADES.pop(trade_id, None)

    await callback.message.edit_text(f"🎉 Вы успешно приняли самокат {trade['scooter_name']} в свой гараж!")
    try:
        await bot.send_message(trade["sender_id"], f"🤝 Трейд завершен! Ваш самокат {trade['scooter_name']} успешно передан новому владельцу.")
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data.startswith("trade_decline_"))
async def cb_trade_decline(callback: types.CallbackQuery):
    trade_id = callback.data.replace("trade_decline_", "")
    trade = ACTIVE_TRADES.get(trade_id)

    if not trade:
        await callback.answer("❌ Трейд уже не активен.", show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    if callback.from_user.id != trade["target_id"]:
        await callback.answer("❌ Это действие не для вас!", show_alert=True)
        return

    ACTIVE_TRADES.pop(trade_id, None)
    await callback.message.edit_text("❌ Вы отклонили предложение обмена.")
    try:
        await bot.send_message(trade["sender_id"], f"⚠️ Пользователь отклонил ваш трейд на {trade['scooter_name']}.")
    except Exception:
        pass
    await callback.answer()

# ---------------- ЗАПУСК ----------------
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"🚀 Бот @{me.username} успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())