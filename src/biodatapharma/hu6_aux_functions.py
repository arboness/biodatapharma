import os

import mysql.connector
from dotenv import load_dotenv


def cargar_credenciales() -> dict[str, str]:
    """Carga las credenciales de acceso a MySQL desde el fichero .env.

    Returns:
        Un diccionario con las claves USER_SQL y PASSWORD_SQL y sus valores correspondientes.

    Raises:
        KeyError: Si USER_SQL está vacío o no existe, o si PASSWORD_SQL no está definido en el .env.
    """
    load_dotenv()
    user = os.getenv("USER_SQL")
    password = os.getenv("PASSWORD_SQL")
    if not user or password is None:
        raise KeyError("Faltan USER_SQL o PASSWORD_SQL en el .env")
    return {"USER_SQL": user, "PASSWORD_SQL": password}

def nombre_base_de_datos() -> str:
    """Obtiene el nombre de la base de datos definido en el fichero .env.

    Returns:
        El nombre de la base de datos indicado en la variable DATABASE, o None si no está definida o está vacía.
    """
    load_dotenv()
    bd = os.getenv("DATABASE")
    if not bd:
        return None
    return bd

def conectar_sql(user: str, password: str, db: str | None):
    """Abre una conexión con el servidor MySQL local.

    Args:
        user: Nombre de usuario de MySQL.
        password: Contraseña del usuario.
        db: Nombre de la base de datos a la que conectarse. Si es None, se conecta al servidor sin seleccionar ninguna base de datos.

    Returns:
        Un objeto de conexión de mysql.connector abierto contra localhost:3306.
    """
    if db is None:
        return mysql.connector.connect(
        host="localhost",
        port=3306,
        user=user,
        password=password,
    )
        
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user=user,
        password=password,
        database=db,
    )

    
def leer_sql(path):
    """Lee el contenido de un fichero .sql.

    Args:
        path: Ruta al fichero SQL.

    Returns:
        El contenido del fichero como una cadena de texto.
    """
    with open(path, encoding="utf-8") as f:
        return f.read()