from telegram.ext import Application, CommandHandler

def start(update, context):
    update.message.reply_text("Привет! Я MasloPro бот.")

def main():
    token = "7761025348:AAHqSDrT5zjFY2r-qTOtYazJlLICK4jlKGQ"  # ВСТАВЬ СВОЙ ТОКЕН СЮДА

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
