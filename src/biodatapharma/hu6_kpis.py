import mysql.connector
import os
from dotenv import load_dotenv

SQL_PATH = ""

def cargar_credenciales()->dict[str,str]:
    load_dotenv() 
    user = os.getenv("USER_SQL")
    password = os.getenv("PASSWORD_SQL")
    
    return {
        "USER_SQL": user,
        "PASSWORD_SQL": password
    }
    

def conectar_sql(user: str, password: str):  
    return mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        port=3306
    )

def leer_sql():
    with open(SQL_PATH, encoding="utf-8") as f:
        return f.read()

def main()->int:
    try:
        dict_credenciales = cargar_credenciales()
        conn = conectar_sql(user=dict_credenciales.get("USER_SQL"),password=dict_credenciales.get("PASSWORD_SQL"))
        sentencia_sql = leer_sql()
        conn.cursor().execute(sentencia_sql)
        conn.commit()
    except FileNotFoundError:
        print("ERROR AL CARGAR EL ARCHIVO. ")
        return 1
    except KeyError:
        print("ERROR AL CARGAR LAS CREDENCIALES. ")
        return 2
    except mysql.connector.Error:
        print("ERROR AL CONECTARSE A LA BASE DE DATOS ")
        return 3
    
    return 0


if __name__ == "__main__":
    main()
        

    