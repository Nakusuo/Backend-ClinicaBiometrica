from pydantic import BaseModel, EmailStr
from typing import List

class FacialLoginRequest(BaseModel):
    correo: EmailStr
    embedding_facial: List[float]