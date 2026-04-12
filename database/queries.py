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

    
