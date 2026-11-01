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

df = pd.read_excel("data/hu3_esquizofrenia.xlsx")
print("Dataset original:", df.shape)

FECHA_REFERENCIA = pd.Timestamp("2026-09-27")

# 1. Duplicados: se conserva la presentación comercializada
df = df.sort_values("comercializado", ascending=False)
df = df.drop_duplicates(subset=["nombre", "labtitular"])
df = df.sort_index()
print("Tras quitar duplicados:", df.shape)

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
def extraer_dosis(texto):
    """Devuelve la dosis en mg (o mg/ml si es una concentración)."""
    texto = texto.lower().replace(",", ".")

    if "desconocida" in texto:
        return 10.0

    numeros = [float(n) for n in re.findall(r"\d+\.?\d*", texto)]

    if "%" in texto:
        return numeros[0] * 10
    if "100 ml" in texto:
        return numeros[0] / 100
    if "ml" in texto:
        return numeros[0]
    if "+" in texto or len(numeros) > 1:
        return sum(numeros)
    return numeros[0]


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

df.to_csv("data/hu4_esquizofrenia_limpio_sin_escalar.csv", index=False)

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

# 8. Comprobaciones y guardado
print("Nulos restantes:", df.isna().sum().sum())
print("Columnas de texto restantes:", list(df.select_dtypes(exclude="number").columns))

df.to_csv("data/hu4_esquizofrenia_limpio.csv", index=False)
print("Dataset final:", df.shape)