## Máster Universitario en Inteligencia Artificial Aplicada Historias de Usuario

## Índice

## 1. Historia de Usuario (HU-1)

## 1.1. Como

Manager del proyecto.

## 1.2. Quiero

## Que las consultoras:

- Implementen un script en Python para interactuar con la API del Centro de Información Online de Medicamentos de la AEMPS (CIMA).

- o Realizar una primera llamada inicial de tipo POST consultando el servicio https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina=1 configurando el payload para obtener el nregistro para cada uno de los medicamentos en base a la enfermedad asignada. El Payload debe configurarse: [URL 🔗](https://cima.aemps.es/cima/rest/buscarEnFichaTecnica?pagina=1)

[{

"seccion": "4.1",

"texto": "enfermedad",

"contiene": 1

}]


- Nota: La url únicamente selecciona los resultados de la primera página, el valor que devuelve totalFilas es el número total de registros por lo que habrá que obtener todos lo registros que indique dicho número.

- o Una vez obtenido el nregistro por cada medicamento, realizar una llamada de tipo GET por cada uno de los nregistros consultando el servicio de medicamentos, https://cima.aemps.es/cima/rest/medicamento. Se deberá obtener las siguientes características por nregistro: [URL 🔗](https://cima.aemps.es/cima/rest/medicamento)

- nregistro: Identificador único del medicamento.

- nombre: Nombre comercial oficial del medicamento.

- pactivos: Principios activos contenidos.

- labtitular: Laboratorio titular de la autorización.

- labcomercializador: Laboratorio comercializador.

- cn: Código Nacional obtenido de las presentaciones (se toma el primero disponible).

- dosis: Concentración o dosis del principio activo.

- forma_farmaceutica_simplificada: Forma farmacéutica simplificada (ej. COMPRIMIDO).

- estado_aut: Fecha de autorización (estado.aut), expresada en formato

- estado_rev: Fecha de revisión (estado.rev), asignando un valor nulo (NaN) si no está disponible.

- vias_administracion: Vías de administración del medicamento

- comercializado: Indicador binario (1 si el campo comerc es verdadero, 0 en caso contrario).

- requiere_receta: Indicador binario (1 si el campo receta es verdadero, 0 en caso contrario).

- generico: Indicador binario (1 si el campo generico es verdadero, 0 en caso contrario).

- afecta_conduccion: Indicador binario (1 si el campo conduc es verdadero, 0 en caso contrario).

- triangulo_negro: Indicador binario (1 si el campo triangulo es verdadero, 0 en caso contrario).

- medicamento_huerfano: Indicador binario (1 si el campo huerfano es verdadero, 0 en caso contrario).

- biosimilar: Indicador binario (1 si el campo biosimilar es verdadero, 0 en caso contrario).

- url_html_ficha_tecnica: Enlace web a la ficha técnica oficial en formato HTML (identificada dentro de los documentos con tipo: 1 y extensión .html).

- url_foto_materiales: Enlace a la imagen o icono de materiales del medicamento (identificada en fotos con el tipo que contiene material y formato .jpg).

- num_registros_atc: Conteo total (longitud) de los elementos en la lista de códigos ATC (atcs).

- num_principios_activos: la lista de principios activos (principiosActivos). Conteo total (longitud) de los elementos en

- num_excipientes: Conteo total (longitud) de los elementos en la lista de excipientes (excipientes).


Para entender cómo se debe configurar las llamadas a la APIREST se provee la documentación donde se encuentran el formato y la configuración de los servicios CIMA_REST_API.pdf. [URL 🔗](https://www.aemps.gob.es/apps/cima/docs/CIMA_REST_API.pdf)

## 1.3. Para

Guardar el fichero resultante en formato xlsx de los medicamentos en base a la enfermedad consiguiendo crear un automatismo para la extracción de datos de medicamentos desde la API de la AEMPS. Por cada nregistro/medicamento deberemos obtener una estructura similar:

| nregistro | 42991 |
| --- | --- |
| nombre | A.A.S. 100 mg COMPRIMIDOS |
| pactivos | ACETILSALICILICO ACIDO |
| labtitular labcomercializador | Laboratorio Stada S.L. |
|   | Laboratorio Stada S.L. |
| en dosis | 686580 |
| forma_farmaceutica_simplificada | 100 mg |
| estado_rev estado_aut | COMPRIMIDO |
| comercializado | n |
| requiere_receta | 1 |
|   | 1 |
| generico afecta_conduccion | ° |
| medicamento_huerfano triangulo_negro | ° |
| biosimilar | ° |
| url_html_ficha_tecnica | ° |
| url_foto_materiales | https://cima.aemps |
|   | https://cima.aemps .es/cima/fotos/thunbnails/ma. . . |
| num_registros_atc |   |
| num_excipientes num_principios_activos |   |
| vias_administracion | 2 |
|   | via oraL |

## 2. Historia de Usuario (HU-2)

## 2.1. Como

Manager del proyecto.

## 2.2. Quiero

## Que las consultoras:

- Realicen un webscraping de forma automática utilizando las urls de las fichas técnicas obtenidas en el HU-1 de cada uno de los medicamentos para calcular las siguientes métricas:

- o Volumen Informativo de Seguridad: Contar cuántas palabras hay exactamente dentro de la sección 4.4. Esto nos da una idea de qué tan denso es el perfil de seguridad del fármaco y cuántas precauciones exige antes de recetarlo.

- o Complejidad del Desglose Clínico: Contar cuántas etiquetas de tablas (<table>) aparecen en todo el documento HTML. Como en las fichas de la AEMPS las tablas se usan para mostrar reacciones adversas o datos químicos, cuantas más tenga, mayor será la complejidad clínica del medicamento.

- o Indicador de Riesgo Severo: Buscar y contar cuántas veces aparece la palabra "grave" (o "graves") en todo el texto. Al ser un término regulatorio estándar


- para alertas máximas, nos sirve como un medidor rápido del nivel de riesgo clínico.

- 2.3. Para

Añadir estos tres indicadores a los datos calculados en HU-1 obteniendo nuevamente un fichero xlsx, con ello conseguimos que el sistema extraiga de forma automática indicadores cuantitativos y estructurales directamente de las Fichas Técnicas, enriqueciendo nuestros datos.

4


## 3. Historia de Usuario (HU-3)

## 3.1. Como

Manager del proyecto.

## 3.2. Quiero

## Que las consultoras:

- Enriquezcan el catálogo de medicamentos añadiendo variables económicas fundamentales utilizando como clave de cruce el Código Nacional ( cn, para ello:

- o Acceder a la plataforma oficial de consulta del Ministerio de Sanidad a través de la siguiente dirección y descargar el fichero. https://www.sanidad.gob.es/profesionales/nomenclator.do?metodo=buscarP roductos [URL 🔗](https://www.sanidad.gob.es/profesionales/nomenclator.do?metodo=buscarProductos)

- Seleccionar únicamente las columnas : Código Nacional, Estado, Precio de venta al público con IVA, Precio de referencia, Tratamiento de larga duración, Especial control médico.

- Incorporar estas columnas en los datos resultantes en la HU-2 en base al cn ( Código Nacional) de cada medicamento.

## 3.3. Para

Añadir los nuevos indicadores a los datos generados en el HU-2 generando un nuevo fichero xlsx, con esto conseguimos que los datos económicos oficiales y actualizados del Sistema Nacional de Salud.
