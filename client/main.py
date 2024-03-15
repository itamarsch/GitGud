import wx
import os
from token_file import read_token_file
from client_comm import ClientComm
from client_protocol import pack_validate_token
from typing import Callable, Optional, TypeVar, cast, List
from dotenv import load_dotenv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from base_screen import BaseScreen
else:
    BaseScreen = TypeVar("BaseScreen")


class MainFrame(wx.Frame):

    def __init__(self, client_com: ClientComm, connection_token: Optional[str]):
        super().__init__(None, title="GitGud")

        self.client_com = client_com

        self.screens: List[BaseScreen] = []

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        if connection_token:
            from gui.repo_screen import RepoScreen

            self.push_screen(lambda: RepoScreen(self, connection_token))
        else:
            from gui.register import RegisterPanel

            self.push_screen(lambda: RegisterPanel(self))
        self.Maximize()

        self.Show()

    def push_screen(self, screen_fn: Callable[[], BaseScreen]):
        if self.screens:
            self.screens[-1].Hide()
            self.sizer.Remove(0)

        from base_screen import BaseScreen

        self.screens.append(cast(BaseScreen, None))
        self.screens[-1] = screen_fn()
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def pop_screen(self):
        self.screens[-1].Hide()
        self.screens.pop()
        self.screens[-1].Show()
        self.screens[-1].on_load()
        self.sizer.Remove(0)
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def change_screen(self, panel: Callable[[], BaseScreen]):
        self.screens[-1].Hide()
        self.screens[-1] = panel()
        self.screens[-1].Show()
        self.sizer.Remove(0)
        self.SetSizer(self.sizer)
        self.Layout()
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)


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
