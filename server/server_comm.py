import socket
from threading import Thread
from typing import Dict, List, Optional, Tuple
from queue import Queue
from encryption import EncryptionState
import select
import compress
from gitgud_types import Address


encryption_length_size = 3
regular_length_size = 4
file_token_length_size = 3
file_length_size = 9


def decompress_bytes(data: bytes) -> str:
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


def compress_bytes(data: bytes) -> bytes:
    """
    Compresses a byte string using the gzip algorithm and returns the compressed bytes.

    Parameters:
        data (bytes): The byte string to be compressed.

    Returns:
        bytes: The compressed bytes.
    """
    return compress.compress_bytes_to_bytes(compress.Algorithm.gzip, data)


def recv(soc: socket.socket, length_size: int) -> bytes:
    """
    A function that receives data from a socket based on the length provided and returns the received data.

    Parameters:
    - soc: A socket.socket object representing the socket to receive data from.
    - length_size: An integer indicating the length of the data to receive.

    Returns:
    - bytes: The data received from the socket.
    """
    length_of_data = int(soc.recv(length_size).decode())
    return soc.recv(length_of_data)


def send(soc: socket.socket, data: bytes, length_size: int):
    """
    A function that sends data over a socket after adding the length of the data at the beginning.

    Parameters:
    - soc: A socket.socket object representing the socket to send data over.
    - data: A bytes object containing the data to be sent.
    - length_size: An integer indicating the size of the length prefix to add to the data.

    No return value.
    """
    length_bytes = str(len(data)).zfill(length_size).encode()
    soc.send(length_bytes + data)


class FileComm:
    def __init__(self, data: bytes, token: str):
        """
        Initializes a new instance of the FileComm class.

        Parameters:
            data (bytes): The data to be stored in the FileComm object.
            token (str): The token to be stored in the FileComm object.

        Returns:
            None
        """
        self.data = data
        self.token = token
        self.running = False
        self.start_listeneing()

    def start_listeneing(self):
        """
        Start listening for incoming connections in a separate thread.

        This method creates a new thread and assigns the `_listen` method as the target for that thread. The `_listen` method is responsible for listening for incoming connections and handling them.

        Parameters:
            None

        Returns:
            None
        """
        thread = Thread(target=self._listen)
        thread.start()

    def get_port(self) -> int:
        """
        Returns port of file communication that was selected randomly by os
        """
        while not self.running:
            pass
        return self.soc.getsockname()[1]

    def _listen(self):
        """
        Listen for incoming connections,
        establish encryption,
        receive file request,
        validate file request,
        send file,
        then close the connection.
        """
        self.soc = socket.socket()
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind(("0.0.0.0", 0))
        self.soc.listen(1)
        self.running = True
        encryption = EncryptionState()

        (client, _) = self.soc.accept()

        send(client, encryption.get_initial_public_message(), encryption_length_size)
        encryption_response = recv(client, encryption_length_size)
        encryption.set_encryption_key(encryption_response)

        token_encrypted = recv(client, file_token_length_size)
        token = encryption.decrypt(token_encrypted).decode()

        if token == self.token:
            data_compressed = compress_bytes(self.data)
            data_encrypted = encryption.encrypt(data_compressed)
            send(client, data_encrypted, file_length_size)

        client.close()
        self.soc.close()
        del self.soc


