import requests
import math
from biodatapharma.hu1_aux_functions import extract_drug_details
import pandas as pd
from biodatapharma.constants import DISEASE_NAME, DATA_DIR


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
    print(nregisters)
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
            f"https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina={page}",
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
        nrecords.extend(m["nregistro"] for m in datos["resultados"])
        
    return nrecords    

def drugs_to_xlsx(drug_register_numbers: list[str])->None:
    """Dado un listado de números de registro, se crea un xlsx con finromación relevante sobre ellos.

    Args:
        drug_register_numbers: lista con los números de registro de los medicamentos.

    """
    
    drug_info_dicts = [] 
    for register_number in drug_register_numbers:
        drug_info_dicts.append(extract_drug_details(register_number))

    df = pd.DataFrame(drug_info_dicts)
    df.to_excel(DATA_DIR / f"hu1_{DISEASE_NAME}.xlsx", index=False)  
    
    print(df.isna().sum()) 

     
def main() -> None:
    nrecords = extract_register_numbers(disease=DISEASE_NAME)
    drugs_to_xlsx(nrecords)
    print(len(nrecords))
    


if __name__ == "__main__":
    main()