from typing_extensions import override
import wx
import wx.adv
from base_screen import BaseScreen
from gui.repo_screen import RepoScreen
from gui_run_request import gui_run_request
import hash_password
from main_frame import MainFrame
from token_file import save_token_file
from client_protocol import pack_login
from gitgud_types import Json


class LoginPanel(BaseScreen):
    def __init__(self, parent: MainFrame):
        """
        Initializes a new instance of the LoginPanel class.

        Args:
            parent (MainFrame): The parent frame of the login panel.

        Returns:
            None
        """
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
        """
        Switches the current screen to the register panel.

        This function is called when the user clicks the "Sign Up" button in the login panel.
        It imports the RegisterPanel class from the gui.register module and creates an instance of it
        with the parent frame of the login panel. Then, it calls the change_screen method of the parent
        frame to switch to the register panel.

        Parameters:
            _: This parameter is not used in the function.

        Returns:
            None
        """
        from gui.register import RegisterPanel

        self.GetParent().change_screen(lambda: RegisterPanel(self.GetParent()))

    def on_login(self, _):
        """
        A callback function called when the login button is pressed.
        It extracts the username and hashed password from the UI elements.
        Makes a GUI request with the login data
        Defines an inner function to handle the response and save the token to a file.
        """
        username = self.username_text.GetValue()
        password = hash_password.hash(self.password_text.GetValue())

        def on_finished(response: Json):
            """
            A callback function called when the login request is finished.

            Parameters:
                response (Json): The response from the login request.

            Returns:
                None
            """
            token = response["connectionToken"]
            save_token_file(token)
            self.GetParent().change_screen(lambda: RepoScreen(self.GetParent(), token))

        gui_run_request(self, pack_login(username, password), on_finished)
