from typing_extensions import override
import wx
from typing import cast
from base_screen import BaseScreen
from gui.main_screen import MainScreen
from main import MainFrame
from token_file import save_token_file
import hash_password
from gitgud_types import Json
from client_protocol import pack_register

from  import gui_run_request


class RegisterPanel(BaseScreen):
    def __init__(self, parent: MainFrame):

        super().__init__(parent, 1, 3, 1, title="Register")

    @override
    def add_children(self, main_sizer):

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

    def on_register(self, _):
        username = self.username_text.GetValue()
        password = hash_password.hash(self.password_text.GetValue())
        ssh_key = self.sshkey_text.GetValue()

        def on_finished(result: Json):
            token = result["connectionToken"]
            save_token_file(token)
            self.GetParent().change_screen(lambda: MainScreen(self.GetParent(), token))

        gui_run_request(self, pack_register(username, password, ssh_key), on_finished)

    def on_login(self, _):
        from gui.login_panel import LoginPanel

        self.GetParent().change_screen(lambda: LoginPanel(self.GetParent()))
