from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from db import *
import os

# 🔐 Укажи свой Telegram ID
ADMIN_ID = 123456789

# Этапы диалога
(MARKA, MODEL, YEAR, ENGINE, TRANSMISSION, MILEAGE, CHOOSE_CAR, DATE, OIL, LITERS,
 OIL_FILTER, AIR_FILTER, CABIN_FILTER, GREASING, COMMENT) = range(15)

user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.full_name)
    await update.message.reply_text("Привет! Давайте добавим ваш автомобиль.\nВведите марку:")
    return MARKA

async def marka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['marka'] = update.message.text
    await update.message.reply_text("Введите модель:")
    return MODEL

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['model'] = update.message.text
    await update.message.reply_text("Введите год выпуска:")
    return YEAR

async def year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['year'] = update.message.text
    await update.message.reply_text("Введите объём двигателя (л):")
    return ENGINE

async def engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['engine'] = update.message.text
    await update.message.reply_text("Выберите тип коробки передач:",
        reply_markup=ReplyKeyboardMarkup([['АКПП', 'МКПП']], one_time_keyboard=True))
    return TRANSMISSION

async def transmission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['transmission'] = update.message.text
    await update.message.reply_text("Введите пробег (км):")
    return MILEAGE

async def mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['mileage'] = update.message.text
    user = update.effective_user
    uid = get_user_id(user.id)
    add_car(uid, user_data['marka'], user_data['model'], user_data['year'],
            user_data['engine'], user_data['transmission'], user_data['mileage'])

    await update.message.reply_text("✅ Автомобиль добавлен! Чтобы записаться на обслуживание, введи /запись")
    return ConversationHandler.END

# Команда /запись
async def zapis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update.effective_user.id)
    cars = get_user_cars(user_id)
    if not cars:
        await update.message.reply_text("Сначала добавьте автомобиль через /start.")
        return ConversationHandler.END
    context.user_data['cars'] = {f"{c[1]} {c[2]} {c[3]}": c[0] for c in cars}
    await update.message.reply_text("Выберите авто:",
        reply_markup=ReplyKeyboardMarkup([[name] for name in context.user_data['cars']], one_time_keyboard=True))
    return CHOOSE_CAR

async def choose_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    context.user_data['car_id'] = context.user_data['cars'][choice]
    await update.message.reply_text("Введите дату обслуживания (например, 2025-07-01):", reply_markup=ReplyKeyboardRemove())
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await update.message.reply_text("Введите название масла:")
    return OIL

async def oil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oil'] = update.message.text
    await update.message.reply_text("Сколько литров масла было использовано?")
    return LITERS

async def liters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['liters'] = update.message.text
    await update.message.reply_text("Масляный фильтр (название или '-'):") 
    return OIL_FILTER

async def oil_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oil_filter'] = update.message.text
    await update.message.reply_text("Воздушный фильтр (название или '-'):")
    return AIR_FILTER

async def air_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['air_filter'] = update.message.text
    await update.message.reply_text("Салонный фильтр (название или '-'):")
    return CABIN_FILTER

async def cabin_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cabin_filter'] = update.message.text
    await update.message.reply_text("Проводилась шприцовка? (да/нет):")
    return GREASING

async def greasing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['greasing'] = 1 if update.message.text.lower() == "да" else 0
    await update.message.reply_text("Комментарий (если есть) или '-'")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['comment'] = update.message.text
    add_service(
        car_id=context.user_data['car_id'],
        service_date=context.user_data['date'],
        oil_brand=context.user_data['oil'],
        oil_liters=float(context.user_data['liters']),
        oil_filter=context.user_data['oil_filter'],
        air_filter=context.user_data['air_filter'],
        cabin_filter=context.user_data['cabin_filter'],
        greasing_done=context.user_data['greasing'],
        comment=context.user_data['comment']
    )
    await update.message.reply_text("✅ Запись сохранена!")
    return ConversationHandler.END

# Команда /история
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = get_user_id(update.effective_user.id)
    history = get_service_history(uid)
    if not history:
        await update.message.reply_text("История пока пуста.")
        return
    msg = ""
    for h in history:
        marka, model, year, date, oil, liters, oil_f, air_f, cabin_f, grease, comm = h
        msg += f"{date} — {marka} {model} {year}, масло: {oil} ({liters}л), фильтры: {oil_f}/{air_f}/{cabin_f}, шприцовка: {'да' if grease else 'нет'}\nКомментарий: {comm}\n\n"
    await update.message.reply_text(msg)

# Команда /admin
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    records = get_all_services()
    if not records:
        await update.message.reply_text("Заявок нет.")
        return
    msg = ""
    for r in records:
        name, marka, model, year, date, oil, liters, oil_f, air_f, cabin_f, grease, comm = r
        msg += f"{date} — {name} ({marka} {model} {year}), масло: {oil} ({liters}л), фильтры: {oil_f}/{air_f}/{cabin_f}, шприцовка: {'да' if grease else 'нет'}\nКомментарий: {comm}\n\n"
    await update.message.reply_text(msg)

# Старт
def main():
    init_db()
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

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
        fallbacks=[]
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
        fallbacks=[]
    )

    app.add_handler(car_conv)
    app.add_handler(service_conv)
    app.add_handler(CommandHandler("история", history))
    app.add_handler(CommandHandler("admin", admin))
    app.run_polling()

if __name__ == "__main__":
    main()
