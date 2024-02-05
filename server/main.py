from server_logic import ServerLogic
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    logic = ServerLogic(30000)
    while True:
        logic.tick()
