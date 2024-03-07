import wx
import hashlib
from typing import cast
import hash_password
from gitgud_types import Json
from client_protocol import pack_register

from gui.gui_run_request import gui_run_request


class RegisterPanel(wx.Panel):
    def __init__(self, parent):

        super().__init__(parent)

        # Username
        username_label = wx.StaticText(self, label="Username:")
        self.username_text = wx.TextCtrl(self)

        # Password
        password_label = wx.StaticText(self, label="Password:")
        self.password_text = wx.TextCtrl(self, style=wx.TE_PASSWORD)

        # SSH Key
        sshkey_label = wx.StaticText(self, label="SSH Key:")
        self.sshkey_text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        num_lines = 5
        font: wx.Font = cast(wx.Font, self.sshkey_text.GetFont())
        font_height: int = cast(wx.Size, font.GetPixelSize()).height
        initial_size = (-1, font_height * num_lines)
        self.sshkey_text.SetInitialSize(cast(wx.Size, initial_size))

        # Register Button
        register_button = wx.Button(self, label="Register")
        register_button.Bind(wx.EVT_BUTTON, self.on_register)

        # Register Button
        login_button = wx.Button(self, label="Already have an account")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)
        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(username_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.username_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(password_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.password_text, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(sshkey_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.sshkey_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(register_button, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(login_button, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddStretchSpacer(3)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 1, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def on_register(self, event):
        username = self.username_text.GetValue()
        password = hash_password.hash(self.password_text.GetValue())
        ssh_key = self.sshkey_text.GetValue()

        def on_finished(result: Json):
            pass

        gui_run_request(self, pack_register(username, password, ssh_key), on_finished)

    def on_login(self, event):
        from gui.login_panel import LoginPanel

        self.Parent.change_screen(LoginPanel(self.GetParent()))
