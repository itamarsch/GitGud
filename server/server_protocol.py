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


def pack_commits(commits: List[Json]) -> Json:
    return {"commits": commits}


def pack_diff(port: int, token: str) -> Json:
    return {"port": port, "token": token}
