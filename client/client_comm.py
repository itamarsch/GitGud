import socket
from typing import Tuple
import compress
import json
from encryption import EncryptionState


encryption_length_size = 3
regular_length_size = 4
file_token_length_size = 3
file_length_size = 9


def decompress_bytes_to_str(data: bytes) -> str:
    return compress.decompress_bytes_to_str(compress.Algorithm.gzip, data)


def decompress_bytes_to_bytes(data: bytes) -> bytes:
    return compress.decompress_bytes_to_bytes(compress.Algorithm.gzip, data)


def compress_str(data: str) -> bytes:
    return compress.compress_str_to_bytes(compress.Algorithm.gzip, data)


def recv(soc: socket.socket, length_size: int) -> bytes:
    length_of_data = int(soc.recv(length_size).decode())
    return soc.recv(length_of_data)


def recv_file(soc: socket.socket, length_size: int) -> bytes:
    length_of_data = int(soc.recv(length_size).decode())
    data = bytes()
    while length_of_data > 0:
        new_data = soc.recv(1024)
        length_of_data -= len(new_data)
        data += new_data
    return data


def send(soc: socket.socket, data: bytes, length_size: int):
    length_bytes = str(len(data)).zfill(length_size).encode()
    soc.send(length_bytes + data)


class ClientComm:
    def __init__(self, addr: Tuple[str, int]) -> None:
        self.ip = addr

    def _exchange_keys(self, soc: socket.socket) -> EncryptionState:
        encryption = EncryptionState()
        initial_encryption_data = recv(soc, encryption_length_size).decode()
        encryption.parse_initial_message(initial_encryption_data)

        mixed_client_key = str(encryption.get_mixed_key()).encode()
        send(soc, mixed_client_key, encryption_length_size)
        return encryption

    def run_request(self, data: str) -> str:
        soc = socket.socket()
        soc.connect(self.ip)

        encryption = self._exchange_keys(soc)
        compressed_data = compress_str(data)
        encrypted_data = encryption.encrypt(compressed_data)
        send(soc, encrypted_data, regular_length_size)

        response = recv(soc, regular_length_size)

        soc.close()
        return decompress_bytes_to_str(encryption.decrypt(response))

    def file_request(self, token: str, port: int) -> bytes:
        soc = socket.socket()
        soc.connect((self.ip[0], port))

        encryption = self._exchange_keys(soc)
        send(soc, encryption.encrypt(token.encode()), file_token_length_size)
        file = recv_file(soc, file_length_size)

        soc.close()
        return decompress_bytes_to_bytes(encryption.decrypt(file))


if __name__ == "__main__":
    client = ClientComm(("127.0.0.1", 30000))
    request = {
        "type": "register",
        "username": "HELL",
        "password": "hi",
        "sshKey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGq2zpYtdWwVTZ9IzNxMlhpUsSG6sJW/AiTX4L7u+Lrd talmid@R211W25",
    }
    file_res = client.run_request(json.dumps(request))
    print(file_res)
