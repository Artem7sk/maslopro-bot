import sqlite3

DB_NAME = "maslopro.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Пользователи
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT
    )''')
    # Автомобили
    c.execute('''CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        marka TEXT,
        model TEXT,
        year TEXT,
        engine TEXT,
        transmission TEXT,
        mileage TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    # Заявки
    c.execute('''CREATE TABLE IF NOT EXISTS service_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        service_date TEXT,
        oil_brand TEXT,
        oil_liters REAL,
        oil_filter TEXT,
        air_filter TEXT,
        cabin_filter TEXT,
        greasing_done INTEGER,
        comment TEXT,
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )''')
    conn.commit()
    conn.close()

def add_user(telegram_id, name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
    conn.commit()
    conn.close()

def get_user_id(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_car(user_id, marka, model, year, engine, transmission, mileage):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO cars (user_id, marka, model, year, engine, transmission, mileage)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, marka, model, year, engine, transmission, mileage))
    conn.commit()
    conn.close()

def get_user_cars(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, marka, model, year FROM cars WHERE user_id=?", (user_id,))
    result = c.fetchall()
    conn.close()
    return result

def add_service(car_id, service_date, oil_brand, oil_liters, oil_filter, air_filter, cabin_filter, greasing_done, comment):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO service_requests
        (car_id, service_date, oil_brand, oil_liters, oil_filter, air_filter, cabin_filter, greasing_done, comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (car_id, service_date, oil_brand, oil_liters, oil_filter, air_filter, cabin_filter, greasing_done, comment))
    conn.commit()
    conn.close()

def get_service_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT c.marka, c.model, c.year, s.service_date, s.oil_brand, s.oil_liters,
               s.oil_filter, s.air_filter, s.cabin_filter, s.greasing_done, s.comment
        FROM service_requests s
        JOIN cars c ON s.car_id = c.id
        WHERE c.user_id = ?
        ORDER BY s.service_date DESC
    ''', (user_id,))
    result = c.fetchall()
    conn.close()
    return result

def get_all_services():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT u.name, c.marka, c.model, c.year, s.service_date, s.oil_brand, s.oil_liters,
               s.oil_filter, s.air_filter, s.cabin_filter, s.greasing_done, s.comment
        FROM service_requests s
        JOIN cars c ON s.car_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY s.service_date DESC
    ''')
    result = c.fetchall()
    conn.close()
    return result
