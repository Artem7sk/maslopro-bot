MasloProBot — Telegram-бот для замены масла

🚀 Как запустить на https://render.com:

1. Зарегистрируйся на render.com и подтверди почту
2. Создай новый проект → "Web Service"
3. Залей туда файлы: main.py, requirements.txt, Procfile
4. Перейди во вкладку "Environment" и добавь переменную окружения:
   BOT_TOKEN = <токен, который ты получил от BotFather>
5. Нажми "Deploy" и дождись запуска
6. Перейди в Telegram и напиши своему боту команду /start

✅ Всё! Готов к приёму заявок.



---------------------------
📄 Инструкция по установке на Render (хостинг)
🔧 Подготовка:
Зарегистрируйся на https://render.com (можно через GitHub или Google)

Нажми "New +" → Web Service

Загрузите все файлы:

main.py

db.py

requirements.txt

Procfile

🌍 Настрой Render:
Environment → Add Environment Variable
→ BOT_TOKEN = твой токен от BotFather

Start Command: оставить пустым (Render сам найдёт Procfile)

Free Plan → Deploy

✅ Готово!
Через 1–2 минуты бот заработает. Напиши в Telegram /start, добавь авто, и можешь сразу ввести /запись.