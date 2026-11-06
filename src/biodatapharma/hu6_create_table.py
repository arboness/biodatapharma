import sys
import mysql.connector
from biodatapharma.hu6_aux_functions import cargar_credenciales, conectar_sql, nombre_base_de_datos

DATABASE = nombre_base_de_datos()

SENTENCIAS = [
    f"CREATE DATABASE IF NOT EXISTS {DATABASE}",
    f"USE {DATABASE}",
    "DROP TABLE IF EXISTS medicamentos",
    """
    CREATE TABLE medicamentos (
        nregistro                        VARCHAR(20) PRIMARY KEY,
        labcomercializador               TEXT,
        forma_farmaceutica_simplificada  TEXT,
        vias_administracion              TEXT,
        comercializado                   BOOLEAN,
        generico                         BOOLEAN,
        num_excipientes                  INTEGER,
        palabras_seccion_4_4             INTEGER,
        num_tablas                       INTEGER,
        num_grave                        INTEGER,
        pvp                              NUMERIC(10, 2),
        antiguedad_anios                 DOUBLE PRECISION,
        revocado                         BOOLEAN,
        tld_unknown                      BOOLEAN,
        pa_base                          TEXT,
        dosis_mg                         DOUBLE PRECISION,
        dosis_es_concentracion           BOOLEAN,
        cluster                          INTEGER,
        precio_de_referencia             NUMERIC(10, 2),
        num_principios_activos           INTEGER
    )
    """,
]


def main() -> int:
    conn = None
    try:
        credenciales = cargar_credenciales()
        conn = conectar_sql(
            user=credenciales["USER_SQL"],
            password=credenciales["PASSWORD_SQL"],
        )
        cursor = conn.cursor()
        for sentencia in SENTENCIAS:
            cursor.execute(sentencia)
        cursor.close()
        conn.commit()
    except KeyError as e:
        print(f"ERROR AL CARGAR LAS CREDENCIALES: {e}")
        return 2
    except mysql.connector.Error as e:
        print(f"ERROR EN LA BASE DE DATOS: {e}")
        return 3
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

    print("Tabla creada correctamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())