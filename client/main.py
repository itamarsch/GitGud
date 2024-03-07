import wx
import os
from client_comm import ClientComm
from typing import Optional, cast
from dotenv import load_dotenv
from gui.register import RegisterPanel


class MainFrame(wx.Frame):

    def __init__(self, client_com: ClientComm):
        super().__init__(None, title="GitGud")

        self.client_com = client_com
        self.screens = []
        self.connection_token: Optional[str] = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.change_screen(RegisterPanel(self))
        self.Maximize()

        self.Show()

    def push_screen(self, screen):
        if self.screens:
            self.screens[-1].Hide()
            self.sizer.Remove(0)
        self.screens.append(screen)
        self.sizer.Add(screen, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def pop_screen(self):
        self.screens[-1].Hide()
        self.screens.pop()
        self.screens[-1].Show()
        self.sizer.Remove(0)
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def change_screen(self, panel):
        self.push_screen(panel)
        if len(self.screens) > 1:
            del self.screens[-2]


if __name__ == "__main__":
    load_dotenv()

    port = int(cast(str, os.getenv("SERVER_PORT")))
    ip = cast(str, os.getenv("SERVER_IP"))

    client_com = ClientComm((ip, port))

    app = wx.App(False)

    main_frame = MainFrame(client_com)
    app.MainLoop()
