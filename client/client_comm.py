import socket
import sys
from typing import Tuple
import compress
import json
from encryption import EncryptionState
from gitgud_types import Json


encryption_length_size = 3
regular_length_size = 4
file_token_length_size = 3
file_length_size = 9


def decompress_bytes_to_str(data: bytes) -> str:
    """
    Decompresses a byte string using the gzip algorithm and returns the decompressed string.

    Parameters:
        data (bytes): The byte string to be decompressed.

    Returns:
        str: The decompressed string.

    Raises:
        ValueError: If the input data is not in a valid gzip format.
    """
    return compress.decompress_bytes_to_str(compress.Algorithm.gzip, data)


def decompress_bytes_to_bytes(data: bytes) -> bytes:
    """
    Decompresses a byte string using the gzip algorithm and returns the decompressed bytes.

    Parameters:
        data (bytes): The byte string to be decompressed.

    Returns:
        bytes: The decompressed bytes.

    Raises:
        ValueError: If the input data is not in a valid gzip format.
    """
    return compress.decompress_bytes_to_bytes(compress.Algorithm.gzip, data)


def compress_str(data: str) -> bytes:
    """
    Compresses a string using the gzip algorithm and returns the compressed bytes.

    Parameters:
        data (str): The string to be compressed.

    Returns:
        bytes: The compressed bytes.

    Raises:
        ValueError: If the input data is not a valid string.
    """
    return compress.compress_str_to_bytes(compress.Algorithm.gzip, data)


def recv(soc: socket.socket, length_size: int) -> bytes:
    """
    Receives data from a socket based on the length provided and returns the received data.

    Parameters:
        soc (socket.socket): The socket from which to receive data.
        length_size (int): The size of the length prefix.

    Returns:
        bytes: The received data.
    """
    length_of_data = int(soc.recv(length_size).decode())
    return soc.recv(length_of_data)


def recv_file(soc: socket.socket, length_size: int) -> bytes:
    """
    Receives a file from a socket connection.

    Args:
        soc (socket.socket): The socket object representing the connection.
        length_size (int): The size of the length prefix of the file.

    Returns:
        bytes: The received file data.

    Raises:
        ValueError: If the received length prefix is not a valid integer.
        ConnectionError: If the connection is closed before receiving the entire file.
    """
    length_of_data = int(soc.recv(length_size).decode())
    data = bytes()
    while length_of_data > 0:
        new_data = soc.recv(1024)
        length_of_data -= len(new_data)
        data += new_data
    return data


def send(soc: socket.socket, data: bytes, length_size: int):
    """
    Sends data over a socket connection by first sending the length of the data as a prefix.

    Parameters:
        soc (socket.socket): The socket object representing the connection.
        data (bytes): The data to be sent.
        length_size (int): The size of the length prefix.

    Returns:
        None
    """
    length_bytes = str(len(data)).zfill(length_size).encode()
    soc.send(length_bytes + data)


class ClientComm:
    def __init__(self, addr: Tuple[str, int]) -> None:
        """
        Initializes a new instance of the class.

        Args:
            addr (Tuple[str, int]): The IP address and port number of the server.

        Returns:
            None
        """
        self.ip = addr

    def _exchange_keys(self, soc: socket.socket) -> EncryptionState:
        """
        A function to exchange keys with a socket using encryption and return the encryption state.

        Parameters:
            soc (socket.socket): The socket to exchange keys with.

        Returns:
            EncryptionState: The encryption state after key exchange.
        """
        encryption = EncryptionState()
        initial_encryption_data = recv(soc, encryption_length_size).decode()
        encryption.parse_initial_message(initial_encryption_data)

        mixed_client_key = str(encryption.get_mixed_key()).encode()
        send(soc, mixed_client_key, encryption_length_size)
        return encryption

    def run_request(self, data: Json) -> Json:
        """
        Runs a request with the provided data using socket communication.
        
        Parameters:
            data (Json): The data to be sent in JSON format.
        
        Returns:
            Json: The response data received after processing the request.
        """
        soc = socket.socket()
        soc.connect(self.ip)

        encryption = self._exchange_keys(soc)
        compressed_data = compress_str(json.dumps(data))
        encrypted_data = encryption.encrypt(compressed_data)
        send(soc, encrypted_data, regular_length_size)
        response = recv(soc, regular_length_size)
        soc.close()

        result = decompress_bytes_to_str(encryption.decrypt(response))
        return json.loads(result)

    def file_request(self, token: str, port: int) -> bytes:
        """
        Runs a file request using the provided token and port number.

        Parameters:
            token (str): The token to be used for the file request.
            port (int): The port number to connect to.

        Returns:
            bytes: The decrypted file content.
        """
        soc = socket.socket()
        soc.connect((self.ip[0], port))

        encryption = self._exchange_keys(soc)
        send(soc, encryption.encrypt(token.encode()), file_token_length_size)
        file = recv_file(soc, file_length_size)

        return decompress_bytes_to_bytes(encryption.decrypt(file))


if __name__ == "__main__":
    client = ClientComm(("127.0.0.1", 30000))
    request = {
        "type": "login",
        "username": "HELLO",
        "password": "FADFDSDf",
    }
    login_res = client.run_request(request)
    # print(login_res)
    if "error" in login_res:
        sys.exit(1)
    connection_token = login_res["connectionToken"]

    create_pr = {
        "type": "searchRepo",
        "searchQuery": "Hell",
    }

    result = client.run_request(create_pr)
    print(result)
    if "error" in result:
        print(result)
        sys.exit(1)
