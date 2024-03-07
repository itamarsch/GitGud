import json
import wx
import wx.adv
from typing import cast
from gui.repo_screen import RepoScren
from main import MainFrame
from client_protocol import pack_login
from gitgud_types import Json

from gui.gui_run_request import gui_run_request


class LoginPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        # Username
        username_label = wx.StaticText(self, label="Username:")
        self.username_text = wx.TextCtrl(self)

        # Password
        password_label = wx.StaticText(self, label="Password:")
        self.password_text = wx.TextCtrl(self, style=wx.TE_PASSWORD)

        # Register Button
        login_button = wx.Button(self, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)

        sign_up_button = wx.Button(self, label="Sign Up")
        sign_up_button.Bind(wx.EVT_BUTTON, self.sign_up)

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(username_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.username_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)

        main_sizer.Add(password_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.password_text, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(login_button, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(sign_up_button, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddStretchSpacer(3)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 1, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def sign_up(self, event):
        from gui.register import RegisterPanel

        self.Parent.change_screen(RegisterPanel(self.GetParent()))

    def on_login(self, event):
        username = self.username_text.GetValue()
        password = self.password_text.GetValue()

        def on_finished(response: Json):
            if "connectionToken" in response:
                cast(MainFrame, self.GetParent()).change_screen(
                    RepoScren(self.GetParent(), response["connectionToken"])
                )
            elif "error" in response:
                wx.MessageBox(response["error"])

        gui_run_request(self, pack_login(username, password), on_finished)

        pass