import socket
from threading import Thread
from typing import Dict, List, Tuple
from queue import Queue
from encryption import EncryptionState
import select
import compress


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


class ServerComm:
    def __init__(self) -> None:
        self.server_socket = socket.socket()
        self.open_sockets: Dict[
            Tuple[str, int], Tuple[socket.socket, EncryptionState]
        ] = {}
        self.logic_queue: Queue[Tuple[str, Tuple[str, int]]] = Queue()
        self.running = False

    def _get_addr_of_socket(self, soc: socket.socket) -> Tuple[str, int]:
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

    def _disconnect_client(self, addr: Tuple[str, int]):
        soc = self.open_sockets[addr]
        del self.open_sockets[addr]
        soc[0].close()

    def _read_sockets(self, rlist: List[socket.socket]):
        for soc in rlist:
            if soc is self.server_socket:
                new_client, addr = self.server_socket.accept()
                self._new_client(new_client, addr)
            else:
                addr = self._get_addr_of_socket(soc)
                try:
                    if self.open_sockets[addr][1].finished_encryption():
                        self._on_message_receive(soc, addr)
                    else:
                        self._on_receive_encryption(soc, addr)
                except Exception as e:
                    print(f"Disconnecting {addr}", e)

                    self._disconnect_client(addr)

    def send_and_close(self, adr: Tuple[str, int], data: str):
        (soc, encyption) = self.open_sockets[adr]
        data_to_send = encyption.encrypt(compress_str(data))
        send(soc, data_to_send, regular_length_size)
        self._disconnect_client(adr)

    def _on_message_receive(self, soc: socket.socket, addr: Tuple[str, int]):
        data_bytes = recv(soc, regular_length_size)
        data_decrypted = self.open_sockets[addr][1].decrypt(data_bytes)
        data_decompressed = decompress_bytes(data_decrypted)
        self.logic_queue.put((data_decompressed, addr))

    def _on_receive_encryption(self, soc: socket.socket, addr: Tuple[str, int]):
        encryption_response_bytes = recv(soc, encyption_length_size)
        client_mixed_key = int(encryption_response_bytes.decode())
        self.open_sockets[addr][1].set_encryption_key(client_mixed_key)

    def _new_client(self, soc: socket.socket, addr: Tuple[str, int]):
        encryption = EncryptionState()
        self.open_sockets[addr] = (soc, encryption)

        msg = encryption.get_initial_public_message()
        length = str(len(msg)).zfill(encyption_length_size)
        soc.send(f"{length}{msg}".encode())

    def start_listeneing(self, port: int):
        self.running = True
        thread = Thread(target=self._listen, args=(port,))
        thread.start()


if __name__ == "__main__":
    comm = ServerComm()
    comm.start_listeneing(3000)
    while True:
        (msg, addr) = comm.logic_queue.get()
        comm.send_and_close(addr, "Bye bye")
        print(msg)
