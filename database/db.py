import sqlite3
import os

APP_NAME = "ControlGastos"
DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# Si existe la variable de entorno CONTROL_GASTOS_ENV=development, usa la DB de test
ENV = os.environ.get("CONTROL_GASTOS_ENV", "production")
DB_NAME = "gastos_test.db" if ENV == "development" else "gastos.db"

DB_PATH = os.path.join(DATA_DIR, DB_NAME)

def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
            activa BOOLEAN DEFAULT 1             
        );

        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            activa BOOLEAN DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
                             
        );

        CREATE TABLE IF NOT EXISTS meses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            año INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            saldo_inicial REAL DEFAULT 0,
            UNIQUE(año, mes)
        );

        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,             
            subcategoria_id INTEGER,
            descripcion TEXT,
            monto REAL NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
            FOREIGN KEY (mes_id) REFERENCES meses(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id)
        );
    """)

    conexion.commit()
    conexion.close()