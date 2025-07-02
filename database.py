import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT
        )
    """)

    # Таблица автомобилей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            brand TEXT,
            model TEXT,
            year INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Таблица записей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            car_id INTEGER,
            service TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(car_id) REFERENCES cars(id)
        )
    """)

    conn.commit()
    conn.close()
