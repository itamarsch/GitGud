import base64
import random
from typing import Optional, cast
from cryptography.fernet import Fernet


def diffie_helman(num: int, g: int, p: int) -> int:
    """
    Calculate the Diffie-Hellman key exchange using the given parameters.

    Parameters:
        num (int): The private key exponent.
        g (int): The generator.
        p (int): The prime modulus.

    Returns:
        int: The calculated Diffie-Hellman key.
    """
    return (g**num) % p


class EncryptionState:
    """
    https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
    """

    def __init__(self):
        """
        Initializes a new instance of the class.

        This constructor sets the `p` attribute to `None`, the `g` attribute to `None`, the `secret_key` attribute to a random integer between 0 and 1000, the `encryption_key` attribute to `None`, and the `fernet` attribute to `None`.

        Parameters:
            None

        Returns:
            None
        """
        self.p: Optional[int] = None
        self.g: Optional[int] = None
        self.secret_key = random.randint(0, 1000)
        self.encryption_key: Optional[int] = None
        self.fernet: Fernet

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts the given data using the Fernet encryption algorithm.

        Parameters:
            data (bytes): The data to be encrypted.

        Returns:
            bytes: The encrypted data.
        """
        return self.fernet.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts the given data using the Fernet encryption algorithm.

        Args:
            data (bytes): The data to be decrypted.

        Returns:
            bytes: The decrypted data.
        """
        return self.fernet.decrypt(data)

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
        """
        Parses the initial message received from the server and sets the necessary attributes for encryption.

        Parameters:
            data (str): The initial message received from the server.

        Returns:
            None
        """
        [mixed_key, p, g] = data.split(";")
        self.p = int(p)
        self.g = int(g)
        self.set_encryption_key(int(mixed_key))

    def get_mixed_key(self):
        """
        Get public A from private a
        """
        return diffie_helman(self.secret_key, cast(int, self.g), cast(int, self.p))
