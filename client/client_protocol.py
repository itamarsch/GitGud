from typing import TypedDict
from gitgud_types import Json


def pack_login(username: str, password: str) -> Json:
    return {"type": "login", "username": username, "password": password}


def pack_register(username: str, password: str, ssh_key: str) -> Json:
    return {
        "type": "register",
        "username": username,
        "password": password,
        "sshKey": ssh_key,
    }


def pack_branches(repo: str, connectionToken: str) -> Json:
    return {"type": "branches", "repo": repo, "connectionToken": connectionToken}


def pack_project_directory(
    directory: str, repo: str, branch: str, connection_token: str
):
    return {
        "type": "projectDirectory",
        "directory": directory,
        "repo": repo,
        "branch": branch,
        "connectionToken": connection_token,
    }


def pack_file_request(repo: str, connection_token: str, file_path: str, branch: str):
    return {
        "type": "viewFile",
        "repo": repo,
        "connectionToken": connection_token,
        "filePath": file_path,
        "branch": branch,
    }


def pack_validate_token(token: str):
    return {"type": "validateConnection", "tokenForValidation": token}


def pack_commits(repo: str, connection_token: str, branch: str, page: int):
    return {
        "type": "commits",
        "repo": repo,
        "connectionToken": connection_token,
        "branch": branch,
        "page": page,
    }


class Commit(TypedDict):
    date: str
    hash: str
    message: str
    authour: str
