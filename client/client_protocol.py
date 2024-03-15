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


def pack_diff(repo: str, connection_token: str, hash: str) -> Json:
    return {
        "type": "diff",
        "repo": repo,
        "connectionToken": connection_token,
        "hash": hash,
    }


class Commit(TypedDict):
    date: str
    hash: str
    message: str
    authour: str


def pack_view_issues(repo: str, connection_token: str) -> Json:
    return {"type": "viewIssues", "repo": repo, "connectionToken": connection_token}


def pack_delete_issue(id: int, connection_token: str) -> Json:
    return {"type": "deleteIssue", "id": id, "connectionToken": connection_token}


def pack_create_issue(
    repo: str, connection_token: str, title: str, content: str
) -> Json:
    return {
        "type": "createIssue",
        "repo": repo,
        "connectionToken": connection_token,
        "title": title,
        "content": content,
    }


def pack_update_issue(id: int, connection_token: str, title: str, content: str) -> Json:
    return {
        "type": "updateIssue",
        "id": id,
        "connectionToken": connection_token,
        "title": title,
        "content": content,
    }


class Issue(TypedDict):
    username: str
    title: str
    content: str
    id: int


def pack_search_repo(query: str):
    return {"type": "searchRepo", "searchQuery": query}


def pack_create_repo(repo_name: str, is_public: bool, connection_token: str):
    return {
        "type": "createRepo",
        "repoName": repo_name,
        "visibility": is_public,
        "connectionToken": connection_token,
    }
