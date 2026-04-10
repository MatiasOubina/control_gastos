import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gastos.db")

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
            tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso'))
        );

        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
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
            fecha TEXT NOT NULL,
            subcategoria_id INTEGER NOT NULL,
            descripcion TEXT,
            monto REAL NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id)
        );
    """)

    conexion.commit()
    conexion.close()