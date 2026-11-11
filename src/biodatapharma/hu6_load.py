from pathlib import Path
import sys
import mysql.connector
import pandas as pd

from biodatapharma.hu6_aux_functions import cargar_credenciales, conectar_sql, nombre_base_de_datos

RAIZ = Path(__file__).resolve().parents[2]
RUTA_SALIDA = RAIZ / "data" / "hu5_clusters_reconstruido.csv"
RUTA_DATOS_HU3 = RAIZ / "data" / "hu3_esquizofrenia.xlsx"
RUTA_DATOS_HU5 = RAIZ / "data" / "hu5_clusters.csv"

BOOL_COLS = ["comercializado", "generico", "revocado", "tld_unknown", "dosis_es_concentracion",]
INT_COLS = ["num_excipientes", "palabras_seccion_4_4", "num_tablas", "num_grave", "cluster", "num_principios_activos",]


def preparar_datos() -> tuple[list[str], list[list]]:
    """Carga el CSV reconstruido y lo prepara para insertarlo en MySQL.

    Lee ``RUTA_SALIDA`` manteniendo ``nregistro`` como texto para no perder ceros
    a la izquierda. Convierte las columnas de ``BOOL_COLS`` al tipo booleano
    anulable de pandas y las de ``INT_COLS`` al tipo entero anulable (``Int64``),
    de forma que los nulos no conviertan esas columnas en ``float``. Por último,
    transforma el DataFrame en una lista de filas con tipos nativos de Python.

    Returns:
        Una tupla con dos elementos:
            - La lista de nombres de columna, en el mismo orden que los valores.
            - La lista de filas, donde cada fila es una lista con los valores
              de un medicamento.

    Raises:
        FileNotFoundError: Si no existe el fichero ``RUTA_SALIDA``.
        KeyError: Si alguna columna de ``BOOL_COLS`` o ``INT_COLS`` no está en el CSV.
        TypeError: Si alguna columna de ``BOOL_COLS`` o ``INT_COLS`` contiene
            valores que no se pueden convertir a booleano o a entero.
    """
    df = pd.read_csv(RUTA_SALIDA, dtype={"nregistro": str})
    
    df[BOOL_COLS] = df[BOOL_COLS].astype("boolean")

    df[INT_COLS] = df[INT_COLS].astype("Int64")

    datos = df.astype(object).values.tolist()
    
    return list(df.columns), datos




def datos_faltantes():
    """Recupera el precio de referencia y el número de principios activos y rellena sus nulos.

    Une los datos de la HU-3 con los de la HU-5 por ``nregistro`` para recuperar las
    columnas ``Precio de referencia`` y ``num_principios_activos``, que se eliminaron
    durante la transformación de la HU-4. Renombra ``Precio de referencia`` a
    ``precio_de_referencia`` e imputa sus valores nulos en cascada:

    1. Mediana del mismo principio activo y forma farmacéutica.
    2. Si no existe, mediana de la forma farmacéutica.
    3. Si tampoco existe, mediana global de la columna.

    El resultado se guarda en ``RUTA_SALIDA`` en formato CSV.

    Returns:
        None. El DataFrame resultante se escribe en ``data/hu5_clusters_reconstruido.csv``.

    Raises:
        FileNotFoundError: Si no existe ``RUTA_DATOS_HU3`` o ``RUTA_DATOS_HU5``.
        KeyError: Si falta alguna de las columnas necesarias (``nregistro``,
            ``Precio de referencia``, ``num_principios_activos``, ``pa_base`` o
            ``forma_farmaceutica_simplificada``).
    """
    df_hu3 = pd.read_excel(RUTA_DATOS_HU3)
    df_hu5 = pd.read_csv(RUTA_DATOS_HU5)

    df = df_hu5.merge(
        right=df_hu3[['nregistro','Precio de referencia', 'num_principios_activos']],
        right_on="nregistro",
        left_on="nregistro",
    )
    df = df.rename(columns={"Precio de referencia": "precio_de_referencia"})
        
    mediana_pa_forma = df.groupby(["pa_base", "forma_farmaceutica_simplificada"])["precio_de_referencia"].transform("median")
    mediana_forma = df.groupby("forma_farmaceutica_simplificada")["precio_de_referencia"].transform("median")
    

    df["precio_de_referencia"] = df["precio_de_referencia"].fillna(mediana_pa_forma)
    df["precio_de_referencia"] = df["precio_de_referencia"].fillna(mediana_forma)
    df["precio_de_referencia"] = df["precio_de_referencia"].fillna(df["precio_de_referencia"].median())

    df.to_csv(RUTA_SALIDA, index=False)
    
def main() -> int:
    conn = None
    try:
        datos_faltantes()
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