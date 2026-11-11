import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from biodatapharma.constants import DATA_DIR


INPUT_NAME = "hu1_esquizofrenia.xlsx"          
OUTPUT_NAME = "hu2_esquizofrenia.xlsx"
COLUMN_URL = "url_ficha_tecnica"
HEADERS = {"User-Agent": "BIODATAPHARMA/1.0 (proyecto academico ICAI)"}

def words_section(soup: BeautifulSoup, section: str)->int:
    """Obtiene el número de palabras de una sección dado un html en formato BeautifulSoup.

    Args:
        soup: HTML formato BeautifulSoup.
        section: String con el número de sección para la que se van a contar las palabras.

    Returns:
        Un entero con el número de palabras contadas.
    """
    
    section_title = soup.find(id=section)
    if section_title is None:
        return None                      

    text = ""
    for element in section_title.find_next_siblings():
        text =  element.get_text(" ")
        if element.name != "p":   
            return  len(re.findall(r"\w+", text))
        text += " " + element.get_text(" ")

def tables_number(soup: BeautifulSoup)-> int:
    """Obtiene el número de tablas de un html en formato BeautifulSoup.

    Args:
        soup: HTML formato BeautifulSoup.

    Returns:
        Un entero con el número de tablas encontradas.
    """
    return len(soup.find_all("table"))


def grave_occurences(soup: BeautifulSoup)-> int:
    """Obtiene el número de ocurrencias de la palabra grave/graves de un html en formato BeautifulSoup.

    Args:
        soup: HTML formato BeautifulSoup.

    Returns:
        Un entero con el número de ocurrencias de la palabra grave/graves encontradas.
    """
    texto = soup.get_text(" ")
    return len(re.findall(r"\bgraves?\b", texto, flags=re.IGNORECASE))


def calcular_metricas(html: str) -> dict:
    """Hace uso de una serie de funciones previamente definidas para extraer unas métricas dado un html.

    Args:
        html: HTML crudo.

    Returns:
        Un diccionario con el número de palabras en la sección dada, número de tablas y número de ocurrencias de la palabra grave/graves.
    """
    
    soup = BeautifulSoup(html, "lxml")
    for etiqueta in soup(["script", "style"]):   
        etiqueta.decompose()
    return {
        "palabras_seccion_4_4": words_section(soup, section="4.4"),
        "num_tablas": tables_number(soup),
        "num_grave": grave_occurences(soup),
    }

def main() -> None:
    df = pd.read_excel(DATA_DIR / INPUT_NAME)
    rows=[]
    for url in tqdm(df[COLUMN_URL], desc="Urls"):
        
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        rows.append(calcular_metricas(resp.text))

    metricas = pd.DataFrame(rows, index=df.index)
    df = df.join(metricas)
    df.to_excel(DATA_DIR / OUTPUT_NAME, index=False)    
    
if  __name__ == "__main__":
    main()