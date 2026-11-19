import logging

import requests
import math
import pandas as pd
from biodatapharma.constants import DISEASE_NAME, COLUMN_URL, HEADERS, HU1_FILE_NAME, HU2_FILE_NAME, HU3_FILE_NAME, NOMENCLATOR_COLUMNS, NOMENCLATOR_FILE_NAME
from tqdm import tqdm

from biodatapharma.hu1_aux_functions import extract_drug_details
from biodatapharma.hu2 import calc_metrics

logger = logging.getLogger(__name__)

METRICAS_VACIAS = {"palabras_seccion_4_4": None, "num_tablas": None, "num_grave": None}

def pages_number(disease: str) -> int:
    """Calcula el número de páginas que se deben de obtener de la API para conseguir todos los registros de la enfermedad.

    Args:
        disease: nombre de la enfermedad.

    Returns:
        El total de páginas
    """
    r = requests.post(
        "https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina=1",
        json=[
            {
                "seccion": "4.1",
                "texto": disease,
                "contiene": 1
            }
        ],
        timeout=10,
    )
    r.raise_for_status()
    datos = r.json()
    page_size = datos.get("tamanioPagina")
    nregisters = datos.get("totalFilas")
    total_pages = math.ceil(nregisters/page_size)
    return total_pages


def extract_register_numbers(disease: str) -> list[str]:
    """Obtiene todos los números de registro de lso fármacos de una enfermedad concreta

    Args:
        disease: nombre de la enfermedad.

    Returns:
        Un array con los números de registros
    """
    nrecords = []
    
    num_pages = pages_number(disease=disease)
    for page in range(1, num_pages+1):
        
        r = requests.post(
            f"https://cima.aemps.es/cima/rest/buscarEnFichaTecnica",
            json=[
                {
                    "seccion": "4.1",
                    "texto": disease,
                    "contiene": 1
                }
            ],
            params={
                "pagina": page
            },
            timeout=10,
        )
        r.raise_for_status()
        datos = r.json()
        nrecords.extend(m["nregistro"] for m in datos["resultados"])
        
    return nrecords    

def drugs_to_xlsx(drug_register_numbers: list[str]):
    """Dado un listado de números de registro, se crea un xlsx con finromación relevante sobre ellos.

    Args:
        drug_register_numbers: lista con los números de registro de los medicamentos.

    """
    
    drug_info_dicts = [] 
    for register_number in tqdm(drug_register_numbers, desc="Medicamentos"):
        drug_dict = extract_drug_details(register_number)
        if drug_dict is not None:
            drug_info_dicts.append(drug_dict)

    df = pd.DataFrame(drug_info_dicts)
    df.to_excel(HU1_FILE_NAME, index=False)  
    return df
     
def extract_and_export_register_numbers() -> None:
    nrecords = extract_register_numbers(disease=DISEASE_NAME)
    logger.info("Encontrados %d números de registro para '%s'", len(nrecords), DISEASE_NAME)
    df = drugs_to_xlsx(nrecords)
    logger.info("HU1 guardada en %s (%d medicamentos)", HU1_FILE_NAME, len(df))
    return df


def aggregated_metrics() -> None:
    df = extract_and_export_register_numbers()
    rows = []
    for url in tqdm(df[COLUMN_URL], desc="Urls"):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            rows.append(calc_metrics(resp.text))
        except Exception as e:
            fallos += 1
            logger.warning("Ficha omitida (%s): %s", url, e)
            rows.append(METRICAS_VACIAS.copy())

    metricas = pd.DataFrame(rows, index=df.index)
    df = df.join(metricas)
    df.to_excel(HU2_FILE_NAME, index=False)
    logger.info("HU2 guardada en %s (%d filas, %d columnas)", HU2_FILE_NAME, *df.shape)

    return df


def extract_nomenclator() -> None:
    df_nomenclator = pd.read_csv(NOMENCLATOR_FILE_NAME)
    df_HU2 = aggregated_metrics()
    df_HU2 = pd.read_excel(HU2_FILE_NAME)
    df_nomenclator_filtered = df_nomenclator[NOMENCLATOR_COLUMNS].copy()
    df_HU2['cn'] = pd.to_numeric(df_HU2["cn"], errors='coerce').astype("Int64")
    df_HU3 = df_HU2.merge(
        df_nomenclator_filtered,
        left_on="cn",
        right_on="Código Nacional",
        how="left",
    )

    sin_match = df_HU3["Código Nacional"].isna().sum()
    if sin_match:
        logger.warning("%d medicamentos sin coincidencia en el Nomenclátor", sin_match)

    df_HU3 = df_HU3.drop(columns=["Código Nacional"])

    df_HU3.to_excel(HU3_FILE_NAME, index=False)
    logger.info("HU3 guardada en %s (%d filas)", HU3_FILE_NAME, len(df_HU3))

    return 0