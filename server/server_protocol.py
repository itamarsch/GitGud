import json
from typing import List

from gitgud_types import Json


def unpack(request: str) -> Json:
    try:
        result = json.loads(request)
    except json.JSONDecodeError:
        raise ValueError("Invalid json")

    if not isinstance(result, dict):
        raise ValueError("Value nees to be Json object")

    if "type" not in result.keys():
        raise ValueError("Every request needs type value")
    return result


def pack_error(error: str) -> Json:
    return {"error": error}


def pack_register(connection_token: str) -> Json:
    return {"connectionToken": connection_token}


def pack_login(connection_token: str) -> Json:
    return {"connectionToken": connection_token}


def pack_create_repo() -> Json:
    return {}


def pack_branches(branches: List[str]) -> Json:
    return {"branches": branches}


def pack_view_file(port: int, token: str) -> Json:
    return {"port": port, "token": token}


def pack_project_dirs(files: List[str]) -> Json:
    return {"files": files}


def pack_commit(date: str, hash: str, message: str, authour: str) -> Json:
    return {"date": date, "hash": hash, "message": message, "authour": authour}


def pack_commits(commits: List[Json]) -> Json:
    return {"commits": commits}


def pack_diff(port: int, token: str) -> Json:
    return {"port": port, "token": token}


def pack_create_issue() -> Json:
    return {}


def pack_issue(username: str, title: str, content: str, id: int):
    return {"username": username, "title": title, "content": content, "id": id}


def pack_view_issues(issues: List[Json]) -> Json:
    return {"issues": issues}


def pack_delete_issue() -> Json:
    return {}


def pack_update_issue() -> Json:
    return {}


def pack_create_pull_request() -> Json:
    return {}


def pack_pull_request(
    username: str, title: str, from_branch: str, into_branch: str, id: int
):
    return {
        "username": username,
        "title": title,
        "fromBranch": from_branch,
        "intoBranch": into_branch,
        "id": id,
    }


def pack_view_pull_requests(pull_requests: List[Json]) -> Json:
    return {"pullRequests": pull_requests}


def pack_delete_pr() -> Json:
    return {}


def pack_update_pr() -> Json:
    return {}


def pack_validate_password(valid: bool) -> Json:
    return {"valid": valid}
