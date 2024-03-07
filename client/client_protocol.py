from gitgud_types import Json


def pack_login(username: str, password: str) -> Json:
    return {"type": "login", "username": username, "password": password}


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
