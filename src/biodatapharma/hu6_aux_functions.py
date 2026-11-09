import os

import mysql.connector
from dotenv import load_dotenv


def cargar_credenciales() -> dict[str, str]:
    load_dotenv()
    user = os.getenv("USER_SQL")
    password = os.getenv("PASSWORD_SQL")
    if not user or password is None:
        raise KeyError("Faltan USER_SQL o PASSWORD_SQL en el .env")
    return {"USER_SQL": user, "PASSWORD_SQL": password}

def nombre_base_de_datos() -> str:
    load_dotenv()
    bd = os.getenv("DATABASE")
    if not bd:
        return None
    return bd

def conectar_sql(user: str, password: str, db: str | None):
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
    with open(path, encoding="utf-8") as f:
        return f.read()