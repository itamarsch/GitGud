import base64
import random
from typing import Optional

from cryptography.fernet import Fernet


global_p = 189871
global_g = 190619


def diffie_helman(num: int, g: int, p: int) -> int:
    return (g**num) % p


class EncryptionState:
    """
    https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
    """

    secret_key: int
    encryption_key: Optional[int]
    fernet: Fernet

    def encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self.fernet.decrypt(data)

    def __init__(self):
        self.secret_key = random.randint(0, 1000)
        self.encryption_key = None

    def set_encryption_key(self, client_mixed_key: int):
        """
        Set S value on server based on client mixed key
        """
        self.encryption_key = diffie_helman(self.secret_key, client_mixed_key, global_p)
        key = base64.urlsafe_b64encode(
            self.encryption_key.to_bytes(32, byteorder="big")
        )
        self.fernet = Fernet(key)

    def get_initial_public_message(self):
        """
        Get initial message to send to client
        """
        return f"{self.get_mixed_key()};{global_p};{global_g}"

    def finished_encryption(self) -> bool:
        """
        :return: Tells if than encryption has been completed
        """
        return self.encryption_key is not None

    def get_mixed_key(self):
        """
        Get public A from private a
        """
        return diffie_helman(self.secret_key, global_g, global_p)
