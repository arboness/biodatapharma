import os

import mysql.connector
from dotenv import load_dotenv


DATABASE = "schezofrenia"


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
        raise KeyError("Falta DATABASE en el .env")
    return bd

def conectar_sql(user: str, password: str):
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user=user,
        password=password,
        database=DATABASE,
    )