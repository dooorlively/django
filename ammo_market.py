import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
import os
from aiogram.types import FSInputFile

BOT_TOKEN = "8241179908:AAFFQCrXmN_E8YwlUm9L8DZp7EHfnfXbfm8"
DB_PATH = "shop/db.sqlite3"
MEDIA_PATH = "shop/media"  # Путь к медиа файлам Django

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_sessions = {}

def check_django_password(password, stored_password):
    """Упрощенная проверка пароля Django"""
    try:
        if stored_password.startswith('pbkdf2_sha256$'):
            return True
        elif password == stored_password:
            return True
        else:
            return False
    except:
        return False

async def send_with_image(message, image_path, caption):
    """Отправка сообщения с картинкой если она существует"""
    full_path = os.path.join(MEDIA_PATH, image_path)

    if os.path.exists(full_path):
        try:
            await message.answer_photo(
                FSInputFile(full_path),
                caption=caption,
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logger.error(f"Error sending image {full_path}: {e}")

    # Если картинки нет или ошибка - отправляем текст
    await message.answer(caption, parse_mode="HTML")
    return False

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🏪 Магазин (реальная база Django)\n\n"
        "🔐 /login - войти в систему\n"
        "📦 /products - товары с картинками\n" 
        "🛡️ /vests - бронежилеты с картинками\n"
        "👤 /profile - профиль\n"
        "📊 /stats - статистика\n"
        "📋 /orders - мои заказы с товарами\n"
    )

@dp.message(Command("login"))
async def login(message: types.Message):
    try:
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.answer("❌ Формат: /login имя пароль")
            return

        username, password = args

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id, username, password FROM auth_user WHERE username = ?", (username,))
            user = await cursor.fetchone()
            await cursor.close()

        if user:
            user_id, db_username, db_password = user

            if check_django_password(password, db_password):
                user_sessions[message.from_user.id] = user_id
                await message.answer(f"✅ Вход выполнен: {db_username}")
            else:
                await message.answer("❌ Неверный пароль")
        else:
            await message.answer("❌ Пользователь не найден")

    except Exception as e:
        logger.error(f"Login error: {e}")
        await message.answer("❌ Ошибка при входе")

@dp.message(Command("products"))
async def show_products(message: types.Message):
    """Показать товары с картинками"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT designation, caliber, ammo_type, price, availability_status, image FROM store_product"
            )
            products = await cursor.fetchall()
            await cursor.close()

        if not products:
            await message.answer("📦 Нет товаров в наличии")
            return

        for product in products:
            designation, caliber, ammo_type, price, status, image = product

            status_icon = {
                "in_stock": "✅",
                "out_of_stock": "❌",
                "restocking": "⏳"
            }.get(status, "❓")

            caption = (
                f"{status_icon} <b>{designation}</b>\n"
                f"Калибр: {caliber}\n"
                f"Тип: {ammo_type}\n" 
                f"Цена: {price} грн\n"
                f"Статус: {status_icon}"
            )

            if image:
                await send_with_image(message, image, caption)
            else:
                await message.answer(caption, parse_mode="HTML")

        await message.answer(f"📊 Всего товаров: {len(products)}")

    except Exception as e:
        logger.error(f"Products error: {e}")
        await message.answer("❌ Ошибка при загрузке товаров")

@dp.message(Command("vests"))
async def show_vests(message: types.Message):
    """Показать бронежилеты с картинками"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT model, protection_level, weight, price, availability_status, image FROM store_vest"
            )
            vests = await cursor.fetchall()
            await cursor.close()

        if not vests:
            await message.answer("🛡️ Нет бронежилетов в наличии")
            return

        for vest in vests:
            model, protection, weight, price, status, image = vest

            status_icon = {
                "in_stock": "✅",
                "out_of_stock": "❌",
                "restocking": "⏳"
            }.get(status, "❓")

            caption = (
                f"{status_icon} <b>{model}</b>\n"
                f"Уровень защиты: {protection}\n"
                f"Вес: {weight} кг\n"
                f"Цена: {price} грн\n"
                f"Статус: {status_icon}"
            )

            if image:
                await send_with_image(message, image, caption)
            else:
                await message.answer(caption, parse_mode="HTML")

        await message.answer(f"📊 Всего бронежилетов: {len(vests)}")

    except Exception as e:
        logger.error(f"Vests error: {e}")
        await message.answer("❌ Ошибка при загрузке бронежилетов")

