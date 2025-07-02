from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import os
from db import init_db, add_user, get_user_id, add_car, get_user_cars, add_service, get_service_history, get_all_services

# Стартовая инициализация
init_db()

ADD_CAR, ADD_SERVICE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    add_user(user.id, user.first_name)
    await update.message.reply_text("Привет! Я бот MasloPro. Добавим ваш автомобиль?")

async def addcar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите марку, модель, год, двигатель, трансмиссию и пробег через запятую:")
    return ADD_CAR

async def save_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update.message.from_user.id)
    parts = update.message.text.split(",")
    if len(parts) < 6:
        await update.message.reply_text("Пожалуйста, введите все данные корректно.")
        return ConversationHandler.END
    marka, model, year, engine, transmission, mileage = map(str.strip, parts)
    add_car(user_id, marka, model, year, engine, transmission, mileage)
    await update.message.reply_text("Автомобиль добавлен!")
    return ConversationHandler.END

async def addservice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cars = get_user_cars(get_user_id(update.message.from_user.id))
    if not cars:
        await update.message.reply_text("У вас нет добавленных авто.")
        return ConversationHandler.END
    msg = "\n".join([f"{i+1}. {car[1]} {car[2]} {car[3]}" for i, car in enumerate(cars)])
    await update.message.reply_text(f"Выберите авто и введите данные:\n{msg}\n\nПример:\n1, 2024-07-01, SHELL, 4.5, Bosch, Sakura, Mann, да, всё ок")
    return ADD_SERVICE

async def save_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update.message.from_user.id)
    cars = get_user_cars(user_id)
    parts = update.message.text.split(",")
    if len(parts) < 9:
        await update.message.reply_text("Неверный формат данных.")
        return ConversationHandler.END
    idx = int(parts[0]) - 1
    if idx < 0 or idx >= len(cars):
        await update.message.reply_text("Неверный номер авто.")
        return ConversationHandler.END
    car_id = cars[idx][0]
    service_date, oil_brand, oil_liters, oil_filter, air_filter, cabin_filter, greasing, comment = map(str.strip, parts[1:])
    greasing_done = 1 if greasing.lower() in ["да", "yes"] else 0
    add_service(car_id, service_date, oil_brand, float(oil_liters), oil_filter, air_filter, cabin_filter, greasing_done, comment)
    await update.message.reply_text("Сервис добавлен!")
    return ConversationHandler.END

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update.message.from_user.id)
    records = get_service_history(user_id)
    if not records:
        await update.message.reply_text("История пуста.")
        return
    text = ""
    for rec in records:
        text += f"{rec[0]} {rec[1]} {rec[2]}, {rec[3]} — {rec[4]} {rec[5]} л\nФильтры: {rec[6]}, {rec[7]}, {rec[8]}\nШприцовка: {'Да' if rec[9] else 'Нет'}\nКомментарий: {rec[10]}\n\n"
    await update.message.reply_text(text[:4096])

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) != os.getenv("ADMIN_ID"):
        await update.message.reply_text("Доступ запрещён.")
        return
    data = get_all_services()
    if not data:
        await update.message.reply_text("Записей нет.")
        return
    text = ""
    for row in data:
        text += f"{row[0]} — {row[1]} {row[2]} {row[3]} | {row[4]}: {row[5]} {row[6]} л\n{row[7]}, {row[8]}, {row[9]} | Шприцовка: {'Да' if row[10] else 'Нет'}\n{row[11]}\n\n"
    await update.message.reply_text(text[:4096])

def main():
    from dotenv import load_dotenv
    load_dotenv()
    app = Application.builder().token(os.getenv("7761025348:AAHqSDrT5zjFY2r-qTOtYazJlLICK4jlKGQ")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("admin", admin))

    add_car_conv = ConversationHandler(
        entry_points=[CommandHandler("addcar", addcar)],
        states={ADD_CAR: [MessageHandler(filters.TEXT, save_car)]},
        fallbacks=[],
    )
    app.add_handler(add_car_conv)

    add_serv_conv = ConversationHandler(
        entry_points=[CommandHandler("addservice", addservice)],
        states={ADD_SERVICE: [MessageHandler(filters.TEXT, save_service)]},
        fallbacks=[],
    )
    app.add_handler(add_serv_conv)

    app.run_polling()

if __name__ == "__main__":
    main()
