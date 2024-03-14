import wx
from client_protocol import pack_create_repo
from gitgud_types import Json

from gui.gui_run_request import gui_request_file, gui_run_request
from gui.repo_screen import RepoScreen


class RepoCreate(wx.Panel):
    def __init__(self, parent, connection_token: str):
        super().__init__(parent)
        self.connection_token = connection_token

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)

        # Text Field for Repository Name
        repo_name_label = wx.StaticText(self, label="Repository Name:")
        main_sizer.Add(repo_name_label, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.repo_name_text = wx.TextCtrl(self)
        main_sizer.Add(self.repo_name_text, flag=wx.EXPAND | wx.ALL, border=5)

        # Toggle Button for "Is Public"
        self.public_checkbox = wx.CheckBox(self, label="Public")
        main_sizer.Add(self.public_checkbox, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # Create Button
        create_button = wx.Button(self, label="Create")
        create_button.Bind(wx.EVT_BUTTON, self.on_create)
        main_sizer.Add(
            create_button, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, border=10
        )

        # Return Button
        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())
        main_sizer.Add(
            return_button, flag=wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, border=10
        )

        main_sizer.AddStretchSpacer(3)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 1, wx.CENTER | wx.EXPAND)
        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def on_create(self, event):
        repo_name = self.repo_name_text.GetValue()
        public = self.public_checkbox.GetValue()

        def on_finished(result: Json):
            full_repo_name = result["fullRepoName"]
            self.GetParent().push_screen(
                RepoScreen(self.GetParent(), self.connection_token, full_repo_name)
            )

        gui_run_request(
            self,
            pack_create_repo(repo_name, public, self.connection_token),
            on_finished,
        )
