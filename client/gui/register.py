from typing_extensions import override
import wx
from typing import cast
from base_screen import BaseScreen
from gui.repo_screen import RepoScreen
from gui.ssh_help import SSHHelp
from main import MainFrame
from token_file import save_token_file
import hash_password
from gitgud_types import Json
from client_protocol import pack_register

from gui_run_request import gui_run_request


class RegisterPanel(BaseScreen):
    def __init__(self, parent: MainFrame):
        """
        Initializes a new instance of the RegisterPanel class.

        Args:
            parent (MainFrame): The parent frame of the RegisterPanel.

        Initializes the RegisterPanel with the given parent frame.
        Calls the parent class's __init__ method with the provided parameters.

        """

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

        ssh_help_button = wx.Button(self, label="SSH Help")
        ssh_help_button.Bind(wx.EVT_BUTTON, self.on_ssh_help)

        sshkey_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sshkey_sizer.Add(sshkey_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sshkey_sizer.Add(ssh_help_button, 0)
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

        main_sizer.Add(sshkey_sizer, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.sshkey_text, 0, wx.CENTER | wx.EXPAND)

        main_sizer.AddSpacer(5)
        main_sizer.Add(register_button, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(login_button, 0, wx.CENTER | wx.EXPAND)

    def on_ssh_help(self, _):
        """
        Callback function to handle the registration process. Retrieves user input, sends a registration request,
        and processes the result to obtain a connection token for further interaction with the application.

        Parameters:
            _ (Any): Unused parameter.

        Returns:
            None
        """
        self.GetParent().push_screen(lambda: SSHHelp(self.GetParent()))

    def on_register(self, _):
        """
        A callback function to handle the registration process. Retrieves user input, sends a registration request,
        and processes the result to obtain a connection token for further interaction with the application.
        """
        username = self.username_text.GetValue()
        password = hash_password.hash(self.password_text.GetValue())
        ssh_key = self.sshkey_text.GetValue()

        def on_finished(result: Json):
            token = result["connectionToken"]
            save_token_file(token)
            self.GetParent().change_screen(lambda: RepoScreen(self.GetParent(), token))

        gui_run_request(self, pack_register(username, password, ssh_key), on_finished)

    def on_login(self, _):
        """
        Switches the current screen to the login panel.

        This function is called when the user clicks the "Login" button in the register panel.
        It imports the LoginPanel class from the gui.login_panel module and creates an instance of it
        with the parent frame of the register panel. Then, it calls the change_screen method of the parent
        frame to switch to the login panel.

        Parameters:
            _ (Any): This parameter is not used in the function.

        Returns:
            None
        """
        from gui.login_panel import LoginPanel

        self.GetParent().change_screen(lambda: LoginPanel(self.GetParent()))
