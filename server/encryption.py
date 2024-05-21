import base64
import random
from typing import Optional, cast

from cryptography.fernet import Fernet


global_p = 189871
global_g = 190619


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

        This constructor sets the `secret_key` attribute to a random integer between 0 and 1000,
        the `encryption_key` attribute to `None`, and the `fernet` attribute to `None`.

        Parameters:
            None

        Returns:
            None
        """
        self.secret_key: int = random.randint(0, 1000)
        self.encryption_key: Optional[int] = None
        self.fernet = None

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts the given data using the Fernet encryption algorithm.

        Parameters:
            data (bytes): The data to be encrypted.

        Returns:
            bytes: The encrypted data.
        """
        return cast(Fernet, self.fernet).encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts the given data using the Fernet encryption algorithm.

        Args:
            data (bytes): The data to be decrypted.

        Returns:
            bytes: The decrypted data.
        """
        return cast(Fernet, self.fernet).decrypt(data)

    def set_encryption_key(self, client_mixed_key_response_bytes: bytes):
        """
        :client_mixed_key: Response of encryption key in bytes
        Set S value on server based on client mixed key
        """
        client_mixed_key = int(client_mixed_key_response_bytes.decode())
        self.encryption_key = diffie_helman(self.secret_key, client_mixed_key, global_p)
        key = base64.urlsafe_b64encode(
            self.encryption_key.to_bytes(32, byteorder="big")
        )
        self.fernet = Fernet(key)

    def get_initial_public_message(self) -> bytes:
        """
        Get initial message to send to client
        """
        return f"{self.get_mixed_key()};{global_p};{global_g}".encode()

    def finished_encryption(self) -> bool:
        """
        :return: Tells if than encryption has been completed
        """
        return self.encryption_key is not None

    def get_mixed_key(self) -> int:
        """
        Get public A from private a
        """
        return diffie_helman(self.secret_key, global_g, global_p)
