from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from biodatapharma.hu6_aux_functions import cargar_credenciales, conectar_sql, leer_sql, nombre_base_de_datos
import logging

logger = logging.getLogger(__name__)


def kpis() -> int:
    try:
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
    except FileNotFoundError as e:
        logger.error("Error al cargar el archivo: %s", e)
        return 1
    except KeyError as e:
        logger.error("Error al cargar las credenciales: falta la clave %s", e)
        return 2
    except mysql.connector.Error as e:
        logger.exception("Error al conectarse a la base de datos: %s", e)
        return 3

    logger.info("KPIs calculados correctamente en la base de datos %s", db)
    return 0

        

    