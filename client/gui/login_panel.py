from typing_extensions import override
import wx
import wx.adv
from base_screen import BaseScreen
from gui.repo_screen import RepoScreen
from gui_run_request import gui_run_request
import hash_password
from main import MainFrame
from token_file import save_token_file
from client_protocol import pack_login
from gitgud_types import Json


class LoginPanel(BaseScreen):
    def __init__(self, parent: MainFrame):
        super().__init__(parent, 1, 3, 1, title="Login")

    @override
    def add_children(self, main_sizer):

        username_label = wx.StaticText(self, label="Username:")
        self.username_text = wx.TextCtrl(self)

        password_label = wx.StaticText(self, label="Password:")
        self.password_text = wx.TextCtrl(
            self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER
        )

        self.password_text.Bind(wx.EVT_TEXT_ENTER, self.on_login)

        login_button = wx.Button(self, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)

        sign_up_button = wx.Button(self, label="Sign Up")
        sign_up_button.Bind(wx.EVT_BUTTON, self.sign_up)

        main_sizer.Add(username_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.username_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)

        main_sizer.Add(password_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.password_text, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(login_button, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(sign_up_button, 0, wx.CENTER | wx.EXPAND)

    def sign_up(self, _):
        from gui.register import RegisterPanel

        self.GetParent().change_screen(lambda: RegisterPanel(self.GetParent()))

    def on_login(self, _):
        username = self.username_text.GetValue()
        password = hash_password.hash(self.password_text.GetValue())

        def on_finished(response: Json):
            token = response["connectionToken"]
            save_token_file(token)
            self.GetParent().change_screen(lambda: RepoScreen(self.GetParent(), token))

        gui_run_request(self, pack_login(username, password), on_finished)
