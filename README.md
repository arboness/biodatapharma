# Readme de seguimiento del proyecto de Ingeniería del dato

## Estructura del proyecto

El proyecto se ha creado con el gestor de paquetes ``uv``. Existen **tres** directorios prinicpales:
    - ``src/biodatapharma/``: Contiene los scripts de python, divididos por **Historia de Usuario**.
    - ``data/``: Contiene todos los ficheros ``.xlsx`` y ``.csv`` del proyecto.
    - ``docs/``: Contiene las instrucciones del proyecto tanto en formato ``.pdf`` como en formato ``.md`` y los documentos de los sprints.

## Manual de usuario

- Para instalarse las dependencias del proyecto, basta con ejecutar ``uv sync`` en el directorio del proyecto.
- El entorno virtual debe de estar **activo**.
- Por defecto, la enfermedad que se analiza es la **esquizofrenia**. Si el usuario quisiese cambiar esta enfermedad, basta con cambiar la constante ``DISEASE_NAME`` del archivo ``src/biodatapharma/constants.py``.
- Para ejecutar cada **historia de usuario**, el usuario debe situarse en el directorio raíz  y en la terminal ejecuta lo siguiente: ``uv run src/biodatapharma/huX.py``, sustituyendo la ``X`` por el número de historia de usuario deseado.

