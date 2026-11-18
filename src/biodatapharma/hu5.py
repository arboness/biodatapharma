from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging

from biodatapharma.constants import HU4_FILE_NAME_LIMPIO, HU4_FILE_NAME_SIN_ESCALAR, HU5_FILE_NAME

"""
    Tras realizar pruebas con diferentes configuraciones para kmeans en hu5.ipynb, se llega a la conclusión de que
    usar 5 clústers porporciona el mejor grado de:
        - silueta: 0.26. Mide si cada punto del cluster está cerca de su cluster y lejos del cluster vecino.
        - inercia: La suma de las distancias al cuadrado de cada punto al centroide. Siempre baja al añadir clusters,
            por eso nos fijamos en el codo, que es el punto en donde la inercia comienza a bajar más despacio.
"""

RAIZ = Path(__file__).resolve().parents[2]

DROP_COLUMNS_TLD = ["nregistro", "tld_unknown"]

NUM_CLUSTERS = 5
N_INIT = 10
RANDOM_STATE = 42

COLUMNS = ['nregistro', 'labcomercializador', 'forma_farmaceutica_simplificada',
       'vias_administracion', 'comercializado', 'generico', 'num_excipientes',
       'palabras_seccion_4_4', 'num_tablas', 'num_grave', 'pvp',
       'antiguedad_anios', 'revocado', 'tld_unknown', 'pa_base', 'dosis_mg',
       'dosis_es_concentracion']



logger = logging.getLogger(__name__)

def cluster_kmeans() -> int:
    df = pd.read_csv(HU4_FILE_NAME_LIMPIO)
    X = df.drop(columns=DROP_COLUMNS_TLD)

    km = KMeans(n_clusters=NUM_CLUSTERS, n_init=N_INIT, random_state=RANDOM_STATE)
    etiquetas = km.fit_predict(X)
    etiquetas = km.fit_predict(X)

    conteo = pd.Series(etiquetas).value_counts().sort_index()
    logger.info("Número de clústeres: %d", km.n_clusters)
    logger.info("Medicamentos por clúster:")
    for cluster, n in conteo.items():
        logger.info("  Clúster %d: %d (%.1f%%)", cluster, n, 100 * n / len(etiquetas))

    df_clusters = df[["nregistro"]].assign(cluster=etiquetas)
    df_hu4 = pd.read_csv(HU4_FILE_NAME_SIN_ESCALAR)

    df = df_clusters.merge(
        right=df_hu4[COLUMNS],
        right_on="nregistro",
        left_on="nregistro",
    )

    df.to_csv(HU5_FILE_NAME, index=False)
    logger.info("Clustering guardado en %s (%d filas)", HU5_FILE_NAME, len(df))

    return 0