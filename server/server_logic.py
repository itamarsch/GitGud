import json
from typing import Callable, Dict, List, Tuple, Any
from database import DB
from git_manager import GitManager
from queue import Queue
from server_protocol import pack_error, pack_login, pack_register, unpack
from server_comm import ServerComm
from gitgud_types import Action, Json, Address
from secrets import token_urlsafe


class ServerLogic:
    def __init__(self, port: int):
        self.port = port
        self.queue: Queue[Tuple[str, Address]] = Queue()
        # Connection Token -> Username
        self.connected_client: Dict[str, str] = {}
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
            response = pack_error(str(e))
        except Exception as e:
            response = pack_error(f"Internal Server error {e}")

        self.server_comm.send_and_close(addr, json.dumps(response))

    def apply_action(self, json: Json) -> Json:
        # Saftey: unpack requires type
        request_type = json["type"]
        if request_type not in self.actions:
            return pack_error("Invalid type")

        (action, required_keys) = self.actions[request_type]
        if not all(required_key in json for required_key in required_keys):
            return pack_error("Invalid keys in request")
        return action(json)

    def get_actions(self) -> Dict[str, Tuple[Action, List[str]]]:
        return {
            "register": (self.register, ["username", "password", "sshKey"]),
            "login": (self.login, ["username", "password"]),
        }

    def generate_new_connection_token(self, username: str) -> str:
        token = token_urlsafe(32)
        self.connected_client[token] = username
        return token

    def register(self, request: Json) -> Json:
        username = request["username"]
        password_hash = request["password"]
        ssh_key = request["sshKey"]
        if self.db.user_exists(username):
            return pack_error("User exists")

        self.db.add_user(username, password_hash)
        self.git_manager.add_ssh_key(username, ssh_key)

        token = self.generate_new_connection_token(username)

        return pack_register(token)

    def login(self, request: Json) -> Json:
        username = request["username"]
        password_hash = request["password"]

        if not self.db.validate_user(username, password_hash):
            return pack_error("Incorrect password")

        token = self.generate_new_connection_token(username)

        return pack_login(token)
