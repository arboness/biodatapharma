import sys
import mysql.connector
import pandas as pd

from biodatapharma.hu6_aux_functions import cargar_credenciales, conectar_sql, nombre_base_de_datos

CSV_PATH = "data/hu5_completo_v4.csv"

BOOL_COLS = ["comercializado", "generico", "revocado", "tld_unknown", "dosis_es_concentracion",]
INT_COLS = ["num_excipientes", "palabras_seccion_4_4", "num_tablas", "num_grave", "cluster", "num_principios_activos",]


def preparar_datos() -> tuple[list[str], list[list]]:
    df = pd.read_csv(CSV_PATH, dtype={"nregistro": str})
    
    df[BOOL_COLS] = df[BOOL_COLS].astype("boolean")

    df[INT_COLS] = df[INT_COLS].astype("Int64")

    datos = df.astype(object).values.tolist()
    
    return list(df.columns), datos


def main() -> int:
    conn = None
    try:
        credenciales = cargar_credenciales()
        columnas, datos = preparar_datos()

        cols = ", ".join(columnas)
        placeholders = ", ".join(["%s"] * len(columnas))
        insert_query = f"INSERT INTO medicamentos ({cols}) VALUES ({placeholders})"
        db = nombre_base_de_datos()
        if db is None:
            raise mysql.connector.Error
        conn = conectar_sql(
            user=credenciales["USER_SQL"],
            password=credenciales["PASSWORD_SQL"],
            db = db
        )
        cursor = conn.cursor()
        cursor.executemany(insert_query, datos)
        cursor.close()
        conn.commit()
    except FileNotFoundError as e:
        print(f"ERROR AL CARGAR EL CSV: {e}")
        return 1
    except KeyError as e:
        print(f"ERROR AL CARGAR LAS CREDENCIALES O COLUMNAS: {e}")
        return 2
    except mysql.connector.Error as e:
        if conn is not None and conn.is_connected():
            conn.rollback()
        print(f"ERROR EN LA BASE DE DATOS: {e}")
        return 3
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

    print(f"Insertadas {len(datos)} filas en medicamentos")
    return 0


if __name__ == "__main__":
    sys.exit(main())