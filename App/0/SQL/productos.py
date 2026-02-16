print(">>> EJECUTANDO productos.py <<<")

import sqlite3
import os

# Mostrar dónde se crea la base de datos
print("BD en:", os.path.abspath("database.db"))

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL
)
""")

conn.commit()
conn.close()

print("Tabla productos creada correctamente")
