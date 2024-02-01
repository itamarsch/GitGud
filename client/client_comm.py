import socket
from typing import Optional, Tuple, cast
import compress
from encryption import EncryptionState


encyption_length_size = 3
regular_length_size = 4


def decompress_bytes(data: bytes) -> str:
    return compress.decompress_bytes_to_str(compress.Algorithm.gzip, data)


def compress_str(data: str) -> bytes:
    return compress.compress_str_to_bytes(compress.Algorithm.gzip, data)


def recv(soc: socket.socket, length_size: int) -> bytes:
    length_of_data = int(soc.recv(length_size).decode())
    return soc.recv(length_of_data)


def send(soc: socket.socket, data: bytes, length_size: int):
    length_bytes = str(len(data)).zfill(length_size).encode()
    soc.send(length_bytes + data)


class ClientComm:
    def __init__(self, addr: Tuple[str, int]) -> None:
        self.ip = addr
        self.encryption: Optional[EncryptionState] = None

    def _exchange_keys(self, soc: socket.socket):
        self.encryption = EncryptionState()
        initial_encryption_data = recv(soc, encyption_length_size).decode()
        self.encryption.parse_initial_message(initial_encryption_data)

        mixed_client_key = str(self.encryption.get_mixed_key()).encode()
        send(soc, mixed_client_key, encyption_length_size)

    def run_request(self, data: str) -> str:
        soc = socket.socket()
        soc.connect(self.ip)

        self._exchange_keys(soc)
        compressed_data = compress_str(data)
        encryption = cast(EncryptionState, self.encryption)
        encrypted_data = encryption.encrypt(compressed_data)
        send(soc, encrypted_data, regular_length_size)

        return decompress_bytes(encryption.decrypt(recv(soc, regular_length_size)))


if __name__ == "__main__":
    client = ClientComm(("127.0.0.1", 3000))
    print(client.run_request("Hello"))
