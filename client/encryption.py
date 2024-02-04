import base64
import random
from typing import Optional, cast
import socket
from cryptography.fernet import Fernet
import compress


def diffie_helman(num: int, g: int, p: int) -> int:
    return (g**num) % p


class EncryptionState:
    """
    https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
    """

    secret_key: int
    encryption_key: Optional[int]

    def encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self.fernet.decrypt(data)

    def __init__(self):
        self.p: Optional[int] = None
        self.g: Optional[int] = None
        self.secret_key = random.randint(0, 1000)
        self.encryption_key = None
        self.fernet: Fernet

    def set_encryption_key(self, server_mixed_key_bytes: int):
        """
        Set S value on server based on client mixed key
        """
        self.encryption_key = diffie_helman(
            self.secret_key, server_mixed_key_bytes, cast(int, self.p)
        )
        key = base64.urlsafe_b64encode(
            self.encryption_key.to_bytes(32, byteorder="big")
        )
        self.fernet = Fernet(key)

    def parse_initial_message(self, data: str):
        [mixed_key, p, g] = data.split(";")
        self.p = int(p)
        self.g = int(g)
        self.set_encryption_key(int(mixed_key))

    def finished_encryption(self) -> bool:
        return self.encryption_key is not None

    def get_mixed_key(self):
        """
        Get public A from private a
        """
        return diffie_helman(self.secret_key, cast(int, self.g), cast(int, self.p))
