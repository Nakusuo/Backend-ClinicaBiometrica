import numpy as np
import json

# Definimos el umbral de similitud sugerido en el plan (0.6)
UMBRAL_CONFIGURADO = 0.6


def verificar_similitud_facial(embedding_frontend: list, embedding_db_str: str) -> bool:
    if not embedding_db_str:
        return False
    try:
        embedding_db = json.loads(embedding_db_str)

        vector_front = np.array(embedding_frontend, dtype=float)
        vector_db = np.array(embedding_db, dtype=float)

        distancia = np.linalg.norm(vector_front - vector_db)

        return bool(distancia <= UMBRAL_CONFIGURADO)
    except (json.JSONDecodeError, ValueError, TypeError):
        return False