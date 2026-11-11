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
RUTA_DATOS_HU4 = RAIZ / "data" / "hu4_esquizofrenia_limpio.csv"
RUTA_DATOS_HU4_SIN_ESCALAR = RAIZ / "data" / "hu4_esquizofrenia_limpio_sin_escalar.csv"
RUTA_SALIDA = RAIZ / "data" / "hu5_clusters.csv"


DROP_COLUMNS_TLD = ["nregistro", "tld_unknown"]

NUM_CLUSTERS = 5
N_INIT = 10
RANDOM_STATE = 42

COLUMNS = ['nregistro', 'labcomercializador', 'forma_farmaceutica_simplificada',
       'vias_administracion', 'comercializado', 'generico', 'num_excipientes',
       'palabras_seccion_4_4', 'num_tablas', 'num_grave', 'pvp',
       'antiguedad_anios', 'revocado', 'tld_unknown', 'pa_base', 'dosis_mg',
       'dosis_es_concentracion']


def main() -> None:
 
    df = pd.read_csv(RUTA_DATOS_HU4)
    X = df.drop(columns=DROP_COLUMNS_TLD)
 
    km = KMeans(n_clusters=NUM_CLUSTERS, n_init=N_INIT, random_state=RANDOM_STATE)
    etiquetas = km.fit_predict(X)
    etiquetas = km.fit_predict(X)

    conteo = pd.Series(etiquetas).value_counts().sort_index()
    print(f"Número de clústeres: {km.n_clusters}")
    print("Medicamentos por clúster:")
    for cluster, n in conteo.items():
        print(f"  Clúster {cluster}: {n} ({n / len(etiquetas):.1%})")
        
    df_clusters = df[["nregistro"]].assign(cluster=etiquetas)
    df_hu4 = pd.read_csv(RUTA_DATOS_HU4_SIN_ESCALAR)

    df = df_clusters.merge(
        right=df_hu4[COLUMNS],
        right_on="nregistro",
        left_on="nregistro",
    )


    df.to_csv(RUTA_SALIDA, index=False)
 
 
if __name__ == "__main__":
    main()