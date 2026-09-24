import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------
ENTRADA = "schizofrenia_drugs.csv"          # salida de la HU-1
SALIDA = "HU2_esquizofrenia.xlsx"
COLUMNA_URL = "url_ficha_tecnica"
HEADERS = {"User-Agent": "BIODATAPHARMA/1.0 (proyecto academico ICAI)"}


# ----------------------------------------------------------------------
# Métricas: cada una recibe el HTML ya parseado (soup)
# ----------------------------------------------------------------------
def palabras_seccion_4_4(soup):
    """Volumen informativo de seguridad: nº de palabras de la sección 4.4.

    En las fichas de CIMA cada sección empieza con <h2 id="4.4">, <h2 id="4.5">...
    Recorremos los elementos que van después del título 4.4 hasta el siguiente <h2>.
    El título de la sección no se cuenta.
    """
    titulo = soup.find("h2", id="4.4")
    if titulo is None:
        return None                      # ficha sin sección 4.4 → NaN

    texto = ""
    for elemento in titulo.find_next_siblings():
        if elemento.name == "h2":        # hemos llegado a la 4.5 → paramos
            break
        texto += " " + elemento.get_text(" ")

    # Palabra = secuencia de letras y/o números (ignora signos de puntuación sueltos)
    return len(re.findall(r"\w+", texto))


def numero_tablas(soup):
    """Complejidad del desglose clínico: nº de etiquetas <table> en todo el HTML."""
    return len(soup.find_all("table"))


def numero_grave(soup):
    """Indicador de riesgo severo: nº de veces que aparece "grave" o "graves".

    \\b = límite de palabra → NO cuenta "gravedad" ni "gravemente".
    re.IGNORECASE → cuenta también "Grave" y "GRAVES".
    """
    texto = soup.get_text(" ")
    return len(re.findall(r"\bgraves?\b", texto, flags=re.IGNORECASE))


def calcular_metricas(html):
    soup = BeautifulSoup(html, "lxml")
    for etiqueta in soup(["script", "style"]):   # quitamos código JS/CSS, no es texto
        etiqueta.decompose()
    return {
        "palabras_seccion_4_4": palabras_seccion_4_4(soup),
        "num_tablas": numero_tablas(soup),
        "num_grave": numero_grave(soup),
    }


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Leemos la salida de la HU-1
    df = pd.read_csv(ENTRADA)
    print("Medicamentos a procesar:", len(df))

    # 2. Descargamos cada ficha y calculamos las métricas
    filas = []
    for i, (nregistro, url) in enumerate(zip(df["nregistro"], df[COLUMNA_URL]), start=1):
        fila = {"nregistro": nregistro,
                "palabras_seccion_4_4": None, "num_tablas": None, "num_grave": None}

        if pd.notna(url):
            try:
                respuesta = requests.get(url, headers=HEADERS, timeout=30)
                respuesta.raise_for_status()
                fila.update(calcular_metricas(respuesta.content))
            except Exception as e:
                print("Error con", nregistro, "→", e)

        filas.append(fila)
        if i % 50 == 0:
            print("Llevamos", i, "de", len(df))
        time.sleep(0.2)                  # pequeña pausa para no saturar la web de la AEMPS

    metricas = pd.DataFrame(filas)

    # 3. Resumen para comprobar que todo ha ido bien
    print("\nFichas procesadas:", metricas["num_tablas"].notna().sum(), "de", len(metricas))
    print("Sin sección 4.4:", metricas["palabras_seccion_4_4"].isna().sum())
    print(metricas[["palabras_seccion_4_4", "num_tablas", "num_grave"]].describe())

    # 4. Unimos las 3 métricas a los datos de la HU-1 y guardamos
    resultado = df.merge(metricas, on="nregistro", how="left")
    resultado.to_excel(SALIDA, index=False)
    print("\nGuardado en", SALIDA, "→", resultado.shape)
