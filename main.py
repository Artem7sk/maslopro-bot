import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes
)
from db import init_db, add_user, get_user_id, add_car, get_user_cars, add_service, get_service_history, get_all_services

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # добавьте сюда свой Telegram ID

# Этапы для разговоров
(MARKA, MODEL, YEAR, ENGINE, TRANSMISSION, MILEAGE,
 CHOOSE_CAR, DATE, OIL, LITERS, OIL_FILTER, AIR_FILTER,
 CABIN_FILTER, GREASING, COMMENT) = range(15)

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.full_name)
    await update.message.reply_text("Привет! Давай добавим твой автомобиль. Введите марку:")
    return MARKA

async def marka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['marka'] = update.message.text
    await update.message.reply_text("Введите модель:")
    return MODEL

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['model'] = update.message.text
    await update.message.reply_text("Введите год выпуска:")
    return YEAR

async def year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['year'] = update.message.text
    await update.message.reply_text("Объём двигателя (л):")
    return ENGINE

async def engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['engine'] = update.message.text
    await update.message.reply_text("Тип коробки (АКПП или МКПП):")
    return TRANSMISSION

async def transmission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['transmission'] = update.message.text
    await update.message.reply_text("Введите пробег (км):")
    return MILEAGE

async def mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_car(
        get_user_id(update.effective_user.id),
        context.user_data['marka'],
        context.user_data['model'],
        context.user_data['year'],
        context.user_data['engine'],
        context.user_data['transmission'],
        update.message.text
    )
    await update.message.reply_text("Авто добавлено! /запись для обслуживания.")
    return ConversationHandler.END

async def zapis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cars = get_user_cars(get_user_id(update.effective_user.id))
    if not cars:
        await update.message.reply_text("Сначала добавьте авто через /start.")
        return ConversationHandler.END
    kb = [[f"{i+1}. {c[1]} {c[2]} {c[3]}"] for i, c in enumerate(cars)]
    context.user_data['cars_list'] = cars
    await update.message.reply_text("Выберите авто:", reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))
    return CHOOSE_CAR

async def choose_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = int(update.message.text.split('.')[0]) - 1
    context.user_data['car_id'] = context.user_data['cars_list'][idx][0]
    await update.message.reply_text("Введите дату (YYYY-MM-DD):", reply_markup=ReplyKeyboardRemove())
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await update.message.reply_text("Название масла:")
    return OIL

async def oil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oil'] = update.message.text
    await update.message.reply_text("Сколько литров?")
    return LITERS

async def liters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['liters'] = float(update.message.text)
    await update.message.reply_text("Масляный фильтр:")
    return OIL_FILTER

async def oil_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oil_filter'] = update.message.text
    await update.message.reply_text("Воздушный фильтр:")
    return AIR_FILTER

async def air_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['air_filter'] = update.message.text
    await update.message.reply_text("Салонный фильтр:")
    return CABIN_FILTER

async def cabin_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cabin_filter'] = update.message.text
    await update.message.reply_text("Шприцовка выполнена? (да/нет)")
    return GREASING

async def greasing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['greasing'] = 1 if update.message.text.lower() == "да" else 0
    await update.message.reply_text("Комментарий:")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_service(
        car_id=context.user_data['car_id'],
        service_date=context.user_data['date'],
        oil_brand=context.user_data['oil'],
        oil_liters=context.user_data['liters'],
        oil_filter=context.user_data['oil_filter'],
        air_filter=context.user_data['air_filter'],
        cabin_filter=context.user_data['cabin_filter'],
        greasing_done=context.user_data['greasing'],
        comment=update.message.text
    )
    await update.message.reply_text("✅ Сервис записан!")
    return ConversationHandler.END

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hist = get_service_history(get_user_id(update.effective_user.id))
    if not hist:
        return await update.message.reply_text("Нет записей.")
    txt = ""
    for r in hist:
        txt += f"{r[3]} — {r[0]} {r[1]} {r[2]}, масло: {r[4]} ({r[5]}л), фильтры: {r[6]}/{r[7]}/{r[8]}, шприцовка: {'да' if r[9] else 'нет'}\nКомментарий: {r[10]}\n\n"
    await update.message.reply_text(txt[:4000])

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return await update.message.reply_text("⛔ Нет доступа.")
    recs = get_all_services()
    if not recs:
        return await update.message.reply_text("Нет заявок.")
    txt = ""
    for r in recs:
        txt += f"{r[4]} — {r[0]} {r[1]} {r[2]}, пользователь: {r[0]}, масло: {r[5]}, {r[6]}л, фильтры: {r[7]}/{r[8]}/{r[9]}, шприцовка: {'да' if r[10] else 'нет'}\nКомментарий: {r[11]}\n\n"
    await update.message.reply_text(txt[:4000])

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Разговор для добавления авто
    car_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MARKA: [MessageHandler(filters.TEXT & ~filters.COMMAND, marka)],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, model)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
            ENGINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, engine)],
            TRANSMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, transmission)],
            MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mileage)],
        },
        fallbacks=[],
    )

    service_conv = ConversationHandler(
        entry_points=[CommandHandler("запись", zapis)],
        states={
            CHOOSE_CAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_car)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            OIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, oil)],
            LITERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, liters)],
            OIL_FILTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, oil_filter)],
            AIR_FILTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, air_filter)],
            CABIN_FILTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, cabin_filter)],
            GREASING: [MessageHandler(filters.TEXT & ~filters.COMMAND, greasing)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
        },
        fallbacks=[],
    )

    # Регистрируем все хэндлеры
    app.add_handler(car_conv)
    app.add_handler(service_conv)
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("admin", admin))

    app.run_polling()

if __name__ == "__main__":
    main()
