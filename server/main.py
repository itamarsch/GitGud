import os
from typing import cast
from server_logic import ServerLogic
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    logic = ServerLogic(int(cast(str, os.getenv("SERVER_PORT"))))
    while True:
        logic.tick()
