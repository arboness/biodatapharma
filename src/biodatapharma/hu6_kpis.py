import mysql.connector
from dotenv import load_dotenv

from biodatapharma.hu6_aux_functions import cargar_credenciales, conectar_sql, leer_sql, nombre_base_de_datos

SQL_PATH = "src/biodatapharma/hu6_kpis.sql"

def main()->int:
    try:
        dict_credenciales = cargar_credenciales()
        credenciales = cargar_credenciales()
        db = nombre_base_de_datos()
        if db is None:
            raise mysql.connector.Error
        conn = conectar_sql(
            user=credenciales["USER_SQL"],
            password=credenciales["PASSWORD_SQL"],
            db=db
        )
        sentencia_sql = leer_sql(SQL_PATH)
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
        

    