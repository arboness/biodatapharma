import requests
import json

url = "https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina=1"

payload = json.dumps([
  {
    "seccion": "4.1",
    "texto": "esquizofrenia",
    "contiene": "1"
  }
])
headers = {
  'Cookie': 'JSESSIONID=qwvKXt2EZGjRHIgraEtWcQD5pkemS-yDwoFQLVrD_z_c71J_0J7I!962100432',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
