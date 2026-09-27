import time
from datetime import datetime, timezone
import json
from typing import Any 
import pandas as pd
import requests
 
CIMA_MEDICAMENTO_URL = "https://cima.aemps.es/cima/rest/medicamento"

def _epoch_ms_to_date(epoch_ms: int | None) -> str | None:
    """Pasa una fecha de formato ms a datetime.

    Args:
        epoch_ms: entero con la fecha en ms o nulo.

    Returns:
        Fecha en datetime o None.
    """
    if epoch_ms is None:
        return None
    try:
        return pd.to_datetime(epoch_ms, unit="ms", utc=True).date().isoformat()
    except (ValueError, OverflowError):
        return None

def _url_material_images(images: list[dict[str, Any]] | None) -> str | None:
    """Devuelve el enlace a la imagen de materiales del medicamento dadas unas url (tipo material).

    Args:
        images: lista de urls.

    Returns:
        Url de la imagen del material del medicamento.
    """
    for image in images or []:
        url = image.get("url", "")
        if image.get("tipo") == "materiales" or url.lower().endswith(".jpg"):
            return url
    return None

def _url_tecnical_specs(docs: list[dict[str, Any]] | None) -> str | None:
    """Devuelve el enlace a las especificaciones técnicas del medicamento dadas unas url (tipo 1).

    Args:
        images: lista de urls.

    Returns:
        Url de las especificaciones técnicas del medicamento.
    """
    for doc in docs or []:
        if doc.get("tipo") == 1:
            return doc.get("urlHtml") or doc.get("url")
    return None


def _vias_administracion(vias: str | None) -> str | None:
    """Dada la información de ViasAdministracion, analiza qué tipos de administración se pueden realizar. 

    Args:
        images: lista de urls.

    Returns:
        Un string con todas las vías de administración del medicamento.
    """
    if not vias:
        return None
    return ", ".join(v.get("nombre", "") for v in vias)

def extract_drug_details(nrecord: str) -> dict:
    """Obtiene todos los detalles de un medicamento que HU1 solicita. Hace uso de las funciones definidas previamente. Realiza una petición get 
       a la API pasando como parámetro el número de registro.
    Args:
        nrecord: número de registro de un medicamento.

    Returns:
        Un diccionario con todos los campos requeridos.
    """
    resp = requests.get(
        CIMA_MEDICAMENTO_URL,
        params={"nregistro": nrecord},
        timeout=10)
    resp.raise_for_status()
    data = resp.json()
 
    state = data.get("estado", {}) or {}
 
    return {
        "nregistro": data.get("nregistro", None),
        "nombre": data.get("nombre", None),
        "pactivos": data.get("pactivos", None),
        "labtitular": data.get("labtitular", None),
        "labcomercializador": data.get("labcomercializador"),
        "cn": data.get("presentaciones", None)[0].get("cn", None),
        "dosis": data.get("dosis", None),
        "forma_farmaceutica_simplificada": (data.get("formaFarmaceuticaSimplificada") or {}).get("nombre"),
        "estado_aut": _epoch_ms_to_date(state.get("aut")),
        "estado_rev": _epoch_ms_to_date(state.get("rev")),
        "vias_administracion": _vias_administracion(data.get("viasAdministracion")),
        "comercializado": int(bool(data.get("comerc"))),
        "requiere_receta": int(bool(data.get("receta"))),
        "generico": int(bool(data.get("generico"))),
        "afecta_conduccion": int(bool(data.get("conduc"))),
        "triangulo_negro": int(bool(data.get("triangulo"))),
        "medicamento_huerfano": int(bool(data.get("huerfano"))),
        "biosimilar": int(bool(data.get("biosimilar"))),
        "url_ficha_tecnica": _url_tecnical_specs(data.get("docs")),
        "url_foto_materiales": _url_material_images(data.get("fotos")),
        "num_registros_atc": len(data.get("atcs") or []),
        "num_principios_activos": len(data.get("principiosActivos") or []),
        "num_excipientes": len(data.get("excipientes") or []),
    }