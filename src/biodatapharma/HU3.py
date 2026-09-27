from pathlib import Path
import pandas as pd
from biodatapharma.constants import DATA_DIR


NOMENCLATOR_COLUMNS = [
    'Código Nacional',
    'Estado',
    'Precio venta al público con IVA',
    'Precio de referencia',
    'Tratamiento de larga duración',
    'Especial control médico'
]


def main()->None:
    df_nomenclator=pd.read_csv(DATA_DIR / "20260927_Nomenclator_de_Facturacion.csv")
    df_HU2=pd.read_excel(DATA_DIR / "HU2_esquizofrenia.xlsx")
    df_nomenclator_filtered = df_nomenclator[NOMENCLATOR_COLUMNS].copy()

    df_HU3 = df_HU2.merge(
        df_nomenclator_filtered,
        left_on="cn",
        right_on="Código Nacional",
        how="left",
    )
    
    df_HU3 = df_HU3.drop(columns=['Código Nacional'])

    df_HU3.to_excel(DATA_DIR / "hu3_esquizofrenia.xlsx", index=False)   
    
if  __name__ == "__main__":
    main()   