class ServerComm:
    def __init__(self, queue: Queue[Tuple[str, Address]]) -> None:
        """
        Initializes a new instance of the ServerComm class.

        Parameters:
            queue (Queue[Tuple[str, Address]]): The queue for handling incoming requests.

        Returns:
            None
        """
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.open_sockets: Dict[Address, Tuple[socket.socket, EncryptionState]] = {}
        self.logic_queue = queue
        self.running = False

    def _get_addr_of_socket(self, soc: socket.socket) -> Optional[Address]:
        """
        Get the address of socket if it is part of the open_clients

        Parameters:
            soc (socket.socket): Socket to get address of
        """
        for k, v in self.open_sockets.items():
            if v[0] is soc:
                return k
        return None

    def _listen(self, port: int):
        """
        Listens on a specified port for incoming connections and reads data from the sockets.

        Parameters:
            port (int): The port number to listen on.
        """
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(4)
        while self.running:
            current_sockets = [conn[0] for conn in self.open_sockets.values()]
            rlist: List[socket.socket]
            rlist, _, _ = select.select(
                [self.server_socket] + current_sockets, current_sockets, [], 0.1
            )
            self._read_sockets(rlist)

    def _disconnect_client(self, addr: Address):
        """
        Disconnects a client from the server by removing its socket from the `open_sockets` dictionary and closing the socket.

        Parameters:
            addr (Address): The address of the client to disconnect.

        Returns:
            None
        """
        if addr in self.open_sockets:
            soc = self.open_sockets[addr]
            del self.open_sockets[addr]
            soc[0].close()

    def _read_sockets(self, rlist: List[socket.socket]):
        """
        Read sockets and handle new client connections or received messages.

        Parameters:
            rlist (List[socket.socket]): List of socket objects to read from.

        Returns:
            None
        """
        for soc in rlist:
            if soc is self.server_socket:
                try:
                    new_client, addr = self.server_socket.accept()
                    self._new_client(new_client, addr)
                except Exception:
                    print("Error on new client")
                    continue
            else:
                addr = self._get_addr_of_socket(soc)
                if not addr:
                    continue

                if self.open_sockets[addr][1].finished_encryption():
                    self._on_message_receive(soc, addr)
                else:
                    self._on_receive_encryption(soc, addr)

    def send_and_close(self, addr: Address, data: str):
        """
        Send data and close the socket for the given address.

        Parameters:
            addr (Address): The address to send the data to.
            data (str): The data to be sent.

        Returns:
            None
        """
        (soc, encyption) = self.open_sockets[addr]
        data_to_send = encyption.encrypt(compress_str(data))
        send(soc, data_to_send, regular_length_size)
        self._disconnect_client(addr)

    def _on_message_receive(self, soc: socket.socket, addr: Address):
        """
        Handle receiving and processing messages from a socket connection.

        Parameters:
            soc (socket.socket): The socket object for the connection.
            addr (Address): The address of the client.

        Returns:
            None
        """
        try:
            data_bytes = recv(soc, regular_length_size)
            data_decrypted = self.open_sockets[addr][1].decrypt(data_bytes)
            data_decompressed = decompress_bytes(data_decrypted)
        except Exception as e:
            print(f"Disconnecting {addr}", e)
            self._disconnect_client(addr)
            return
        self.logic_queue.put((data_decompressed, addr))

    def _on_receive_encryption(self, soc: socket.socket, addr: Address):
        """
        A function to handle receiving encryption responses from a socket.

        Parameters:
            soc (socket.socket): The socket object for communication.
            addr (Address): The address of the connection.
        """
        try:
            encryption_response_bytes = recv(soc, encryption_length_size)
            self.open_sockets[addr][1].set_encryption_key(encryption_response_bytes)
        except Exception as e:
            print(f"Disconnecting {addr}", e)
            self._disconnect_client(addr)
            return

    def _new_client(self, soc: socket.socket, addr: Address):
        """
        Initializes a new client connection with the given socket and address.

        Parameters:
            soc (socket.socket): The socket object for the client connection.
            addr (Address): The address of the client.

        Returns:
            None
        """
        encryption = EncryptionState()
        self.open_sockets[addr] = (soc, encryption)

        encryption_initial_message = encryption.get_initial_public_message()
        try:
            send(soc, encryption_initial_message, encryption_length_size)
        except Exception as e:
            print(f"Disconnecting {addr}", e)
            self._disconnect_client(addr)
            return

    def start_listeneing(self, port: int):
        """
        Start listening for incoming connections in a separate thread.

        This method creates a new thread and assigns the `_listen` method as the target for that thread. The `_listen` method is responsible for listening for incoming connections and handling them.

        Parameters:
            port (int): The port number to listen on.

        Returns:
            None
        """
        self.running = True
        thread = Thread(target=self._listen, args=(port,))
        thread.start()
