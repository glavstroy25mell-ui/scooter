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
    # --- Обычные (Легкие городские, 20-30 км/ч) ---
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
    {"id": 21, "name": "Kugoo Wish 01", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 11200},
    {"id": 22, "name": "Kugoo Wish 02", "rarity": "⚪️ Обычный", "speed": 28, "weight": 3, "price": 11500},
    {"id": 23, "name": "Kugoo S3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 11800},
    {"id": 24, "name": "Halten Lite", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 12000},
    {"id": 25, "name": "Ninebot ES2", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 12500},
    {"id": 26, "name": "Ninebot ES4", "rarity": "⚪️ Обычный", "speed": 30, "weight": 3, "price": 13000},
    {"id": 27, "name": "Xiaomi Mi Scooter Pro", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 13500},
    {"id": 28, "name": "Joyor F3", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 14000},
    {"id": 29, "name": "Aovo Pro", "rarity": "⚪️ Обычный", "speed": 30, "weight": 3, "price": 14200},
    {"id": 30, "name": "Kugoo C1 Pro", "rarity": "⚪️ Обычный", "speed": 30, "weight": 3, "price": 14500},

    # --- Редкие (Динамичные городские и средние модели, 30-55 км/ч) ---
    {"id": 31, "name": "Xiaomi Mi Electric Scooter Pro 2", "rarity": "🔵 Редкий", "speed": 25, "weight": 2, "price": 15000},
    {"id": 32, "name": "Ninebot KickScooter Max G30LP", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 18000},
    {"id": 33, "name": "Ninebot KickScooter Max G30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 22000},
    {"id": 34, "name": "Kugoo M4", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 23000},
    {"id": 35, "name": "Kugoo M4 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 25000},
    {"id": 36, "name": "Kugoo Kirin G2 Pro", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 28000},
    {"id": 37, "name": "Ninebot KickScooter F30", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 30000},
    {"id": 38, "name": "Ninebot KickScooter F40", "rarity": "🔵 Редкий", "speed": 30, "weight": 2, "price": 32000},
    {"id": 39, "name": "Xiaomi Electric Scooter 4 Pro", "rarity": "🔵 Редкий", "speed": 25, "weight": 2, "price": 35000},
    {"id": 40, "name": "Joyor Y8-S", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 38000},
    {"id": 41, "name": "Halten Cross V3", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 40000},
    {"id": 42, "name": "Kugoo R1", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 41000},
    {"id": 43, "name": "Kugoo R2", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 42000},
    {"id": 44, "name": "Kugoo R3", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 43500},
    {"id": 45, "name": "Kugoo R3 Pro", "rarity": "🔵 Редкий", "speed": 50, "weight": 2, "price": 45000},
    {"id": 46, "name": "Kugoo Wish 03", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 46000},
    {"id": 47, "name": "Kugoo Wish 04", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 47500},
    {"id": 48, "name": "Kugoo Kirin M5", "rarity": "🔵 Редкий", "speed": 50, "weight": 2, "price": 49000},
    {"id": 49, "name": "Kugoo Kirin M5 Pro", "rarity": "🔵 Редкий", "speed": 55, "weight": 2, "price": 52000},
    {"id": 50, "name": "Ninebot Max G2", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 54000},
    {"id": 51, "name": "Ultron T10", "rarity": "🔵 Редкий", "speed": 50, "weight": 2, "price": 55000},
    {"id": 52, "name": "Speedway 5", "rarity": "🔵 Редкий", "speed": 55, "weight": 2, "price": 57000},
    {"id": 53, "name": "Dualtron Spider", "rarity": "🔵 Редкий", "speed": 60, "weight": 2, "price": 58000},
    {"id": 54, "name": "Kugoo X1", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 59000},

    # --- Эпические (Мощные полноприводные, 55-85 км/ч) ---
    {"id": 55, "name": "KuKirin G3 Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 60000},
    {"id": 56, "name": "Kugoo Kirin G4", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 70000},
    {"id": 57, "name": "Ultron T118", "rarity": "🟣 Эпический", "speed": 85, "weight": 1, "price": 80000},
    {"id": 58, "name": "Vsett 9+", "rarity": "🟣 Эпический", "speed": 55, "weight": 1, "price": 85000},
    {"id": 59, "name": "Vsett 10+", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 90000},
    {"id": 60, "name": "Kugoo R4", "rarity": "🟣 Эпический", "speed": 60, "weight": 1, "price": 92000},
    {"id": 61, "name": "Kugoo R4 Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 95000},
    {"id": 62, "name": "Kugoo R5", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 98000},
    {"id": 63, "name": "Kugoo R5 Pro", "rarity": "🟣 Эпический", "speed": 75, "weight": 1, "price": 102000},
    {"id": 64, "name": "Kugoo Wish 05", "rarity": "🟣 Эпический", "speed": 60, "weight": 1, "price": 105000},
    {"id": 65, "name": "Kugoo Wish 06", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 108000},
    {"id": 66, "name": "Kugoo Kirin G2 Master", "rarity": "🟣 Эпический", "speed": 60, "weight": 1, "price": 110000},
    {"id": 67, "name": "Kugoo Kirin G3", "rarity": "🟣 Эпический", "speed": 50, "weight": 1, "price": 112000},
    {"id": 68, "name": "Dualtron Eagle Pro", "rarity": "🟣 Эпический", "speed": 75, "weight": 1, "price": 115000},
    {"id": 69, "name": "Dualtron Victor", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 120000},
    {"id": 70, "name": "Kaabo Mantis 10 Pro", "rarity": "🟣 Эпический", "speed": 60, "weight": 1, "price": 125000},
    {"id": 71, "name": "Kaabo Mantis King GT", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 130000},
    {"id": 72, "name": "Halten RS-03 v2", "rarity": "🟣 Эпический", "speed": 75, "weight": 1, "price": 135000},
    {"id": 73, "name": "Currus R11", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 140000},
    {"id": 74, "name": "Speedway 4", "rarity": "🟣 Эпический", "speed": 50, "weight": 1, "price": 145000},

    # --- Легендарные (Супер-мощные гиперсамокаты, 90-115 км/ч) ---
    {"id": 75, "name": "Dualtron Thunder 3", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 150000},
    {"id": 76, "name": "Dualtron X-Limited", "rarity": "🟡 Легендарный", "speed": 110, "weight": 0.2, "price": 200000},
    {"id": 77, "name": "Kaabo Wolf King GT Pro", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.3, "price": 220000},
    {"id": 78, "name": "Nami Burn-E 2 Max", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2, "price": 250000},
    {"id": 79, "name": "Kugoo R6", "rarity": "🟡 Легендарный", "speed": 90, "weight": 0.3, "price": 270000},
    {"id": 80, "name": "Kugoo R6 Pro", "rarity": "🟡 Легендарный", "speed": 95, "weight": 0.3, "price": 290000},
    {"id": 81, "name": "Kugoo R7", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 310000},
    {"id": 82, "name": "Kugoo Wish 07", "rarity": "🟡 Легендарный", "speed": 90, "weight": 0.3, "price": 330000},
    {"id": 83, "name": "Kugoo Wish 08", "rarity": "🟡 Легендарный", "speed": 95, "weight": 0.3, "price": 350000},
    {"id": 84, "name": "Dualtron Storm", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 360000},
    {"id": 85, "name": "Dualtron Ultra 2", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 370000},
    {"id": 86, "name": "Vsett 11+", "rarity": "🟡 Легендарный", "speed": 85, "weight": 0.3, "price": 380000},
    {"id": 87, "name": "Nami Burn-E Viper", "rarity": "🟡 Легендарный", "speed": 115, "weight": 0.2, "price": 390000},

    # --- Ультра (Эксклюзивные гоночные монстры, 120-160 км/ч) ---
    {"id": 88, "name": "Kugoo Max Speed", "rarity": "💎 Ультра", "speed": 50, "weight": 0.08, "price": 400000},
    {"id": 89, "name": "Ninebot S3 Pro", "rarity": "💎 Ультра", "speed": 120, "weight": 0.07, "price": 450000},
    {"id": 90, "name": "Kugoo F3", "rarity": "💎 Ультра", "speed": 60, "weight": 0.06, "price": 500000},
    {"id": 91, "name": "Kugoo G5", "rarity": "💎 Ультра", "speed": 65, "weight": 0.05, "price": 550000},
    {"id": 92, "name": "Hyperion Quantum X-9000", "rarity": "💎 Ультра", "speed": 130, "weight": 0.04, "price": 700000},
    {"id": 93, "name": "Cyberway Apex Prototype", "rarity": "💎 Ультра", "speed": 140, "weight": 0.03, "price": 850000},
    {"id": 94, "name": "Stellar Phantom V", "rarity": "💎 Ультра", "speed": 150, "weight": 0.02, "price": 1000000},
    {"id": 95, "name": "Kugoo R8 Ultimate", "rarity": "💎 Ультра", "speed": 110, "weight": 0.08, "price": 1050000},
    {"id": 96, "name": "Kugoo R9 Hyper", "rarity": "💎 Ультра", "speed": 120, "weight": 0.07, "price": 1100000},
    {"id": 97, "name": "Kugoo Wish 09 Apex", "rarity": "💎 Ультра", "speed": 125, "weight": 0.06, "price": 1150000},
    {"id": 98, "name": "Kugoo Wish 10 Godlike", "rarity": "💎 Ультра", "speed": 135, "weight": 0.05, "price": 1200000},
    {"id": 99, "name": "Dualtron Achilleus", "rarity": "💎 Ультра", "speed": 125, "weight": 0.08, "price": 1250000},
    {"id": 100, "name": "Dualtron City", "rarity": "💎 Ультра", "speed": 90, "weight": 0.07, "price": 1300000},
    
    # --- Дополнительные модели Kugoo R / Wish / Kirin (ID 101 - 150 с фиксированной реалистичной скоростью) ---
    {"id": 101, "name": "Kugoo Kirin Mini", "rarity": "⚪️ Обычный", "speed": 20, "weight": 3, "price": 13000},
    {"id": 102, "name": "Kugoo Wish Ultra Lite", "rarity": "⚪️ Обычный", "speed": 22, "weight": 3, "price": 13500},
    {"id": 103, "name": "Kugoo R-Line 1", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 14000},
    {"id": 104, "name": "Kugoo Kirin ES2", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 14200},
    {"id": 105, "name": "Kugoo Wish City", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 14500},
    {"id": 106, "name": "Kugoo R-Line 2", "rarity": "⚪️ Обычный", "speed": 28, "weight": 3, "price": 14800},
    {"id": 107, "name": "Kugoo Kirin Mini 4", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 15000},
    {"id": 108, "name": "Kugoo Wish Urban", "rarity": "⚪️ Обычный", "speed": 27, "weight": 3, "price": 15200},
    {"id": 109, "name": "Kugoo R-Line 3", "rarity": "⚪️ Обычный", "speed": 30, "weight": 3, "price": 15500},
    {"id": 110, "name": "Kugoo Kirin S1 Plus", "rarity": "⚪️ Обычный", "speed": 25, "weight": 3, "price": 16000},

    {"id": 111, "name": "Kugoo Kirin G2", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 17000},
    {"id": 112, "name": "Kugoo Wish Sport 1", "rarity": "🔵 Редкий", "speed": 35, "weight": 2, "price": 19000},
    {"id": 113, "name": "Kugoo R-Drive 1", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 21000},
    {"id": 114, "name": "Kugoo Kirin M4 Pro Plus", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 24000},
    {"id": 115, "name": "Kugoo Wish Sport 2", "rarity": "🔵 Редкий", "speed": 40, "weight": 2, "price": 26000},
    {"id": 116, "name": "Kugoo R-Drive 2", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 29000},
    {"id": 117, "name": "Kugoo Kirin G2 Pro Plus", "rarity": "🔵 Редкий", "speed": 48, "weight": 2, "price": 31000},
    {"id": 118, "name": "Kugoo Wish Cross", "rarity": "🔵 Редкий", "speed": 45, "weight": 2, "price": 33000},
    {"id": 119, "name": "Kugoo R-Drive 3", "rarity": "🔵 Редкий", "speed": 50, "weight": 2, "price": 36000},
    {"id": 120, "name": "Kugoo Kirin Max Speed", "rarity": "🔵 Редкий", "speed": 50, "weight": 2, "price": 39000},

    {"id": 121, "name": "Kugoo Kirin G3 Pro Max", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 62000},
    {"id": 122, "name": "Kugoo Wish Monster 1", "rarity": "🟣 Эпический", "speed": 60, "weight": 1, "price": 68000},
    {"id": 123, "name": "Kugoo R-Turbo 1", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 74000},
    {"id": 124, "name": "Kugoo Kirin G4 Pro", "rarity": "🟣 Эпический", "speed": 75, "weight": 1, "price": 82000},
    {"id": 125, "name": "Kugoo Wish Monster 2", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 88000},
    {"id": 126, "name": "Kugoo R-Turbo 2", "rarity": "🟣 Эпический", "speed": 75, "weight": 1, "price": 94000},
    {"id": 127, "name": "Kugoo Kirin G2 Master Pro", "rarity": "🟣 Эпический", "speed": 65, "weight": 1, "price": 99000},
    {"id": 128, "name": "Kugoo Wish Extreme", "rarity": "🟣 Эпический", "speed": 70, "weight": 1, "price": 106000},
    {"id": 129, "name": "Kugoo R-Turbo 3", "rarity": "🟣 Эпический", "speed": 80, "weight": 1, "price": 113000},
    {"id": 130, "name": "Kugoo Kirin Beast", "rarity": "🟣 Эпический", "speed": 85, "weight": 1, "price": 118000},

    {"id": 131, "name": "Kugoo Kirin G3 Pro Extreme", "rarity": "🟡 Легендарный", "speed": 90, "weight": 0.3, "price": 160000},
    {"id": 132, "name": "Kugoo Wish Titan 1", "rarity": "🟡 Легендарный", "speed": 90, "weight": 0.3, "price": 180000},
    {"id": 133, "name": "Kugoo R-Overlord 1", "rarity": "🟡 Легендарный", "speed": 95, "weight": 0.3, "price": 210000},
    {"id": 134, "name": "Kugoo Kirin G4 Max", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 230000},
    {"id": 135, "name": "Kugoo Wish Titan 2", "rarity": "🟡 Легендарный", "speed": 95, "weight": 0.3, "price": 260000},
    {"id": 136, "name": "Kugoo R-Overlord 2", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 280000},
    {"id": 137, "name": "Kugoo Kirin Beast Pro", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2, "price": 300000},
    {"id": 138, "name": "Kugoo Wish Titan 3", "rarity": "🟡 Легендарный", "speed": 100, "weight": 0.2, "price": 320000},
    {"id": 139, "name": "Kugoo R-Overlord 3", "rarity": "🟡 Легендарный", "speed": 105, "weight": 0.2, "price": 340000},
    {"id": 140, "name": "Kugoo Kirin Supreme", "rarity": "🟡 Легендарный", "speed": 110, "weight": 0.2, "price": 375000},
    {"id": 141, "name": "Kugoo Kirin G3 Pro Godlike", "rarity": "💎 Ультра", "speed": 120, "weight": 0.08, "price": 420000},
    {"id": 142, "name": "Kugoo Wish Phantom 1", "rarity": "💎 Ультра", "speed": 125, "weight": 0.07, "price": 480000},
    {"id": 143, "name": "Kugoo R-Absolute 1", "rarity": "💎 Ультра", "speed": 130, "weight": 0.06, "price": 530000},
    {"id": 144, "name": "Kugoo Kirin G4 Godlike", "rarity": "💎 Ультра", "speed": 135, "weight": 0.05, "price": 600000},
    {"id": 145, "name": "Kugoo Wish Phantom 2", "rarity": "💎 Ультра", "speed": 140, "weight": 0.04, "price": 750000},
    {"id": 146, "name": "Kugoo R-Absolute 2", "rarity": "💎 Ультра", "speed": 145, "weight": 0.03, "price": 900000},
    {"id": 147, "name": "Kugoo Kirin Supreme Pro", "rarity": "💎 Ультра", "speed": 150, "weight": 0.02, "price": 1020000},
    {"id": 148, "name": "Kugoo Wish Phantom 3", "rarity": "💎 Ультра", "speed": 155, "weight": 0.02, "price": 1120000},
    {"id": 149, "name": "Kugoo R-Absolute 3", "rarity": "💎 Ультра", "speed": 160, "weight": 0.01, "price": 1220000},
    {"id": 150, "name": "Kugoo Kirin Final Boss", "rarity": "💎 Ультра", "speed": 180, "weight": 0.01, "price": 1500000}
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
        # Проверяем, существует ли уже пользователь в базе
        cursor = await db.execute("SELECT watts, volts FROM users WHERE user_id = ?", (user_id,))
        user_row = await cursor.fetchone()
        await cursor.close()

        if not user_row:
            # Если пользователя нет вообще — создаем с нуля
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, registered_at, watts, volts) VALUES (?, ?, ?, ?, 0, 0)",
                (user_id, username, first_name, now_iso)
            )
        else:
            # Если пользователь уже есть — просто обновляем его username и имя, не трогая баланс и дату регистрации!
            await db.execute(
                "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?", 
                (username, first_name, user_id)
            )
        await db.commit()

    display_name, custom_id = get_user_display_info(user_id, first_name)
    text = (
        f"👋 С возвращением, {display_name}! (ID: {custom0 := custom_id if 'custom_id' in locals() else custom_id})\n\n"
        "⚡ Добро пожаловать в E-ScooterCards!\n"
        "Собирайте редкие самокаты, торгуйте на Авито, обменивайтесь и улучшайте транспорт!"
    )
    # Исправленный вывод ID для стабильности
    text = (
        f"👋 С возвращением, {display_name}! (ID: {custom_id})\n\n"
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