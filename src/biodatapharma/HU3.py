import pandas as pd
import os

#Importar  las archivos csv y xlsx y convertirlos en df
df_eco=pd.read_csv(
    "20260924_Nomenclator_de_Facturacion.csv",
    encoding="utf-8",
    sep=",",
    )
df_medicos=pd.read_excel("HU2_esquizofrenia.xlsx")

#Mostramos las primeras 5 filas de cada una de los data frames
print(df_medicos.head())
print("\n")
print(df_medicos.head())


#Extraemos los datos de valor del archivo proveniente de los 
var_eco = df_eco[[
    'Código Nacional',
    'Estado',
    'Precio venta al público con IVA',
    'Precio de referencia',
    'Tratamiento de larga duración',
    'Especial control médico'
]]


#Crear un nuevo data frame que contenga las variables de interés de ambos archivos
df_completo=pd.merge(
    df_medicos,
    var_eco,
    left_on='cn', 
    right_on='Código Nacional', 
    how='left'
)
print(df_medicos.head())

##La clave de unión de mabas tablas es el código nacional y alamacenará unicamente los cn únicos que se almacenan en la tabla de los datos medcamentos a pesar de que esta no cuente conregistro en el archivo de datos económicos

#Solo falta crear un nuevo archivo xlsx que contenga los datos de la nueva tabla creada
df_completo.to_excel("Catalogo_Medicamentos_Completo.xlsx", index=False)
