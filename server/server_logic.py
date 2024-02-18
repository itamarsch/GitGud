import json
from os.path import isdir
from typing import Dict, List, Optional, Tuple, cast, TypeVar
import datetime
from git.diff import Diff
from gitdb.base import OStream
from gitdb.util import os
from database import DB
from git_manager import GitManager
from queue import Queue
from repo_clone import RepoClone
from server_protocol import (
    pack_branches,
    pack_commits,
    pack_create_issue,
    pack_create_repo,
    pack_diff,
    pack_error,
    pack_login,
    pack_project_dirs,
    pack_register,
    pack_view_file,
    unpack,
)
from git import GitCommandError, IndexObject
from server_comm import FileComm, ServerComm
from gitgud_types import Action, Json, Address
from secrets import token_urlsafe

commit_page_size = 30


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
            "projectDirectory": (
                self.project_directory,
                ["directory", "repo", "branch", "connectionToken"],
            ),
            "commits": (self.commits, ["repo", "connectionToken", "branch", "page"]),
            "diff": (self.diff, ["repo", "connectionToken", "hash"]),
            "createIssue": (
                self.create_issue,
                ["repo", "connectionToken", "title", "content"],
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
        id = cast(int, self.db.username_to_id(username))

        self.db.add_repo(id, repo_name, visibility)
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

        path = os.path.relpath(f"./cache/{full_repo_name}/{file}")

        if not path.startswith(f"cache/{full_repo_name}"):
            return pack_error("Path out of repository")

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            try:
                r.git.checkout(branch)
            except GitCommandError:
                return pack_error("Invalid branch name")

            try:
                with open(path, "rb") as f:
                    file_com = FileComm(f.read(), token)
                    return pack_view_file(file_com.get_port(), token)
            except FileNotFoundError:
                return pack_error("File doesn't exist")

    def project_directory(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result

        directory_in_project = request["directory"]
        branch = request["branch"]

        path = os.path.relpath(f"./cache/{full_repo_name}/{directory_in_project}")

        if not path.startswith(f"cache/{full_repo_name}"):
            return pack_error("Path out of repository")

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            try:
                r.git.checkout(branch)
            except GitCommandError:
                return pack_error("Invalid branch name")

            if not os.path.isdir(path):
                return pack_error("Directory doesn't exist")

            try:
                (_, dirs, files) = next(os.walk(path))
                if ".git" in dirs:
                    dirs.remove(".git")

                dirs = map(lambda dir: f"{dir}/", dirs)

                return pack_project_dirs([*dirs, *files])

            except FileNotFoundError:
                return pack_error("File doesn't exist")

    def commits(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result

        branch = request["branch"]
        page = int(request["page"])

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            fifty_first_commits = list(
                r.iter_commits(
                    branch, skip=page * commit_page_size, max_count=commit_page_size
                )
            )
            commits_list = []
            for c in fifty_first_commits:
                date = datetime.datetime.fromtimestamp(c.authored_date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                authour = str(c.author)
                hash = c.hexsha
                message = c.message
                commits_list.append(
                    {"date": date, "hash": hash, "message": message, "authour": authour}
                )

            return pack_commits(commits_list)

    def diff(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result

        with RepoClone(full_repo_name) as r:
            hash = request["hash"]
            try:
                commit = r.commit(hash)
            except Exception:
                return pack_error("Invalid commit hash")

            diff = commit.parents[0].diff(commit)

            diff_result: List[str] = []
            for diff_item in diff.iter_change_type("R"):
                diff_item: Diff
                diff_result.append(
                    f"Rename: {diff_item.rename_from} -> {diff_item.rename_to}"
                )
            for diff_item in diff.iter_change_type("A"):
                diff_item: Diff
                blob = (
                    cast(IndexObject, diff_item.b_blob)
                    .data_stream.read()
                    .decode("utf-8")
                )

                blob = make_diff_str(True, blob)
                diff_result.append(f"Added: {diff_item.b_path}\n{blob}")

            for diff_item in diff.iter_change_type("D"):
                diff_item: Diff
                blob = (
                    cast(IndexObject, diff_item.a_blob)
                    .data_stream.read()
                    .decode("utf-8")
                )

                blob = make_diff_str(False, blob)
                diff_result.append(f"Deleted: {diff_item.a_path}\n{blob}")

            for diff_item in diff.iter_change_type("M"):
                diff_item: Diff

                b_blob: str = (
                    cast(IndexObject, diff_item.b_blob)
                    .data_stream.read()
                    .decode("utf-8")
                )
                a_blob: str = (
                    cast(IndexObject, diff_item.a_blob)
                    .data_stream.read()
                    .decode("utf-8")
                )
                b_blob = make_diff_str(True, b_blob)
                a_blob = make_diff_str(False, a_blob)
                diff_result.append(
                    f"Modified: {diff_item.b_path}\n" + b_blob + "\n" + a_blob
                )
            full_diff = "\n****************\n".join(diff_result).encode()
            token = token_urlsafe(32)
            file_com = FileComm(full_diff, token)
        return pack_diff(file_com.get_port(), token)

    def create_issue(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if result is not None:
            return result
        token = request["connectionToken"]
        username = self.connected_client[token]
        user_id = self.db.username_to_id(username)

        assert user_id is not None

        repo = self.db.repo_by_name(full_repo_name)
        assert repo is not None
        repo_id = repo[0]

        self.db.create_issue(user_id, repo_id, request["title"], request["content"])

        return pack_create_issue()


def make_diff_str(add: bool, diff: str) -> str:
    add_remove_str = "++" if add else "--"
    return "\n".join([f"{add_remove_str}{line}" for line in diff.splitlines()])
