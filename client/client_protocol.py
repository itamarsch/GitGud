import sys

if sys.version_info[0] == 3 and sys.version_info[1] < 8:

    class A:
        pass

    TypedDict = A
else:
    from typing import TypedDict
from gitgud_types import Json


def pack_login(username: str, password: str) -> Json:
    """
    Packs the given username and password into a JSON object with a "type" key set to "login".

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "login".
            - username (str): The username of the user.
            - password (str): The password of the user.
    """
    return {"type": "login", "username": username, "password": password}


def pack_register(username: str, password: str, ssh_key: str) -> Json:
    """
    Packs the given username, password, and SSH key into a JSON object with a "type" key set to "register".

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        ssh_key (str): The SSH key of the user.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "register".
            - username (str): The username of the user.
            - password (str): The password of the user.
            - sshKey (str): The SSH key of the user.
    """
    return {
        "type": "register",
        "username": username,
        "password": password,
        "sshKey": ssh_key,
    }


def pack_branches(repo: str, connectionToken: str) -> Json:
    """
    Packs the given repository and connection token into a JSON object with a "type" key set to "branches".

    Args:
        repo (str): The repository name.
        connectionToken (str): The connection token.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "branches".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
    """
    return {"type": "branches", "repo": repo, "connectionToken": connectionToken}


def pack_project_directory(
    directory: str, repo: str, branch: str, connection_token: str
):
    """
    Packs the given directory, repository, branch, and connection token into a JSON object with a "type" key set to "projectDirectory".

    Args:
        directory (str): The directory path.
        repo (str): The repository name.
        branch (str): The branch name.
        connection_token (str): The connection token.

    Returns:
        dict: A JSON object with the following keys:
            - type (str): The type of the request, set to "projectDirectory".
            - directory (str): The directory path.
            - repo (str): The repository name.
            - branch (str): The branch name.
            - connectionToken (str): The connection token.
    """
    return {
        "type": "projectDirectory",
        "directory": directory,
        "repo": repo,
        "branch": branch,
        "connectionToken": connection_token,
    }


def pack_file_request(repo: str, connection_token: str, file_path: str, branch: str):
    """
    Packs the given repository, connection token, file path, and branch into a JSON object with a "type" key set to "viewFile".

    Parameters:
        repo (str): The repository name.
        connection_token (str): The connection token.
        file_path (str): The file path.
        branch (str): The branch name.

    Returns:
        dict: A JSON object with the following keys:
            - type (str): The type of the request, set to "viewFile".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
            - filePath (str): The file path.
            - branch (str): The branch name.
    """
    return {
        "type": "viewFile",
        "repo": repo,
        "connectionToken": connection_token,
        "filePath": file_path,
        "branch": branch,
    }


def pack_validate_token(token: str):
    """
    Packs the given token for validation into a JSON object.

    Args:
        token (str): The token to be packed for validation.

    Returns:
        dict: A JSON object containing the token for validation with the following keys:
            - type (str): The type of the request, set to "validateConnection".
            - tokenForValidation (str): The token to be validated.
    """
    return {"type": "validateConnection", "tokenForValidation": token}


def pack_commits(repo: str, connection_token: str, branch: str, page: int):
    """
    Packs the given repository, connection token, branch, and page into a JSON object with a "type" key set to "commits".

    Parameters:
        repo (str): The repository name.
        connection_token (str): The connection token.
        branch (str): The branch name.
        page (int): The page number.

    Returns:
        dict: A JSON object with the following keys:
            - type (str): The type of the request, set to "commits".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
            - branch (str): The branch name.
            - page (int): The page number.
    """
    return {
        "type": "commits",
        "repo": repo,
        "connectionToken": connection_token,
        "branch": branch,
        "page": page,
    }


def pack_diff(repo: str, connection_token: str, hash: str) -> Json:
    """
    Packs the given repository, connection token, and commit hash into a JSON object with a "type" key set to "diff".

    Args:
        repo (str): The repository name.
        connection_token (str): The connection token.
        hash (str): The commit hash.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "diff".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
            - hash (str): The commit hash.
    """
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
    """
    Packs the given repository and connection token into a JSON object with a "type" key set to "viewIssues".

    Parameters:
        repo (str): The repository name.
        connection_token (str): The connection token.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "viewIssues".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
    """
    return {"type": "viewIssues", "repo": repo, "connectionToken": connection_token}


def pack_delete_issue(id: int, connection_token: str) -> Json:
    """
    Packs the given issue ID and connection token into a JSON object with a "type" key set to "deleteIssue".

    Parameters:
        id (int): The ID of the issue to be deleted.
        connection_token (str): The connection token for authorization.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "deleteIssue".
            - id (int): The ID of the issue to be deleted.
            - connectionToken (str): The connection token for authorization.
    """
    return {"type": "deleteIssue", "id": id, "connectionToken": connection_token}


def pack_create_issue(
    repo: str, connection_token: str, title: str, content: str
) -> Json:
    """
    Packs the given repository, connection token, title, and content into a JSON object with a "type" key set to "createIssue".

    Parameters:
        repo (str): The repository name.
        connection_token (str): The connection token.
        title (str): The title of the issue.
        content (str): The content of the issue.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "createIssue".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
            - title (str): The title of the issue.
            - content (str): The content of the issue.
    """
    return {
        "type": "createIssue",
        "repo": repo,
        "connectionToken": connection_token,
        "title": title,
        "content": content,
    }


