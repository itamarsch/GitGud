import os
from typing import Optional

token_file_name = ".token_cookie"


def read_token_file() -> Optional[str]:
    """
    Reads the token file and returns its contents as a string, or returns None if the file does not exist.
    """
    if os.path.exists(token_file_name):
        with open(token_file_name, "r") as f:
            return f.read()
    return None


def save_token_file(token: str):
    """
    Saves the token to a file.

    Parameters:
        token (str): The token to be saved to the file.
    """
    with open(token_file_name, "w") as f:
        f.write(token)
