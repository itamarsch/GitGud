import socket
from threading import Thread
from typing import Dict, List, Tuple
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
    return compress.decompress_bytes_to_str(compress.Algorithm.gzip, data)


def compress_str(data: str) -> bytes:
    return compress.compress_str_to_bytes(compress.Algorithm.gzip, data)


def compress_bytes(data: bytes) -> bytes:
    return compress.compress_bytes_to_bytes(compress.Algorithm.gzip, data)


def recv(soc: socket.socket, length_size: int) -> bytes:
    length_of_data = int(soc.recv(length_size).decode())
    return soc.recv(length_of_data)


def send(soc: socket.socket, data: bytes, length_size: int):
    length_bytes = str(len(data)).zfill(length_size).encode()
    soc.send(length_bytes + data)


class FileComm:
    def __init__(self, data: bytes, token: str):
        self.data = data
        self.token = token
        self.running = False
        self.start_listeneing()

    def start_listeneing(self):
        thread = Thread(target=self._listen)
        thread.start()

    def get_port(self) -> int:
        while not self.running:
            pass
        return self.soc.getsockname()[1]

    def _listen(self):
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
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.open_sockets: Dict[Address, Tuple[socket.socket, EncryptionState]] = {}
        self.logic_queue = queue
        self.running = False

    def _get_addr_of_socket(self, soc: socket.socket) -> Address:
        for k, v in self.open_sockets.items():
            if v[0] is soc:
                return k
        raise Exception(
            "Invalid socket, shouldn't happen because rlist only contains known sockets"
        )

    def _listen(self, port: int):
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
        if addr in self.open_sockets:
            soc = self.open_sockets[addr]
            del self.open_sockets[addr]
            soc[0].close()

    def _read_sockets(self, rlist: List[socket.socket]):
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
                if self.open_sockets[addr][1].finished_encryption():
                    self._on_message_receive(soc, addr)
                else:
                    self._on_receive_encryption(soc, addr)

    def send_and_close(self, adr: Address, data: str):
        (soc, encyption) = self.open_sockets[adr]
        data_to_send = encyption.encrypt(compress_str(data))
        send(soc, data_to_send, regular_length_size)
        self._disconnect_client(adr)

    def _on_message_receive(self, soc: socket.socket, addr: Address):
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
        try:
            encryption_response_bytes = recv(soc, encryption_length_size)
            self.open_sockets[addr][1].set_encryption_key(encryption_response_bytes)
        except Exception as e:
            print(f"Disconnecting {addr}", e)
            self._disconnect_client(addr)
            return

    def _new_client(self, soc: socket.socket, addr: Address):
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
        self.running = True
        thread = Thread(target=self._listen, args=(port,))
        thread.start()