def pack_update_issue(id: int, connection_token: str, title: str, content: str) -> Json:
    """
    Packs the given issue ID, connection token, title, and content into a JSON object with a "type" key set to "updateIssue".

    Parameters:
        id (int): The ID of the issue to be updated.
        connection_token (str): The connection token for authorization.
        title (str): The new title for the issue.
        content (str): The new content for the issue.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "updateIssue".
            - id (int): The ID of the issue to be updated.
            - connectionToken (str): The connection token for authorization.
            - title (str): The new title for the issue.
            - content (str): The new content for the issue.
    """
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
    """
    Packs the given search query into a JSON object with a "type" key set to "searchRepo".

    Args:
        query (str): The search query.

    Returns:
        dict: A JSON object with the following keys:
            - type (str): The type of the request, set to "searchRepo".
            - searchQuery (str): The search query.
    """
    return {"type": "searchRepo", "searchQuery": query}


def pack_create_repo(repo_name: str, is_public: bool, connection_token: str):
    """
    Packs the given repository name, visibility, and connection token into a JSON object with a "type" key set to "createRepo".

    Args:
        repo_name (str): The name of the repository.
        is_public (bool): A boolean indicating if the repository is public.
        connection_token (str): The connection token.

    Returns:
        dict: A JSON object with the following keys:
            - type (str): The type of the request, set to "createRepo".
            - repoName (str): The name of the repository.
            - visibility (bool): A boolean indicating if the repository is public.
            - connectionToken (str): The connection token.
    """
    return {
        "type": "createRepo",
        "repoName": repo_name,
        "visibility": is_public,
        "connectionToken": connection_token,
    }


def pack_view_prs(repo: str, connection_token: str) -> Json:
    """
    Packs the given repository and connection token into a JSON object with a "type" key set to "viewPullRequests".

    Parameters:
        repo (str): The repository name.
        connection_token (str): The connection token.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "viewPullRequests".
            - repo (str): The repository name.
            - connectionToken (str): The connection token.
    """
    return {
        "type": "viewPullRequests",
        "repo": repo,
        "connectionToken": connection_token,
    }


def pack_update_pull_request(
    id: int, connection_token: str, title: str, from_branch: str, into_branch: str
):
    """
    Packs the given pull request information into a JSON object.

    Args:
        id (int): The unique identifier of the pull request.
        connection_token (str): The connection token for authorization.
        title (str): The new title for the pull request.
        from_branch (str): The branch the pull request is coming from.
        into_branch (str): The branch the pull request is going into.

    Returns:
        dict: A JSON object representing the pull request with the following keys:
            - type (str): The type of the request, set to "updatePullRequest".
            - id (int): The unique identifier of the pull request.
            - connectionToken (str): The connection token for authorization.
            - title (str): The new title for the pull request.
            - fromBranch (str): The branch the pull request is coming from.
            - intoBranch (str): The branch the pull request is going into.
    """
    return {
        "type": "updatePullRequest",
        "id": id,
        "connectionToken": connection_token,
        "title": title,
        "fromBranch": from_branch,
        "intoBranch": into_branch,
    }


def pack_create_pull_request(
    repo: str, connection_token: str, title: str, from_branch: str, into_branch: str
):
    """
    Creates a pull request with the specified repository, connection token, title, from branch, and into branch.

    Parameters:
        repo (str): The name of the repository.
        connection_token (str): The connection token for authorization.
        title (str): The title of the pull request.
        from_branch (str): The branch the pull request is coming from.
        into_branch (str): The branch the pull request is going into.

    Returns:
        dict: A JSON object representing the pull request with the following keys:
            - type (str): The type of the request, set to "createPullRequest".
            - repo (str): The name of the repository.
            - connectionToken (str): The connection token for authorization.
            - title (str): The title of the pull request.
            - fromBranch (str): The branch the pull request is coming from.
            - intoBranch (str): The branch the pull request is going into.
    """
    return {
        "type": "createPullRequest",
        "repo": repo,
        "connectionToken": connection_token,
        "title": title,
        "fromBranch": from_branch,
        "intoBranch": into_branch,
    }


def pack_delete_pr(id: int, connection_token: str) -> Json:
    """
    Packs the given pull request ID and connection token into a JSON object with a "type" key set to "deletePullRequest".

    Args:
        id (int): The ID of the pull request to be deleted.
        connection_token (str): The connection token for authorization.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "deletePullRequest".
            - id (int): The ID of the pull request to be deleted.
            - connectionToken (str): The connection token for authorization.
    """
    return {"type": "deletePullRequest", "id": id, "connectionToken": connection_token}


def pack_pull_request_diff(id: int, connection_token: str) -> Json:
    """
    Packs the given pull request ID and connection token into a JSON object with a "type" key set to "prDiff".

    Args:
        id (int): The ID of the pull request.
        connection_token (str): The connection token for authorization.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "prDiff".
            - connectionToken (str): The connection token for authorization.
            - id (int): The ID of the pull request.
    """
    return {"type": "prDiff", "connectionToken": connection_token, "id": id}


def pack_pr_commits(id: int, page: int, connection_token: str) -> Json:
    """
    Packs the given pull request ID, page, and connection token into a JSON object with a "type" key set to "prCommits".

    Args:
        id (int): The ID of the pull request.
        page (int): The page number of the commits.
        connection_token (str): The connection token for authorization.

    Returns:
        Json: A JSON object with the following keys:
            - type (str): The type of the request, set to "prCommits".
            - id (int): The ID of the pull request.
            - page (int): The page number of the commits.
            - connectionToken (str): The connection token for authorization.
    """
    return {
        "type": "prCommits",
        "id": id,
        "page": page,
        "connectionToken": connection_token,
    }


class PullRequest(TypedDict):
    username: str
    title: str
    fromBranch: str
    intoBranch: str
    approved: bool
    id: int
