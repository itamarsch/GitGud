from typing_extensions import override
import wx
from base_screen import BaseScreen
from client_protocol import pack_create_repo
from gitgud_types import Json

from gui_run_request import gui_run_request
from gui.repo_screen import RepoScreen
from main import MainFrame


class RepoCreate(BaseScreen):
    def __init__(self, parent: MainFrame, connection_token: str):
        self.connection_token = connection_token
        super().__init__(parent, 1, 3, 1, title="Create Repo")

    @override
    def add_children(self, main_sizer: wx.BoxSizer):

        repo_name_label = wx.StaticText(self, label="Repository Name:")
        main_sizer.Add(repo_name_label, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.repo_name_text = wx.TextCtrl(self)
        main_sizer.Add(self.repo_name_text, flag=wx.EXPAND | wx.ALL, border=5)

        self.public_checkbox = wx.CheckBox(self, label="Public")
        main_sizer.Add(self.public_checkbox, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        create_button = wx.Button(self, label="Create")
        create_button.Bind(wx.EVT_BUTTON, self.on_create)
        main_sizer.Add(
            create_button, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, border=10
        )

    def on_create(self, _):
        repo_name = self.repo_name_text.GetValue()
        public = self.public_checkbox.GetValue()

        def on_finished(result: Json):
            full_repo_name = result["fullRepoName"]
            self.GetParent().push_screen(
                lambda: RepoScreen(
                    self.GetParent(), self.connection_token, full_repo_name
                )
            )

        gui_run_request(
            self,
            pack_create_repo(repo_name, public, self.connection_token),
            on_finished,
        )
