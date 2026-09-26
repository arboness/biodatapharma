import math
import requests
import pandas as pd

enfermedad = "esquizofrenia"   # <-- cambiar por la enfermedad del grupo
url = "https://cima.aemps.es/cima/rest/buscarEnFichaTecnica"
payload = [{"seccion": "4.1", "texto": "esquizofrenia", "contiene": 1}]

# 1. Pedimos la primera página para saber cuántos medicamentos hay en total
respuesta = requests.post(url, params={"pagina": 1}, json=payload).json()
total = respuesta["totalFilas"]
tamanio = respuesta["tamanioPagina"]
num_paginas = math.ceil(total / tamanio)
print("Total:", total, "| Páginas:", num_paginas)

# 2. Guardamos los nregistro de la primera página
nregistros = []
for medicamento in respuesta["resultados"]:
    nregistros.append(medicamento["nregistro"])

# 3. Pedimos el resto de páginas y seguimos guardando
for pagina in range(2, num_paginas + 1):
    
    respuesta = requests.post(url, params={"pagina": pagina}, json=payload).json()
    for medicamento in respuesta["resultados"]:
        nregistros.append(medicamento["nregistro"])
    print("Página", pagina, "→ llevamos", len(nregistros))

# 4. Comprobamos que tenemos todos
print("Esperados:", total, "| Obtenidos:", len(nregistros))

# 5. Guardamos en Excel
df = pd.DataFrame({"nregistro": nregistros})
df.to_excel(f"nregistros_{enfermedad}.xlsx", index=False)
