"""
BIODATAPHARMA - HU-4: limpieza y transformación del dataset de esquizofrenia.

Aplica las conclusiones del EDA al fichero de la HU-3 para dejarlo listo
para el modelo K-Means de la HU-5.

Entrada:  data/hu3_esquizofrenia.xlsx
Salidas:  data/hu4_esquizofrenia_limpio.csv
          data/hu4_esquizofrenia_limpio_sin_escalar.csv
"""

import re

import pandas as pd
from sklearn.preprocessing import RobustScaler

RUTA_ENTRADA = "data/hu3_esquizofrenia.xlsx"
RUTA_SALIDA_SIN_ESCALAR = "data/hu4_esquizofrenia_limpio_sin_escalar.csv"
RUTA_SALIDA = "data/hu4_esquizofrenia_limpio.csv"

FECHA_REFERENCIA = pd.Timestamp.today().normalize()


# 5. Dosis: de texto a número en mg (o mg/ml)
def extraer_dosis(texto: str) -> float:
    """Devuelve la dosis en mg, o en mg/ml si es una concentración.

    Si la dosis viene en porcentaje se multiplica por 10: 4 % son 4 g / 100 ml;
    para pasarlo a mg/ml hay que multiplicar por 1000 y dividir entre 100, que
    es lo mismo que multiplicar por 10.

    Args:
        texto: dosis en texto libre, tal como aparece en CIMA.

    Returns:
        La dosis numérica en mg (o mg/ml).
    """
    texto = texto.lower().replace(",", ".")
    numeros = []
    # única fila: Zyprexa 10 mg
    if "desconocida" in texto:
        return 10.0

    # \d es un número. Un número o más, seguidos de un punto o no con 0 o más números después del punto
    for n in re.findall(r"\d+\.?\d*", texto):
        numeros.append(float(n))
    # g/100ml, hay que multiplicar por 1000 y dividir entre 100 -> multiplicar por 10
    if "%" in texto:
        return numeros[0] * 10

    # Caso de haloperidol, que aparece la concentración por 100ml, pero en realidad son 200mg/100 ml
    # Dividimos 200 entre 100 para dar la concentración por 1ml
    if "100 ml" in texto:
        return numeros[0] / 100

    # No está ni en % ni en 100ml, se devuelve el número
    if "ml" in texto:
        return numeros[0]

    # Son varias concentraciones, se devuelve la suma de ellas
    if "+" in texto or len(numeros) > 1:
        return sum(numeros)

    # Si no, devuelve el primer número (único)
    return numeros[0]


def main() -> None:
    """Limpia y transforma el dataset de la HU-3 y guarda las versiones sin escalar y escalada."""
    df = pd.read_excel(RUTA_ENTRADA)
    print("Dataset original:", df.shape)

    # 1. Duplicados: se conserva la presentación comercializada
    df = df.sort_values("comercializado", ascending=False)
    df = df.drop_duplicates(subset=["nombre", "labtitular"])
    df = df.sort_index()

    # 2. Identificadores y columnas sin variación
    df = df.drop(columns=["cn", "nombre", "url_ficha_tecnica", "url_foto_materiales"])
    df = df.drop(columns=[
        "requiere_receta",
        "afecta_conduccion",
        "medicamento_huerfano",
        "biosimilar",
        "triangulo_negro",
        "num_principios_activos",
        "num_registros_atc",
        "Especial control médico",
    ])

    # 3. Fechas
    fecha_autorizacion = pd.to_datetime(df["estado_aut"])
    df["antiguedad_anios"] = (FECHA_REFERENCIA - fecha_autorizacion).dt.days / 365.25
    df["revocado"] = df["estado_rev"].notna().astype(int)
    df = df.drop(columns=["estado_aut", "estado_rev"])

    # 4. Nulos
    df["labcomercializador"] = df["labcomercializador"].fillna("Zentiva K.S.")

    df["tld_unknown"] = df["Tratamiento de larga duración"].isna().astype(int)
    df = df.drop(columns=["Tratamiento de larga duración"])

    df = df.rename(columns={"Precio venta al público con IVA": "pvp"})
    df = df.drop(columns=["Precio de referencia"])

    df["pa_base"] = df["pactivos"].str.split().str[0]
    df = df.drop(columns=["pactivos"])

    mediana_pa_forma = df.groupby(["pa_base", "forma_farmaceutica_simplificada"])["pvp"].transform("median")
    mediana_forma = df.groupby("forma_farmaceutica_simplificada")["pvp"].transform("median")

    df["pvp"] = df["pvp"].fillna(mediana_pa_forma)
    df["pvp"] = df["pvp"].fillna(mediana_forma)
    df["pvp"] = df["pvp"].fillna(df["pvp"].median())

    # 5. Dosis: de texto a número en mg (o mg/ml)
    df["dosis_mg"] = df["dosis"].apply(extraer_dosis)
    df["dosis_es_concentracion"] = df["dosis"].str.lower().str.contains("ml|%").astype(int)
    df = df.drop(columns=["dosis"])

    # 6. Categóricas: categorías poco frecuentes a OTROS
    conteo_pa = df["pa_base"].value_counts()
    pa_frecuentes = conteo_pa[conteo_pa >= 10].index
    df["pa_base"] = df["pa_base"].where(df["pa_base"].isin(pa_frecuentes), "OTROS")

    conteo_lab = df["labcomercializador"].value_counts()
    lab_frecuentes = conteo_lab[conteo_lab >= 30].index
    df["labcomercializador"] = df["labcomercializador"].where(
        df["labcomercializador"].isin(lab_frecuentes), "OTROS")

    df = df.drop(columns=["labtitular"])

    df.to_csv(RUTA_SALIDA_SIN_ESCALAR, index=False)

    # One-hot
    df = pd.get_dummies(
        df,
        columns=["forma_farmaceutica_simplificada", "vias_administracion", "Estado",
                 "pa_base", "labcomercializador"],
        dummy_na=False,
        dtype=int,
    )

    # 7. Escalado
    numericas = ["antiguedad_anios", "pvp", "dosis_mg", "num_excipientes",
                 "palabras_seccion_4_4", "num_tablas", "num_grave"]
    df[numericas] = RobustScaler().fit_transform(df[numericas])

    df.to_csv(RUTA_SALIDA, index=False)
    print("Dataset final:", df.shape)


if __name__ == "__main__":
    main()