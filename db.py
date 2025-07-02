
import sqlite3

def init_db():
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        name TEXT
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        marka TEXT,
        model TEXT,
        year TEXT,
        engine TEXT,
        transmission TEXT,
        mileage TEXT
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        service_date TEXT,
        oil_brand TEXT,
        oil_liters REAL,
        oil_filter TEXT,
        air_filter TEXT,
        cabin_filter TEXT,
        greasing_done INTEGER,
        comment TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(tg_id, name):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (tg_id, name) VALUES (?, ?)", (tg_id, name))
    conn.commit()
    conn.close()

def get_user_id(tg_id):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def add_car(user_id, marka, model, year, engine, transmission, mileage):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO cars (user_id, marka, model, year, engine, transmission, mileage) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, marka, model, year, engine, transmission, mileage))
    conn.commit()
    conn.close()

def get_user_cars(user_id):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marka, model, year FROM cars WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_service(car_id, service_date, oil_brand, oil_liters, oil_filter, air_filter, cabin_filter, greasing_done, comment):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO services (
        car_id, service_date, oil_brand, oil_liters,
        oil_filter, air_filter, cabin_filter,
        greasing_done, comment
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (car_id, service_date, oil_brand, oil_liters,
          oil_filter, air_filter, cabin_filter, greasing_done, comment))
    conn.commit()
    conn.close()

def get_service_history(user_id):
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute('''
    SELECT c.marka, c.model, c.year,
           s.service_date, s.oil_brand, s.oil_liters,
           s.oil_filter, s.air_filter, s.cabin_filter,
           s.greasing_done, s.comment
    FROM services s
    JOIN cars c ON s.car_id = c.id
    WHERE c.user_id = ?
    ORDER BY s.service_date DESC
    ''', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_services():
    conn = sqlite3.connect("maslo.db")
    cur = conn.cursor()
    cur.execute('''
    SELECT u.name, c.marka, c.model, c.year,
           s.service_date, s.oil_brand, s.oil_liters,
           s.oil_filter, s.air_filter, s.cabin_filter,
           s.greasing_done, s.comment
    FROM services s
    JOIN cars c ON s.car_id = c.id
    JOIN users u ON c.user_id = u.id
    ORDER BY s.service_date DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows
