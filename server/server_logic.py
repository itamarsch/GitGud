import json
from typing import Dict, List, Tuple, cast, Union, Optional
import datetime
from gitdb.util import os
from database import DB
from git_manager import GitManager
from queue import Queue
from diff import commits_between_branches, get_diff_string, triple_dot_diff
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
    pack_search_repo,
    pack_update_issue,
    pack_update_pr,
    pack_validate_password,
    pack_view_file,
    pack_view_issues,
    pack_view_pull_requests,
    unpack,
)
from git import GitCommandError, Repo, Commit as GitCommit
from server_comm import FileComm, ServerComm
from gitgud_types import Action, IssuePr, Json, Address, commit_page_size
from secrets import token_urlsafe
from fuzzywuzzy import process


from ssh_validation import validate_pubkey


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
        """
        Process a request from the queue, apply an action, and send the response back to the client.
        """
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
        """
        A function to apply a given action to a JSON input assuming the keys are validated and return the result as JSON.
        Parameters:
            self: the instance of the class
            json: the JSON input
        Returns:
            JSON: the result of applying the action to the JSON input
        """
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
                ["repo", "title", "connectionToken", "fromBranch", "intoBranch"],
            ),
            "viewPullRequests": (self.view_pull_requests, ["repo", "connectionToken"]),
            "deletePullRequest": (self.delete_pull_request, ["id", "connectionToken"]),
            "updatePullRequest": (
                self.update_pull_request,
                ["id", "connectionToken", "title", "fromBranch", "intoBranch"],
            ),
            "prDiff": (self.pr_diff, ["connectionToken", "id"]),
            "prCommits": (self.pr_commits, ["connectionToken", "id", "page"]),
            "validateConnection": (self.validate_connection, ["tokenForValidation"]),
            "searchRepo": (self.search_repo, ["searchQuery"]),
        }

    def generate_new_connection_token(self, username: str) -> str:
        """
        Generate a new connection token for a given username.

        Parameters:
            username (str): The username for which the token is generated.

        Returns:
            str: The newly generated connection token.
        """
        token = token_urlsafe(32)
        self.connected_client[token] = username
        return token

    def validate_repo_request(
        self, repo: str, connectionToken: str
    ) -> Union[Json, Tuple[int, str, bool]]:
        """
        Validate the repository request by checking if the user and repo are valid.
        Parameters:
            repo (str): A string representing the user and repo separated by a forward slash.
            connectionToken (str): A string representing the connection token for the request.
        Returns:
            Union[Json, Tuple[int, str, bool]]: Either repository data if valid, or an error message with status code and boolean.
        """
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
        """
        A function to register a user with a unique username, password, and SSH key.

        Parameters:
            request (Json): A JSON object containing the user's information including username, password, and SSH key.

        Returns:
            Json: A JSON object containing a token after successful registration.
        """
        username = request["username"]
        password_hash = request["password"]
        ssh_key = request["sshKey"]
        if self.db.user_exists(username):
            return pack_error("User exists")
        if not validate_pubkey(ssh_key):
            return pack_error("Invalid ssh key")

        if not username:
            return pack_error("Invalid username")

        self.db.add_user(username, password_hash)
        self.git_manager.add_ssh_key(username, ssh_key)

        token = self.generate_new_connection_token(username)

        return pack_register(token)

    def login(self, request: Json) -> Json:
        """
        A function that handles user login. Takes a JSON request with username and password, validates the user, generates a new connection token, and returns the login response in a JSON format.
        Parameters:
            request (Json): A JSON object containing the username and password.
        Returns:
            Json: A JSON object containing the login token.
        """
        username = request["username"]
        password_hash = request["password"]

        if not self.db.validate_user(username, password_hash):
            return pack_error("Incorrect password")

        token = self.generate_new_connection_token(username)

        return pack_login(token)

    def create_repo(self, request: Json) -> Json:
        """
        Create a new repository based on the provided request JSON.

        Parameters:
            request (Json): A JSON object containing keys "repoName", "visibility", and "connectionToken".

        Returns:
            Json: A JSON object representing the result of the repository creation process.
        """
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

        return pack_create_repo(f"{username}/{repo_name}")

    def branches(self, request: Json) -> Json:
        """
        A function to retrieve branches of a repository given a JSON request.

        Parameters:
            request (Json): A JSON object containing repository information.

        Returns:
            Json: A JSON object containing information about the branches of the repository.
        """
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if isinstance(result, dict):
            return result

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            branches = branches_of_repo(r)
        return pack_branches(branches)

    def view_file(self, request: Json) -> Json:
        """
        A function to view a file based on the repo, file path and branch.

        Parameters:
            request (Json): A JSON object containing information about the file to be viewed.

        Returns:
            Json: The result of viewing the file, either the file content or an error message.
        """
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
        """
        A function to handle requests for files within a directory in a repository.

        Parameters:
            request (Json): A JSON object containing information about the request, including the repository, directory, and branch.

        Returns:
            Json: A JSON object representing the result of the request, which could be project directories or an error message.
        """
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

    @staticmethod
    def pack_git_commits(commits: List[GitCommit]) -> List[Json]:
        """
        Generate a JSON representation of a list of Git commits.

        Parameters:
            commits (List[GitCommit]): A list of GitCommit objects to be processed.

        Returns:
            List[Json]: A list of JSON objects representing each Git commit.
        """
        res = []
        for c in commits:
            date = datetime.datetime.fromtimestamp(c.authored_date).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            authour = str(c.author)
            hash = c.hexsha
            message = cast(str, c.message)
            res.append(pack_commit(date, hash, message, authour))
        return res

    def commits(self, request: Json) -> Json:
        """
        A function to retrieve a specified number of commits from a given repository branch.

        Parameters:
            request (Json): A JSON object containing information about the repository and connection token.

        Returns:
            Json: A JSON object containing the specified number of commits from the repository branch.
        """
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
                    f"origin/{branch}",
                    skip=page * commit_page_size,
                    max_count=commit_page_size,
                )
            )

            commits = pack_commits(ServerLogic.pack_git_commits(fifty_first_commits))
            token = token_urlsafe(32)
            file_com = FileComm(json.dumps(commits).encode(), token)
            port = file_com.get_port()
            return pack_view_file(port, token)

    def pr_commits(self, request: Json) -> Json:
        """
        A function that processes and returns commits related to a pull request.

        Parameters:
            request (Json): A JSON object containing the pull request ID and connection token. and commits page

        Returns:
            Json: A JSON object representing the commits.
        """
        error = self.validate_issue_or_pr(
            request["id"], request["connectionToken"], "PR"
        )

        if error is not None:
            return error

        (owner, repo_name) = cast(
            Tuple[str, str], self.db.repo_and_repo_owner_of_pr(request["id"])
        )
        # Saftey: Id validation in validate_issue_or_pr
        (into_branch, from_branch) = cast(
            Tuple[str, str], self.db.pr_branches(request["id"])
        )

        full_repo_name = f"{owner}/{repo_name}"
        page = int(request["page"])

        # Safe to clone, repo exists in database
        with RepoClone(full_repo_name) as r:
            error = self.validate_pr_branches(
                r, request["id"], into_branch, from_branch
            )
            if error is not None:
                return error

            fifty_first_commits = list(
                commits_between_branches(
                    r, f"origin/{from_branch}", f"origin/{into_branch}", page
                )
            )

            commits = pack_commits(ServerLogic.pack_git_commits(fifty_first_commits))
            token = token_urlsafe(32)
            file_com = FileComm(json.dumps(commits).encode(), token)
            port = file_com.get_port()
            return pack_view_file(port, token)

    def diff(self, request: Json) -> Json:
        """
        Generate a diff for a given commit hash in a repository.

        Parameters:
            request (Json): A JSON object containing the repository name, connection token, and commit hash.

        Returns:
            Json: A JSON object with the port and token for the diff as a file request
        """
        full_repo_name = cast(str, request["repo"])
        result = self.validate_repo_request(full_repo_name, request["connectionToken"])
        if isinstance(result, dict):
            return result

        with RepoClone(full_repo_name) as r:
            hash = request["hash"]
            try:
                commit = r.commit(hash)
                parent = commit.parents[0]
            except Exception:
                return pack_error("Invalid commit hash")

            token = token_urlsafe(32)
            diff: str = commit.repo.git.show(commit.hexsha)

            file_com = FileComm(json.dumps(get_diff_string(diff)).encode(), token)
        return pack_diff(file_com.get_port(), token)

    def create_issue(self, request: Json) -> Json:
        """
        Create an issue for a given repository.

        Parameters:
            request (Json): The JSON request containing information about the repository and the issue.

        Returns:
            Json: The JSON response containing information about the created issue.
        """
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
        """
        A function to view the list of issues for a given repository.

        Parameters:
            request (Json): A JSON object containing the repo and connection token.

        Returns:
            Json: A JSON object containing the list of issues for the repository.
        """
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
        """
        Validate the given issue or PR with the provided ID, connection token, and issue or PR object.

        Parameters:
            id (int): The ID of the issue or PR to validate.
            connection_token (str): The connection token for authorization.
            issue (IssuePr): Enum to say if you want to validate an issue or PR

        Returns:
            Optional[Json]: Returns an error message if the ID is invalid or the user doesn't have permissions, otherwise returns None.
        """
        match issue:
            case "Issue":
                repo = self.db.repo_and_repo_owner_of_issue(id)
            case "PR":
                repo = self.db.repo_and_repo_owner_of_pr(id)

        if repo is None:
            return pack_error("Invalid id")
        error_or_repo = self.validate_repo_request(
            f"{repo[0]}/{repo[1]}", connection_token
        )
        if isinstance(error_or_repo, dict):
            return error_or_repo
        return None

    def delete_issue(self, request: Json) -> Json:
        """
        A function that deletes an issue based on the provided request JSON.
        Parameters:
            - request (Json) - JSON object containing the id and connectionToken of the issue to be deleted.
        Returns:
            - Json: JSON response indicating the success or failure of the deletion operation.
        """
        error = self.validate_issue_or_pr(
            request["id"], request["connectionToken"], "Issue"
        )
        if error is not None:
            return error

        self.db.delete_issue(request["id"])
        return pack_delete_issue()

    def update_issue(self, request: Json) -> Json:
        """
        Update an issue with the provided information.

        Parameters:
            request (Json): A JSON object containing the details for updating the issue.

        Returns:
            Json: JSON response indicating the success or failure of the update operation.
        """
        id = request["id"]
        connectionToken = request["connectionToken"]
        error = self.validate_issue_or_pr(id, connectionToken, "Issue")
        if error is not None:
            return error

        self.db.update_issue(id, request["title"], request["content"])
        return pack_update_issue()

    def create_pull_request(self, request: Json) -> Json:
        """
        A function to create a pull request with the given request JSON object.

        Parameters:
            request (Json): The JSON object containing information about the pull request.

        Returns:
            Json: The result of the pull request creation process, either an error or the created pull request.
        """
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
        """
        A method to view pull requests based on the given request JSON.

        Parameters:
            request (Json): The request JSON containing repo and connection token.

        Returns:
            Json: A JSON response with the view of pull requests.
        """
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
                (id, _, _, from_branch, into_branch, _) = pr
                if from_branch not in branches or into_branch not in branches:
                    pull_requests.pop(i)
                    self.db.delete_pr(id)

        return pack_view_pull_requests(
            [
                pack_pull_request(pr[1], pr[2], pr[3], pr[4], pr[0], pr[5])
                for pr in pull_requests
            ]
        )

    def delete_pull_request(self, request: Json) -> Json:
        """
        Deletes a pull request based on the provided request JSON object.

        Parameters:
            request (Json): The JSON object containing the pull request id and connection token.

        Returns:
            Json: The JSON response after deleting the pull request.
        """
        id = request["id"]
        connectionToken = request["connectionToken"]
        error = self.validate_issue_or_pr(id, connectionToken, "PR")
        if error is not None:
            return error

        self.db.delete_pr(id)
        return pack_delete_pr()

    def update_pull_request(self, request: Json) -> Json:
        """
        Update a pull request in the database with the provided information.

        Parameters:
            request (Json): A JSON object containing the details of the pull request including id, connectionToken, fromBranch, intoBranch, and title.

        Returns:
            Json: A JSON object representing the updated pull request.
        """
        id = request["id"]
        connectionToken = request["connectionToken"]
        from_branch = request["fromBranch"]
        into_branch = request["intoBranch"]
        title = request["title"]
        error = self.validate_issue_or_pr(id, connectionToken, "PR")

        if error is not None:
            return error

        (owner, repo_name) = cast(
            Tuple[str, str], self.db.repo_and_repo_owner_of_pr(id)
        )
        full_repo = f"{owner}/{repo_name}"

        with RepoClone(full_repo) as repo:
            error = self.validate_pr_branches(
                repo, request["id"], into_branch, from_branch
            )
            if error is not None:
                return error
        self.db.update_pr(id, title, from_branch, into_branch)
        return pack_update_pr()

    def validate_pr_branches(
        self, repo: Repo, id: int, into_branch: str, from_branch: str
    ) -> Optional[Json]:
        """
        Validate the branches of a pull request.

        Parameters:
            repo (Repo): The repository object.
            id (int): The id of the pull request.
            into_branch (str): The branch being merged into.
            from_branch (str): The branch being merged from.

        Returns:
            Optional[Json]: None if branches are valid, error message if not.
        """

        repo_branches = branches_of_repo(repo)
        if into_branch not in repo_branches or from_branch not in repo_branches:
            self.db.delete_pr(id)
            return pack_error("Invalid pr branches, deleting")
        return None

    def pr_diff(self, request: Json) -> Json:
        """
        A function to calculate the difference between two branches in a pull request.

        Parameters:
            request (Json): The JSON object containing the request data.

        Returns:
            Json: A JSON object with the port and token for the diff as a file request
        """
        error = self.validate_issue_or_pr(
            request["id"], request["connectionToken"], "PR"
        )
        if error is not None:
            return error

        (owner, repo_name) = cast(
            Tuple[str, str], self.db.repo_and_repo_owner_of_pr(request["id"])
        )

        (into_branch, from_branch) = cast(
            Tuple[str, str], self.db.pr_branches(request["id"])
        )  # Saftey: id validation in validate_issue_or_pr

        if into_branch.startswith("origin/") or from_branch.startswith("origin/"):
            return pack_error("Use only branch name no need for remote")

        with RepoClone(f"{owner}/{repo_name}") as r:
            error = self.validate_pr_branches(
                r, request["id"], into_branch, from_branch
            )

            if error is not None:
                return error

            into_branch = f"origin/{into_branch}"
            from_branch = f"origin/{from_branch}"
            diff = triple_dot_diff(r, into_branch, from_branch)
            if not diff:
                return pack_error("No common base")

            token = token_urlsafe(32)
            full_diff = get_diff_string(diff)

            file_com = FileComm(json.dumps(full_diff).encode(), token)
        return pack_diff(file_com.get_port(), token)

    def validate_connection(self, request: Json) -> Json:
        """
        Validate the connection using the provided request JSON object.

        Parameters:
            request (Json): The JSON object containing the token for validation.

        Returns:
            Json: The result of the validation process.
        """
        return pack_validate_password(
            request["tokenForValidation"] in self.connected_client
        )

    def search_repo(self, request: Json) -> Json:
        """
        A function that searches the repository based on a given search query.

        Parameters:
            request (Json): The JSON object containing the search query.

        Returns:
            Json: The search results packed in a JSON object.
        """
        all_repos = self.db.all_repos()
        names = list(map(lambda a: f"{a[1]}/{a[2]}", all_repos))
        results: List[Tuple[str, int]] = cast(
            List[Tuple[str, int]],
            process.extract(request["searchQuery"], names, limit=10),
        )
        results = list(filter(lambda a: a[1] > 70, results))
        repo_results = list(map(lambda a: a[0], results))

        return pack_search_repo(repo_results)


def branches_of_repo(repo: Repo) -> List[str]:
    """
    Generate a list of branch names for the given repository.

    Parameters:
    repo (Repo): The repository for which to list branches.

    Returns:
    List[str]: A list of branch names without the 'origin/' prefix.
    """
    return [branch.name.removeprefix("origin/") for branch in repo.remote().refs]
