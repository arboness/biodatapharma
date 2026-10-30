"""
BIODATAPHARMA · HU-4 · Limpieza y transformación del dataset de esquizofrenia

Aplica las conclusiones del EDA para dejar el dataset listo para el modelo K-Means (HU-5).

Entrada:
    hu3_esquizofrenia.xlsx  -> 1.013 medicamentos x 31 columnas (salida de la HU-3)

Salidas:
    hu4_esquizofrenia_limpio.csv              -> dataset para el K-Means (numérico y escalado)
    hu4_esquizofrenia_limpio_sin_escalar.csv  -> mismo dataset con valores reales (para interpretar)

Versión A del modelo: todas las columnas. Versión B: sin la columna tld_unknown.
"""

import re

import pandas as pd
from sklearn.preprocessing import RobustScaler


# ---------------------------------------------------------------
# 0. Cargar los datos
# ---------------------------------------------------------------
df = pd.read_excel("data/hu3_esquizofrenia.xlsx")
print("Dataset original:", df.shape)

# Fecha fija de referencia (descarga de CIMA y del Nomenclátor)
FECHA_REFERENCIA = pd.Timestamp("2026-09-27")


# ---------------------------------------------------------------
# 1. Duplicados e identificador
# ---------------------------------------------------------------
# Las autorizaciones europeas tienen un nregistro por envase:
# dejamos una sola fila por nombre + laboratorio titular.
# Ordenamos para que la presentación comercializada quede primero y sea la que se conserva.
df = df.sort_values("comercializado", ascending=False)
df = df.drop_duplicates(subset=["nombre", "labtitular"])
df = df.sort_index()
print("Tras quitar duplicados:", df.shape)

# nregistro es el identificador (no entra en el modelo).
# Eliminamos el resto de identificadores y URLs.
df = df.drop(columns=["cn", "nombre", "url_ficha_tecnica", "url_foto_materiales"])


# ---------------------------------------------------------------
# 2. Columnas sin variación (no aportan información al modelo)
# ---------------------------------------------------------------
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


# ---------------------------------------------------------------
# 3. Fechas
# ---------------------------------------------------------------
# estado_aut (fecha de autorización) -> antigüedad en años
fecha_autorizacion = pd.to_datetime(df["estado_aut"])
df["antiguedad_anios"] = (FECHA_REFERENCIA - fecha_autorizacion).dt.days / 365.25

# estado_rev es la fecha de REVOCACIÓN: si tiene fecha, el medicamento está revocado
df["revocado"] = df["estado_rev"].notna().astype(int)

df = df.drop(columns=["estado_aut", "estado_rev"])


# ---------------------------------------------------------------
# 4. Valores nulos
# ---------------------------------------------------------------
# 4.1 Laboratorio comercializador: los 3 nulos son Aripiprazol Zentiva
df["labcomercializador"] = df["labcomercializador"].fillna("Zentiva K.S.")

# 4.2 Tratamiento de larga duración: el nulo indica que no hay dato del Nomenclátor
df["tld_unknown"] = df["Tratamiento de larga duración"].isna().astype(int)
df = df.drop(columns=["Tratamiento de larga duración"])

# 4.3 Precio: nos quedamos solo con el PVP con IVA (correlación 1,00 con el de referencia)
df = df.rename(columns={"Precio venta al público con IVA": "pvp"})
df = df.drop(columns=["Precio de referencia"])

# Unificamos las sales del principio activo: "QUETIAPINA FUMARATO" -> "QUETIAPINA"
df["pa_base"] = df["pactivos"].str.split().str[0]
df = df.drop(columns=["pactivos"])

# Rellenamos el precio en tres pasos, de más concreto a más general:
#   1) mediana del mismo principio activo y misma forma farmacéutica
#   2) mediana de la misma forma farmacéutica
#   3) mediana general
mediana_pa_forma = df.groupby(["pa_base", "forma_farmaceutica_simplificada"])["pvp"].transform("median")
mediana_forma = df.groupby("forma_farmaceutica_simplificada")["pvp"].transform("median")

df["pvp"] = df["pvp"].fillna(mediana_pa_forma)
df["pvp"] = df["pvp"].fillna(mediana_forma)
df["pvp"] = df["pvp"].fillna(df["pvp"].median())


# ---------------------------------------------------------------
# 5. Dosis: de texto libre a número en mg
# ---------------------------------------------------------------
def extraer_dosis(texto):
    """Devuelve la dosis en mg (o mg/ml si es una concentración)."""
    texto = texto.lower().replace(",", ".")

    if "desconocida" in texto:              # Zyprexa: dosis estándar de 10 mg
        return 10.0

    numeros = [float(n) for n in re.findall(r"\d+\.?\d*", texto)]

    if "%" in texto:                        # "4 %" = 4 g / 100 ml = 40 mg/ml
        return numeros[0] * 10
    if "100 ml" in texto:                   # "200 mg / 100 ml" = 2 mg/ml
        return numeros[0] / 100
    if "ml" in texto:                       # "20 mg/ml" -> 20
        return numeros[0]
    if "+" in texto or len(numeros) > 1:    # packs de paliperidona "100 mg + 150 mg" -> suma
        return sum(numeros)
    return numeros[0]                       # caso normal: "10 mg" -> 10


df["dosis_mg"] = df["dosis"].apply(extraer_dosis)

# Las concentraciones (mg/ml) no se pueden comparar con los comprimidos: las marcamos
df["dosis_es_concentracion"] = df["dosis"].str.lower().str.contains("ml|%").astype(int)

df = df.drop(columns=["dosis"])


# ---------------------------------------------------------------
# 6. Variables categóricas
# ---------------------------------------------------------------
# Agrupamos las categorías poco frecuentes en "OTROS"
conteo_pa = df["pa_base"].value_counts()
pa_frecuentes = conteo_pa[conteo_pa >= 10].index
df["pa_base"] = df["pa_base"].where(df["pa_base"].isin(pa_frecuentes), "OTROS")

conteo_lab = df["labcomercializador"].value_counts()
lab_frecuentes = conteo_lab[conteo_lab >= 30].index
df["labcomercializador"] = df["labcomercializador"].where(
    df["labcomercializador"].isin(lab_frecuentes), "OTROS")

# Solo usamos un laboratorio (titular y comercializador coinciden casi siempre)
df = df.drop(columns=["labtitular"])

# Guardamos una copia con valores reales, antes del one-hot y del escalado
df.to_csv("data/hu4_esquizofrenia_limpio_sin_escalar.csv", index=False)

# One-hot: cada categoría pasa a ser una columna 0/1
df = pd.get_dummies(
    df,
    columns=["forma_farmaceutica_simplificada", "vias_administracion", "Estado",
             "pa_base", "labcomercializador"],
    dummy_na=False,
    dtype=int,
)


# ---------------------------------------------------------------
# 7. Escalado de las variables numéricas
# ---------------------------------------------------------------
# RobustScaler usa la mediana y el rango intercuartílico,
# así los valores extremos no deforman la escala.
numericas = ["antiguedad_anios", "pvp", "dosis_mg", "num_excipientes",
             "palabras_seccion_4_4", "num_tablas", "num_grave"]

scaler = RobustScaler()
df[numericas] = scaler.fit_transform(df[numericas])


# ---------------------------------------------------------------
# 8. Comprobaciones y guardado
# ---------------------------------------------------------------
print("Nulos restantes:", df.isna().sum().sum())
print("Columnas de texto restantes:", list(df.select_dtypes(exclude="number").columns))

df.to_csv("data/hu4_esquizofrenia_limpio.csv", index=False)
print("Dataset final:", df.shape)