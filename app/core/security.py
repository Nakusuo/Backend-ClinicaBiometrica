from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "telemedicina2026"
ALGORITHM = "HS256"

def create_access_token(data):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )