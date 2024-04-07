import hashlib
import base64


def hash(password: str) -> str:
    """
    Compute the SHA-256 hash of the input password and return the base64 encoded hash value as a string.
    
    Password:
        password (str): The input password to be hashed.
        
    Returns:
        str: The base64 encoded hash value of the input password.
    """
    hashed_value = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed_value).decode()
