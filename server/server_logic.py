import json
from typing import Callable, Dict, List, Tuple, Any
from database import DB
from git_manager import GitManager
from queue import Queue
from server_protocol import unpack
from server_comm import ServerComm
from gitgud_types import Json, Address


class ServerLogic:
    def __init__(self, port: int):
        self.port = port
        self.queue: Queue[Tuple[str, Address]] = Queue()
        # Connection Token -> UserID
        self.connected_client: Dict[str, int] = {}
        self.server_comm = ServerComm(self.queue)
        self.server_comm.start_listeneing(port)
        self.db = DB()
        self.git_manager = GitManager("../gitolite-admin")
        self.actions = self.get_actions()

    def tick(self):
        (request, addr) = self.queue.get()
        response: Json
        try:
            json_request = unpack(request)
            response = self.apply_action(json_request)
        except ValueError as e:
            response = {"error": str(e)}

        self.server_comm.send_and_close(addr, json.dumps(response))

    def apply_action(self, json: Json) -> Json:
        # Saftey: unpack requires type
        request_type = json["type"]
        if request_type not in self.actions:
            return {"error": "Invalid type"}

        return self.actions[request_type](json)

    def get_actions(self) -> Dict[str, Callable[[Json], Json]]:
        return {"register": self.register}

    def register(self, request: Json) -> Json:
        required_keys = ["username", "password", "sshKey"]
        if not all(required_key in request for required_key in required_keys):
            return {"error": "Invalid request"}
        username = request["username"]
        password_hash = request["password"]
        ssh_key = request["sshKey"]
        return {"connectionToken": ""}
