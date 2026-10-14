import numpy as np
import json

# Distancia euclidiana máxima entre descriptores de face-api.js para considerarlos la misma persona.
# face-api.js sugiere 0.6; usamos 0.5 para ser más estrictos.
UMBRAL_CONFIGURADO = 0.5

# face-api.js (FaceRecognitionNet) produce descriptores de 128 valores
DIMENSION_EMBEDDING = 128


def verificar_similitud_facial(embedding_frontend: list, embedding_db_str: str) -> bool:
    if not embedding_db_str:
        return False
    try:
        embedding_db = json.loads(embedding_db_str)

        vector_front = np.array(embedding_frontend, dtype=float)
        vector_db = np.array(embedding_db, dtype=float)

        # Sin esta validación numpy "estira" un vector de 1 valor a 128 y la comparación se puede burlar
        if vector_front.shape != (DIMENSION_EMBEDDING,) or vector_db.shape != (DIMENSION_EMBEDDING,):
            return False
        if not np.all(np.isfinite(vector_front)):
            return False

        distancia = np.linalg.norm(vector_front - vector_db)

        return bool(distancia <= UMBRAL_CONFIGURADO)
    except (json.JSONDecodeError, ValueError, TypeError):
        return False
