import wx
import os
from client_comm import ClientComm
from typing import cast
from dotenv import load_dotenv
from gui.register import RegisterPanel


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="GitGud")
        port = int(cast(str, os.getenv("SERVER_PORT")))
        ip = cast(str, os.getenv("SERVER_IP"))
        addr = (ip, port)

        self.client_com = ClientComm(addr)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.current_panel = None

        self.change_screen(RegisterPanel(self))

        self.Show()

    def change_screen(self, panel):
        if self.current_panel:
            self.current_panel.Hide()
            self.sizer.Remove(0)

        self.current_panel = panel
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()


if __name__ == "__main__":
    load_dotenv()
    app = wx.App(False)

    main_frame = MainFrame()
    app.MainLoop()
