import json
from typing import Dict, List, Optional, Tuple, cast

from gitdb.util import os
from database import DB
from git_manager import GitManager
from queue import Queue
from repo_clone import RepoClone
from server_protocol import (
    pack_branches,
    pack_create_repo,
    pack_error,
    pack_login,
    pack_register,
    pack_view_file,
    unpack,
)
from git import GitCommandError
from server_comm import FileComm, ServerComm
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
        if (
            "connectionToken" in required_keys
            and json["connectionToken"] not in self.connected_client
        ):
            return pack_error("Invalid connection token")

        return action(json)

    def get_actions(self) -> Dict[str, Tuple[Action, List[str]]]:
        return {
            "register": (self.register, ["username", "password", "sshKey"]),
            "login": (self.login, ["username", "password"]),
            "createRepo": (
                self.create_repo,
                ["repoName", "visibility", "connectionToken"],
            ),
            "branches": (self.branches, ["repo", "connectionToken"]),
            "viewFile": (
                self.view_file,
                ["repo", "connectionToken", "filePath", "branch"],
            ),
        }

    def generate_new_connection_token(self, username: str) -> str:
        token = token_urlsafe(32)
        self.connected_client[token] = username
        return token

    def validate_repo_request(self, repo: str, connectionToken: str) -> Optional[Json]:
        user_and_repo = repo.split("/")
        if len(user_and_repo) != 2:
            return pack_error("Invalid user and repo request")

        sql_repo_data = self.db.repo_by_name(repo)
        if sql_repo_data is None:
            return pack_error("Invalid username or repo")
        username = self.connected_client[connectionToken]

        # You are not owner of repo and repo is not public
        if username != user_and_repo[0] and not sql_repo_data[2]:
            return pack_error("Invalid permissions")

        return None

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

    def create_repo(self, request: Json) -> Json:
        repo_name = request["repoName"]
        visibility = request["visibility"]
        connection_token = request["connectionToken"]
        username = self.connected_client[connection_token]
        repo_id = self.db.repo_by_name(f"{username}/{repo_name}")
        if repo_id is not None:
            return pack_error("Repository already exists")

        self.db.add_repo(username, repo_name, visibility)
        self.git_manager.create_repo(repo_name, username, visibility)

        return pack_create_repo()

    def branches(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            branches = [branch.name for branch in r.remote().refs]
        return pack_branches(branches)

    def view_file(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result
        file = request["filePath"]
        token = token_urlsafe(32)
        branch = request["branch"]

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            try:
                r.git.checkout(branch)
            except GitCommandError:
                return pack_error("Invalid branch name")

            try:
                path = os.path.relpath(f"./cache/{full_repo_name}/{file}")

                if not path.startswith(f"cache/{full_repo_name}"):
                    return pack_error("Path out of repository")

                with open(path, "rb") as f:
                    file_com = FileComm(f.read(), token)
                    return pack_view_file(file_com.get_port(), token)
            except FileNotFoundError:
                return pack_error("File doesn't exist")
