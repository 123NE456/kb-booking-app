import sqlite3
import os

DB_PATH = "database.db"

# Supprimer l'ancienne DB si elle existe
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Ancienne base supprimée ✅")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Table messages
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    subject TEXT,
    message TEXT
)
""")

# Table reservations
c.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    hairstyle TEXT,
    date TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()
print("Tables messages et reservations créées avec succès !")
