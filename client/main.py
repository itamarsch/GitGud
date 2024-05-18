import wx
import os
from main_frame import MainFrame
from token_file import read_token_file
from client_comm import ClientComm
from client_protocol import pack_validate_token
from typing import cast
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    port = int(cast(str, os.getenv("SERVER_PORT")))
    ip = cast(str, os.getenv("SERVER_IP"))

    client_com = ClientComm((ip, port))

    app = wx.App(False)

    token = read_token_file()

    valid_token: bool = False
    if token:
        result = client_com.run_request(pack_validate_token(token))
        if result["valid"]:
            valid_token = True

    MainFrame(client_com, token if valid_token else None)
    app.MainLoop()
