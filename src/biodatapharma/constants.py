from pathlib import Path


DISEASE_NAME = "esquizofrenia"

DATA_DIR = Path("data")

LOG_DIR = Path(__file__).resolve().parents[2] / "log"
LOG_FILE = LOG_DIR / "schezofrenia_esquizofrenia.log"

HEADERS = {"User-Agent": "BIODATAPHARMA/1.0 (proyecto academico ICAI)"}

HU1_FILE_NAME = DATA_DIR / "hu1_esquizofrenia.xlsx"
CIMA_MEDICAMENTO_URL = "https://cima.aemps.es/cima/rest/medicamento"
         
HU2_FILE_NAME = DATA_DIR / "hu2_esquizofrenia.xlsx"
COLUMN_URL = "url_ficha_tecnica"

NOMENCLATOR_FILE_NAME = DATA_DIR / "nomenclator.csv"
HU3_FILE_NAME = DATA_DIR / "hu3_esquizofrenia.xlsx"
NOMENCLATOR_COLUMNS = [
    'Código Nacional',
    'Estado',
    'Precio venta al público con IVA',
    'Precio de referencia',
    'Tratamiento de larga duración',
    'Especial control médico'
]

HU4_FILE_NAME_SIN_ESCALAR = DATA_DIR / "hu4_esquizofrenia_limpio_sin_escalar.csv"
HU4_FILE_NAME_LIMPIO = DATA_DIR / "hu4_esquizofrenia_limpio.csv"

HU5_FILE_NAME = DATA_DIR / "hu5_clusters.csv"
HU5_FILE_NAME_RECONSTRUIDO = DATA_DIR / "hu5_clusters_reconstruido.csv"

SQL_PATH = Path(__file__).resolve().parents[2] / "sql" / "hu6_kpis.sql"




