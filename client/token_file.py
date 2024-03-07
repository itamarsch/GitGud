import os
from typing import Optional

token_file_name = ".token_cookie"


def read_token_file() -> Optional[str]:
    if os.path.exists(token_file_name):
        with open(token_file_name, "r") as f:
            return f.read()
    return None


def save_token_file(token: str):
    with open(token_file_name, "w") as f:
        f.write(token)
