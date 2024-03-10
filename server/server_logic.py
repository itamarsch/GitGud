import json
from typing import Dict, List, Tuple, cast, Union, Optional
import datetime
from gitdb.util import os
from database import DB
from git_manager import GitManager
from queue import Queue
from diff import get_diff_string
from repo_clone import RepoClone
from server_protocol import (
    pack_branches,
    pack_commit,
    pack_commits,
    pack_create_issue,
    pack_create_pull_request,
    pack_create_repo,
    pack_delete_issue,
    pack_delete_pr,
    pack_diff,
    pack_error,
    pack_issue,
    pack_login,
    pack_project_dirs,
    pack_pull_request,
    pack_register,
    pack_update_issue,
    pack_update_pr,
    pack_validate_password,
    pack_view_file,
    pack_view_issues,
    pack_view_pull_requests,
    unpack,
)
from git import GitCommandError, Repo
from server_comm import FileComm, ServerComm
from gitgud_types import Action, IssuePr, Json, Address
from secrets import token_urlsafe

commit_page_size = 20


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
            "viewIssues": (self.view_issues, ["repo", "connectionToken"]),
            "deleteIssue": (self.delete_issue, ["id", "connectionToken"]),
            "updateIssue": (
                self.update_issue,
                ["id", "connectionToken", "title", "content"],
            ),
            "createPullRequest": (
                self.create_pull_request,
                ["repo", "connectionToken", "fromBranch", "intoBranch"],
            ),
            "viewPullRequests": (self.view_pull_requests, ["repo", "connectionToken"]),
            "deletePullRequest": (self.delete_pull_request, ["id", "connectionToken"]),
            "updatePullRequest": (
                self.update_pull_request,
                ["id", "connectionToken", "title", "fromBranch", "intoBranch"],
            ),
            "prDiff": (self.pr_diff, ["connectionToken", "prId"]),
            "validateConnection": (self.validate_connection, ["tokenForValidation"]),
        }

    def generate_new_connection_token(self, username: str) -> str:
        token = token_urlsafe(32)
        self.connected_client[token] = username
        return token

    def validate_repo_request(
        self, repo: str, connectionToken: str
    ) -> Union[Json, Tuple[int, str, bool]]:
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

        return sql_repo_data

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
        if isinstance(result, dict):
            return result

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            branches = branches_of_repo(r)
        return pack_branches(branches)

    def view_file(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if isinstance(result, dict):
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
        if isinstance(result, dict):
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
        if isinstance(result, dict):
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
                message = cast(str, c.message)
                commits_list.append(pack_commit(date, hash, message, authour))

            return pack_commits(commits_list)

    def diff(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if isinstance(result, dict):
            return result

        with RepoClone(full_repo_name) as r:
            hash = request["hash"]
            try:
                commit = r.commit(hash)
            except Exception:
                return pack_error("Invalid commit hash")

            token = token_urlsafe(32)
            full_diff = get_diff_string(commit.parents[0].diff(commit))
            file_com = FileComm(full_diff.encode(), token)
        return pack_diff(file_com.get_port(), token)

    def create_issue(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        error_or_repo = self.validate_repo_request(
            full_repo_name, request["connectionToken"]
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo
        token = request["connectionToken"]
        username = self.connected_client[token]
        user_id = self.db.username_to_id(username)
        assert user_id is not None

        repo_id = error_or_repo[0]

        self.db.create_issue(user_id, repo_id, request["title"], request["content"])

        return pack_create_issue()

    def view_issues(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        error_or_repo = self.validate_repo_request(
            full_repo_name, request["connectionToken"]
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo

        repo_id = error_or_repo[0]

        issues = self.db.issues(repo_id)
        return pack_view_issues(
            [pack_issue(issue[1], issue[2], issue[3], issue[0]) for issue in issues]
        )

    def validate_issue_or_pr(
        self, id: int, connection_token: str, issue: IssuePr
    ) -> Optional[Json]:
        if issue == "Issue":
            repo = self.db.repo_and_owner_of_issue(id)
        else:
            repo = self.db.repo_and_owner_of_pr(id)
        if repo is None:
            return pack_error("Invalid id")
        error_or_repo = self.validate_repo_request(
            f"{repo[0]}/{repo[1]}", connection_token
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo
        return None

    def delete_issue(self, request: Json) -> Json:
        error = self.validate_issue_or_pr(
            request["id"], request["connectionToken"], "Issue"
        )
        if error is not None:
            return error

        self.db.delete_issue(request["id"])
        return pack_delete_issue()

    def update_issue(self, request: Json) -> Json:
        id = request["id"]
        connectionToken = request["connectionToken"]
        error = self.validate_issue_or_pr(id, connectionToken, "Issue")
        if error is not None:
            return error

        self.db.update_issue(id, request["title"], request["content"])
        return pack_update_issue()

    def create_pull_request(self, request: Json) -> Json:
        error_or_repo = self.validate_repo_request(
            request["repo"], request["connectionToken"]
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo

        username = self.connected_client[request["connectionToken"]]
        user_id = self.db.username_to_id(username)

        # Repo validation asserts this
        assert user_id is not None

        from_branch = request["fromBranch"]
        into_branch = request["intoBranch"]
        repo_id = error_or_repo[0]
        with RepoClone(request["repo"]) as repo:
            branches = branches_of_repo(repo)
            if not (from_branch in branches and into_branch in branches):
                return pack_error("Invalid branch names")

        self.db.create_pr(
            request["title"],
            from_branch,
            into_branch,
            repo_id,
            user_id,
        )
        return pack_create_pull_request()

    def view_pull_requests(self, request: Json) -> Json:
        error_or_repo = self.validate_repo_request(
            request["repo"], request["connectionToken"]
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo

        repo_id = error_or_repo[0]

        pull_requests = self.db.pull_requests(repo_id)

        with RepoClone(request["repo"]) as repo:
            branches = branches_of_repo(repo)
            for i, pr in enumerate(pull_requests):
                (id, _, _, from_branch, into_branch) = pr
                if from_branch not in branches or into_branch not in branches:
                    pull_requests.pop(i)
                    self.db.delete_pr(id)

        return pack_view_pull_requests(
            [
                pack_pull_request(issue[1], issue[2], issue[3], issue[4], issue[0])
                for issue in pull_requests
            ]
        )

    def delete_pull_request(self, request: Json) -> Json:
        id = request["id"]
        connectionToken = request["connectionToken"]
        error = self.validate_issue_or_pr(id, connectionToken, "PR")
        if error is not None:
            return error

        self.db.delete_pr(id)
        return pack_delete_pr()

    def update_pull_request(self, request: Json) -> Json:
        id = request["id"]
        connectionToken = request["connectionToken"]
        from_branch = request["fromBranch"]
        into_branch = request["intoBranch"]
        title = request["title"]
        error = self.validate_issue_or_pr(id, connectionToken, "PR")
        if error is not None:
            return error

        with RepoClone(request["repo"]) as repo:
            branches = branches_of_repo(repo)
            if from_branch not in branches or into_branch not in branches:
                return pack_error("Invalid branches")
        self.db.update_pr(id, title, from_branch, into_branch)
        return pack_update_pr()

    def pr_diff(self, request: Json) -> Json:
        full_repo_name = cast(str, request["repo"])
        error = self.validate_issue_or_pr(
            request["prId"], request["connectionToken"], "PR"
        )
        if error is not None:
            return error

        branches = cast(
            Tuple[str, str], self.db.pr_branches(request["prId"])
        )  # Saftey: id validation in validate_issue_or_pr

        if branches[0].startswith("origin/") or branches[1].startswith("origin/"):
            return pack_error("Use only branch name no need for remote")

        with RepoClone(full_repo_name) as r:

            diff = r.git.diff(f"origin/{branches[0]}...origin/{branches[1]}")
            print(diff)

            token = token_urlsafe(32)
            full_diff = get_diff_string(diff)

            file_com = FileComm(full_diff.encode(), token)
        return pack_diff(file_com.get_port(), token)

    def validate_connection(self, request: Json) -> Json:
        return pack_validate_password(
            request["tokenForValidation"] in self.connected_client
        )


def branches_of_repo(repo: Repo) -> List[str]:
    return [branch.name.removeprefix("origin/") for branch in repo.remote().refs]