@dp.message(Command("orders"))
async def show_orders(message: types.Message):
    """Показать реальные заказы пользователя с товарами"""
    user_id = user_sessions.get(message.from_user.id)

    if not user_id:
        await message.answer("❌ Сначала войдите: /login имя пароль")
        return

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Получаем заказы пользователя
            cursor = await db.execute(
                "SELECT id, created_at FROM store_order WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
                (user_id,)
            )
            orders = await cursor.fetchall()
            await cursor.close()

        if not orders:
            await message.answer("📦 У вас нет заказов")
            return

        for order in orders:
            order_id, created_at = order

            # Получаем товары из этого заказа
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT oi.quantity, oi.price_at_time, oi.item_type,
                           p.designation, p.caliber, p.image as p_image,
                           v.model, v.protection_level, v.image as v_image
                    FROM store_orderitem oi
                    LEFT JOIN store_product p ON oi.product_id = p.id
                    LEFT JOIN store_vest v ON oi.vest_id = v.id
                    WHERE oi.order_id = ?
                """, (order_id,))
                items = await cursor.fetchall()
                await cursor.close()

            if not items:
                await message.answer(f"📦 Заказ #{order_id} от {created_at}\nНет товаров в заказе")
                continue

            # Отправляем заголовок заказа
            await message.answer(
                f"📦 <b>Заказ #{order_id}</b>\n"
                f"📅 {created_at}\n"
                f"🛒 Товаров: {len(items)}",
                parse_mode="HTML"
            )

            # Отправляем каждый товар отдельным сообщением
            total_price = 0
            for item in items:
                quantity, price_at_time, item_type, designation, caliber, p_image, model, protection, v_image = item
                item_total = quantity * price_at_time
                total_price += item_total

                if item_type == "product" and designation:
                    caption = (
                        f"🔫 <b>{designation}</b> ({caliber})\n"
                        f"Количество: {quantity} шт\n"
                        f"Цена: {price_at_time} грн\n"
                        f"Сумма: {item_total} грн"
                    )
                    image_path = p_image
                elif item_type == "vest" and model:
                    caption = (
                        f"🛡️ <b>{model}</b>\n"
                        f"Уровень: {protection}\n"
                        f"Количество: {quantity} шт\n"
                        f"Цена: {price_at_time} грн\n"
                        f"Сумма: {item_total} грн"
                    )
                    image_path = v_image
                else:
                    caption = (
                        f"❓ <b>Неизвестный товар</b>\n"
                        f"Количество: {quantity} шт\n"
                        f"Цена: {price_at_time} грн\n"
                        f"Сумма: {item_total} грн"
                    )
                    image_path = None

                if image_path:
                    await send_with_image(message, image_path, caption)
                else:
                    await message.answer(caption, parse_mode="HTML")

            # Итоговая сумма заказа
            await message.answer(f"💰 <b>Общая сумма заказа: {total_price} грн</b>", parse_mode="HTML")

    except Exception as e:
        logger.error(f"Orders error: {e}")
        await message.answer("❌ Ошибка при загрузке заказов")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    user_id = user_sessions.get(message.from_user.id)

    if not user_id:
        await message.answer("❌ Сначала войдите: /login имя пароль")
        return

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT username, email, date_joined, is_staff FROM auth_user WHERE id = ?", (user_id,))
            user = await cursor.fetchone()
            await cursor.close()

        if user:
            username, email, date_joined, is_staff = user
            role = "👑 Администратор" if is_staff else "👤 Пользователь"
            await message.answer(
                f"👤 <b>Профиль</b>\n"
                f"Имя: {username}\n"
                f"Email: {email}\n"
                f"Роль: {role}\n"
                f"Дата регистрации: {date_joined}",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Пользователь не найден")

    except Exception as e:
        logger.error(f"Profile error: {e}")
        await message.answer("❌ Ошибка при загрузке профиля")

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    """Показать статистику"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            tables = {
                'auth_user': '👥 Пользователи',
                'store_product': '🔫 Товары',
                'store_vest': '🛡️ Бронежилеты',
                'store_order': '📦 Заказы',
                'store_orderitem': '📋 Позиции заказов'
            }

            response = "📊 <b>Статистика магазина:</b>\n\n"

            for table, name in tables.items():
                cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                count = (await cursor.fetchone())[0]
                await cursor.close()
                response += f"{name}: {count}\n"

            await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("users"))
async def show_users(message: types.Message):
    """Показать пользователей"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id, username, email, is_staff FROM auth_user")
            users = await cursor.fetchall()
            await cursor.close()

        response = "👥 <b>Пользователи:</b>\n\n"
        for user in users:
            user_id, username, email, is_staff = user
            role = "👑 Админ" if is_staff else "👤 Пользователь"
            response += f"{role} {username}\nID: {user_id}\nEmail: {email}\n\n"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    logger.info(f"🚀 Бот запущен!")
    logger.info(f"📁 База: {DB_PATH}")
    logger.info(f"🖼️ Медиа: {MEDIA_PATH}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())