import hashlib
import base64


def hash(password: str) -> str:
    hashed_value = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed_value).decode()
