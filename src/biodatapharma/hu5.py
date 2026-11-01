from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

"""
    Tras realizar pruebas con diferentes configuraciones para kmeans en hu5.ipynb, se llega a la conclusión de que
    usar 5 clústers porporciona el mejor grado de:
        - silueta: 0.26. Mide si cada punto del cluster está cerca de su cluster y lejos del cluster vecino.
        - inercia: La suma de las distancias al cuadrado de cada punto al centroide. Siempre baja al añadir clusters,
            por eso nos fijamos en el codo, que es el punto en donde la inercia comienza a bajar más despacio.
"""

RAIZ = Path(__file__).resolve().parents[2]
RUTA_DATOS = RAIZ / "data" / "hu4_esquizofrenia_limpio.csv"
RUTA_SALIDA = RAIZ / "data" / "hu5_clusters.csv"


DROP_COLUMNS = ["nregistro"]
DROP_COLUMNS_TLD = ["nregistro", "tld_unknown"]


NUM_CLUSTERS = 5
N_INIT = 10
RANDOM_STATE = 42


def main() -> None:
 
    df = pd.read_csv(RUTA_DATOS)
    X = df.drop(columns=DROP_COLUMNS_TLD)
 
    km = KMeans(n_clusters=NUM_CLUSTERS, n_init=N_INIT, random_state=RANDOM_STATE)
    etiquetas = km.fit_predict(X)
 
    df[["nregistro"]].assign(cluster=etiquetas).to_csv(RUTA_SALIDA, index=False)
 
 
if __name__ == "__main__":
    main()