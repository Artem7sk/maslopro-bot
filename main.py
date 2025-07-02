import logging
import os
import random
import sqlite3
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Этапы регистрации
ASK_PHONE, CONFIRM_CODE = range(2)

# Подключение к БД
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    phone TEXT,
    verification_code TEXT,
    verified INTEGER DEFAULT 0
)
""")
conn.commit()

# Словарь сессий для временного хранения кодов
sessions = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text("Добро пожаловать! Пожалуйста, отправьте свой номер телефона для регистрации.", reply_markup=reply_markup)
    return ASK_PHONE

# Обработка номера телефона
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    if not contact or not contact.phone_number:
        await update.message.reply_text("Пожалуйста, используйте кнопку для отправки номера.")
        return ASK_PHONE

    phone = contact.phone_number
    telegram_id = update.message.from_user.id
    code = str(random.randint(1000, 9999))

    # Сохраняем или обновляем запись
    cursor.execute("INSERT OR REPLACE INTO users (telegram_id, phone, verification_code, verified) VALUES (?, ?, ?, ?)",
                   (telegram_id, phone, code, 0))
    conn.commit()

    # Отправляем код
    await update.message.reply_text(f"Код подтверждения: {code}\nВведите его ниже:")
    return CONFIRM_CODE

# Обработка кода подтверждения
async def confirm_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_code = update.message.text.strip()
    telegram_id = update.message.from_user.id

    cursor.execute("SELECT verification_code FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()

    if row and user_code == row[0]:
        cursor.execute("UPDATE users SET verified = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        await update.message.reply_text("✅ Успешная регистрация!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Неверный код. Попробуйте снова:")
        return CONFIRM_CODE

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

# Основная функция
def main():
    import dotenv
    dotenv.load_dotenv()

    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [MessageHandler(filters.CONTACT, handle_phone)],
            CONFIRM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
