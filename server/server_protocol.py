import json
from typing import List

from gitgud_types import Json


def unpack(request: str) -> Json:
    """
    Unpacks a JSON-encoded string into a Python dictionary.

    Args:
        request (str): The JSON-encoded string to be unpacked.

    Returns:
        Json: The unpacked Python dictionary.

    Raises:
        ValueError: If the input is not a valid JSON string or if the unpacked result is not a dictionary.
        ValueError: If the unpacked result does not contain the required "type" key.
    """
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
    """
    Packs an error message into a JSON object.

    Args:
        error (str): The error message to be packed.

    Returns:
        Json: A JSON object containing the error message.
    """
    return {"error": error}


def pack_register(connection_token: str) -> Json:
    """
    Packs the given connection token into a JSON object.

    Parameters:
        connection_token (str): The connection token to be packed.

    Returns:
        Json: The JSON object containing the connection token.
    """
    return {"connectionToken": connection_token}


def pack_login(connection_token: str) -> Json:
    """
    Packs the given connection token into a JSON object.

    Args:
        connection_token (str): The connection token to be packed.

    Returns:
        Json: The JSON object containing the connection token.
    """
    return {"connectionToken": connection_token}


def pack_create_repo(full_repo_name: str) -> Json:
    """
    Create a JSON object with the given full repository name.

    Parameters:
        full_repo_name (str): The full name of the repository.

    Returns:
        Json: A JSON object with the key "fullRepoName" and the value of the full repository name.
    """
    return {"fullRepoName": full_repo_name}


def pack_branches(branches: List[str]) -> Json:
    """
    Packs a list of branch names into a JSON object.

    Args:
        branches (List[str]): A list of branch names.

    Returns:
        Json: A JSON object with the key "branches" and the value being the input list of branch names.
    """
    return {"branches": branches}


def pack_view_file(port: int, token: str) -> Json:
    """
    Packs the given port and token for a file request into a JSON object.

    Args:
        port (int): The port number to be packed.
        token (str): The token to be packed.

    Returns:
        Json: The JSON object containing the port and token.
    """
    return {"port": port, "token": token}


def pack_project_dirs(files: List[str]) -> Json:
    """
    Packs a list of file names into a JSON object.

    Args:
        files (List[str]): A list of file names.

    Returns:
        Json: A JSON object with the key "files" and the value being the input list of file names.
    """
    return {"files": files}


def pack_commit(date: str, hash: str, message: str, authour: str) -> Json:
    """
    Packs a commit into a JSON object.

    Args:
        date (str): The date of the commit.
        hash (str): The hash of the commit.
        message (str): The commit message.
        authour (str): The author of the commit.

    Returns:
        Json: A JSON object representing the commit with the following keys:
            - "date" (str): The date of the commit.
            - "hash" (str): The hash of the commit.
            - "message" (str): The commit message.
            - "authour" (str): The author of the commit.
    """
    return {"date": date, "hash": hash, "message": message, "authour": authour}


def pack_commits(commits: List[Json]) -> Json:
    """
    Packs a list of JSON objects representing commits into a single JSON object.

    Args:
        commits (List[Json]): A list of JSON objects representing commits.

    Returns:
        Json: A JSON object with the key "commits" and the value being the input list of commits.
    """
    return {"commits": commits}


def pack_diff(port: int, token: str) -> Json:
    """
    Packs the given port and token for a diff request into a JSON object.

    Args:
        port (int): The port number to be packed.
        token (str): The token to be packed.

    Returns:
        Json: The JSON object containing the port and token.
    """
    return {"port": port, "token": token}


def pack_create_issue() -> Json:
    """
    Creates a JSON object representing the response for creating a new issue.

    Returns:
        Json: A JSON object representing the response.
    """
    return {}


