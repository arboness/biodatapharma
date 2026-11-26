
import logging
import sys

from biodatapharma import hu1_3, hu4, hu5, hu6_create_table, hu6_kpis, hu6_load
from biodatapharma.constants import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Iniciando ejecución de: schezofrenia_esquizofrenia.py")

    if hu1_3.extract_nomenclator() != 0:
        logger.error("Fallo en HU1-HU3 (extracción y nomenclátor)")
        return 1
    logger.info("HU1-HU3 completadas")

    if hu4.clean_and_transform() != 0:
       logger.error("Fallo en HU4 (limpieza y transformación)")
       return 2
    logger.info("HU4 completada")

    if hu5.cluster_kmeans() != 0:
      logger.error("Fallo en HU5 (clustering)")
      return 3
    logger.info("HU5 completada")

    if hu6_create_table.create_table() != 0:
        logger.error("Fallo en HU6 (creación de tablas)")
        return 4
    logger.info("HU6: tablas creadas")

    if hu6_load.load_data() != 0:
        logger.error("Fallo en HU6 (carga de datos)")
        return 5
    logger.info("HU6: datos cargados")

    if hu6_kpis.kpis() != 0:
        logger.error("Fallo en HU6 (KPIs)")
        return 6
    logger.info("HU6: KPIs calculados")

    logger.info("Finalizada correctamente la ejecución de:  schezofrenia_esquizofrenia.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
    