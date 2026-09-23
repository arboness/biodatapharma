import requests

from biodatapharma.api_aux_functions import extract_drug_details
import pandas as pd

TOTAL_PAG=6
page = 1
nrecords = []

while page <= TOTAL_PAG:
    
    r = requests.post(
        f"https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina={page}",
        json=[
            {
                "seccion": "4.1",
                "texto": "esquizofrenia",
                "contiene": 1
            }
        ],
        timeout=10,
    )
    r.raise_for_status()
    datos = r.json()
    page+=1
    nrecords.extend(m["nregistro"] for m in datos["resultados"])

 
nrecords = list(set(nrecords))  
print(f"Total de nregistro únicos: {len(nrecords)}")
print(nrecords[0:5])

records = []
for nrecord in nrecords:
    records.append(extract_drug_details(nrecord))
 
df = pd.DataFrame(records) 
print(df)

df.to_csv("schizofrenia_drugs.csv", index=False)