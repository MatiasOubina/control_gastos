from .db import obtener_conexion

def obtener_categorias(tipo=None, solo_activas=True):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if tipo:
        cursor.execute("SELECT * FROM categorias WHERE tipo = ? AND activa = ?", (tipo, solo_activas))
    else:
        cursor.execute("SELECT * FROM categorias WHERE activa = ?", (solo_activas,))
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_subcategorias(categoria_id: int, solo_activas=True):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM subcategorias WHERE categoria_id = ? AND activa = ?", (categoria_id, solo_activas))

    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def insertar_categoria(nombre: str, tipo:str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO categorias (nombre, tipo) VALUES(?,?)", (nombre, tipo))
    conexion.commit()

    conexion.close()

def insertar_subcategoria(categoria_id: int, nombre: str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO subcategorias (categoria_id, nombre) VALUES (?,?)", (categoria_id, nombre))
    conexion.commit()

    conexion.close()

def actualizar_categoria(id, nombre: str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE categorias SET nombre = ? WHERE id = ?", (nombre, id))
    conexion.commit()

    conexion.close()

def actualizar_subcategoria(id: int, nombre:str):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE subcategorias SET nombre = ? WHERE id = ?", (nombre, id))
    conexion.commit()

    conexion.close()

def deshabilitar_categoria(id:int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE categorias SET activa = 0 WHERE id = ?", (id,))
    cursor.execute("UPDATE subcategorias SET activa = 0 WHERE categoria_id = ?", (id,))

    conexion.commit()

    conexion.close()

def deshabilitar_subcategoria(id:int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE subcategorias SET activa = 0 WHERE id = ?", (id,))

    conexion.commit()

    conexion.close()

    
def obtener_meses():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM meses ORDER BY año DESC, mes DESC")
    resultado = cursor.fetchall()
    conexion.close()

    return [
        {
            "id": row[0],
            "año": row[1],
            "mes": row[2],
            "saldo_inicial": row[3]
        }
        for row in resultado
    ]

def obtener_mes_actual():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM meses ORDER BY año DESC, mes DESC LIMIT 1")
    resultado = cursor.fetchone()
    conexion.close()

    if resultado is None:
        return None

    return {
        "id": resultado[0],
        "año": resultado[1],
        "mes": resultado[2],
        "saldo_inicial": resultado[3]
    }

def insertar_mes(año: int, mes:int, saldo_inicial:float):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO meses (año, mes, saldo_inicial) VALUES (?,?,?)", (año, mes, saldo_inicial))
    conexion.commit()

    conexion.close()
    return cursor.lastrowid


def obtener_movimientos(mes_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT m.id, m.fecha, m.descripcion, m.monto, m.tipo, sc.nombre AS subcategoria, c.nombre AS categoria
        FROM movimientos m
        LEFT JOIN subcategorias sc ON m.subcategoria_id = sc.id
        LEFT JOIN categorias c ON m.categoria_id = c.id
        WHERE m.mes_id = ?
        ORDER BY m.fecha DESC
    """, (mes_id,))
    resultado = cursor.fetchall()
    conexion.close()

    return [
        {
            "id": row[0],
            "fecha": row[1],
            "descripcion": row[2],
            "monto": row[3],
            "tipo": row[4],
            "subcategoria": row[5],
            "categoria": row[6]
        }
        for row in resultado
    ]


def insertar_movimiento(mes_id: int, fecha: str, categoria_id: int, subcategoria_id: int,
                        descripcion: str, monto: float, tipo: str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO movimientos (mes_id, fecha, categoria_id, subcategoria_id, descripcion, monto, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (mes_id, fecha, categoria_id, subcategoria_id, descripcion, monto, tipo))
    conexion.commit()

    conexion.close()
    return cursor.lastrowid


def eliminar_movimiento(movimiento_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM movimientos WHERE id = ?", (movimiento_id,))
    conexion.commit()

    conexion.close()


def obtener_resumen_mes(mes_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS total_ingresos,
            SUM(CASE WHEN tipo = 'egreso' THEN monto ELSE 0 END) AS total_egresos,
            (SELECT saldo_inicial FROM meses WHERE id = ?) +
            SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) -
            SUM(CASE WHEN tipo = 'egreso' THEN monto ELSE 0 END) AS saldo
        FROM movimientos
        WHERE mes_id = ?
    """, (mes_id, mes_id))
    resultado = cursor.fetchone()
    conexion.close()

    return {
        "total_ingresos": resultado[0] or 0.0,
        "total_egresos": resultado[1] or 0.0,
        "saldo": resultado[2] or 0.0
    }

# Retorna lista de dicts con el desglose por categoría para un mes dado.
# Cada dict: {"categoria": str, "tipo": str, "total": float}
# Ordenado: primero ingresos, luego egresos, dentro de cada grupo ordenado por total DESC
def obtener_desglose_por_categoria(mes_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT c.nombre AS categoria, c.tipo, SUM(m.monto) AS total
        FROM movimientos m
        JOIN categorias c ON m.categoria_id = c.id
        WHERE m.mes_id = ?
        GROUP BY c.id
        ORDER BY c.tipo DESC, total DESC
    """, (mes_id,))
    resultado = cursor.fetchall()
    conexion.close()

    return [
        {
            "categoria": row[0],
            "tipo": row[1],
            "total": row[2] or 0.0
        }
        for row in resultado
    ]