def pack_issue(username: str, title: str, content: str, id: int):
    """
    Create a dictionary representing an issue with the given username, title, content, and ID.

    Args:
        username (str): The username of the issue creator.
        title (str): The title of the issue.
        content (str): The content of the issue.
        id (int): The ID of the issue.

    Returns:
        dict: A dictionary containing the issue information with the keys "username", "title", "content", and "id".
    """
    """
    Create a dictionary representing an issue with the given username, title, content, and ID.

    Args:
        username (str): The username of the issue creator.
        title (str): The title of the issue.
        content (str): The content of the issue.
        id (int): The ID of the issue.

    Returns:
        dict: A dictionary containing the issue information with the keys "username", "title", "content", and "id".
    """
    return {"username": username, "title": title, "content": content, "id": id}


def pack_view_issues(issues: List[Json]) -> Json:
    """
    Packs a list of JSON objects representing issues into a single JSON object.

    Args:
        issues (List[Json]): A list of JSON objects representing issues.

    Returns:
        Json: A JSON object with the key "issues" and the value being the input list of issues.
    """
    return {"issues": issues}


def pack_delete_issue() -> Json:
    """
    Creates a JSON object representing the response for deleting an issue.

    Returns:
        Json: A JSON object representing the response.
    """
    return {}


def pack_update_issue() -> Json:
    """
    Creates a JSON object representing the response for updating an issue.

    Returns:
        Json: A JSON object representing the response.
    """
    return {}


def pack_create_pull_request() -> Json:
    """
    Creates a JSON object representing the response for creating a new pull request.

    Returns:
        Json: A JSON object representing the response.
    """
    return {}


def pack_pull_request(
    username: str,
    title: str,
    from_branch: str,
    into_branch: str,
    id: int,
    approved: bool,
) -> Json:
    """
    Packs the given pull request information into a JSON object.

    Args:
        username (str): The username of the pull request creator.
        title (str): The title of the pull request.
        from_branch (str): The branch the pull request is coming from.
        into_branch (str): The branch the pull request is going into.
        id (int): The ID of the pull request.
        approved (bool): Whether the pull request is approved or not.

    Returns:
        Json: A JSON object representing the pull request with the following keys:
            - username (str): The username of the pull request creator.
            - title (str): The title of the pull request.
            - fromBranch (str): The branch the pull request is coming from.
            - intoBranch (str): The branch the pull request is going into.
            - approved (bool): Whether the pull request is approved or not.
            - id (int): The ID of the pull request.
    """
    return {
        "username": username,
        "title": title,
        "fromBranch": from_branch,
        "intoBranch": into_branch,
        "approved": approved,
        "id": id,
    }


def pack_view_pull_requests(pull_requests: List[Json]) -> Json:
    """
    Packs a list of JSON objects representing pull requests into a single JSON object.

    Args:
        pull_requests (List[Json]): A list of JSON objects representing pull requests.

    Returns:
        Json: A JSON object with the key "pullRequests" and the value being the input list of pull requests.
    """
    return {"pullRequests": pull_requests}


def pack_delete_pr() -> Json:
    """
    Packs the information for deleting a pull request into a JSON object.

    Returns:
        Json: An empty JSON object representing the response for deleting a pull request.
    """
    return {}


def pack_update_pr() -> Json:
    """
    Packs the information for updating a pull request into a JSON object.

    Returns:
        Json: An empty JSON object representing the response for updating a pull request.
    """
    return {}


def pack_validate_token(valid: bool) -> Json:
    """
    Packs the given boolean value into a JSON object representing a validation token.

    Args:
        valid (bool): A boolean value indicating the validity of the token.

    Returns:
        Json: A JSON object with a single key "valid" and its corresponding boolean value.
    """
    return {"valid": valid}


def pack_search_repo(repos: List[str]) -> Json:
    """
    Packs a list of repository names into a JSON object.

    Args:
        repos (List[str]): A list of repository names.

    Returns:
        Json: A JSON object with the key "repos" and the value being the input list of repository names.
    """
    return {"repos": repos}
