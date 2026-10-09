from pydantic import BaseModel

from app.schemas.tipos import Embedding


class BiometriaRequest(BaseModel):
    embedding: Embedding
