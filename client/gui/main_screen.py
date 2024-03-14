from typing import List
from typing_extensions import override
import wx
from base_screen import BaseScreen
from gui.repo_create import RepoCreate
from gui.repo_screen import RepoScreen
from client_protocol import pack_search_repo
from gitgud_types import Json

from gui.gui_run_request import gui_run_request


class MainScreen(BaseScreen):
    def __init__(self, parent, connection_token: str):
        self.connection_token = connection_token
        super().__init__(parent, 0, 5)

    @override
    def add_children(self, main_sizer):

        title = wx.StaticText(self, label="GitGud")
        title_font = wx.Font(
            40, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        title.SetFont(title_font)

        self.search_box = wx.TextCtrl(self)
        self.search_box.Bind(wx.EVT_TEXT, self.on_text_changed)
        self.search_box.SetHint("Search Repo")

        self.repo_list_box = wx.ListBox(self, style=wx.LB_NO_SB)
        self.repo_list_box.Bind(wx.EVT_LISTBOX_DCLICK, self.on_search_result_selected)

        repo_create_button = wx.Button(self, label="Create repo")
        repo_create_button.Bind(
            wx.EVT_BUTTON,
            lambda _: self.GetParent().push_screen(
                RepoCreate(self.GetParent(), self.connection_token)
            ),
        )

        main_sizer.Add(title, 1, wx.CENTER)
        main_sizer.Add(repo_create_button, 0, wx.LEFT)
        main_sizer.Add(self.search_box, 0, wx.EXPAND)
        main_sizer.Add(self.repo_list_box, 0, wx.EXPAND)

    def on_search_result_selected(self, _):

        selection = self.repo_list_box.GetSelection()
        if selection != wx.NOT_FOUND:
            repo = self.repo_list_box.GetString(selection)
            self.GetParent().push_screen(
                RepoScreen(self.GetParent(), self.connection_token, repo=repo)
            )

    def on_text_changed(self, event):
        query = event.GetEventObject().GetValue()
        if query:

            def on_finished(result: Json):
                options = result["repos"]

                self.update_list(options)

            gui_run_request(self, pack_search_repo(query), on_finished)
        else:
            self.hide_list()

    def update_list(self, options):
        self.repo_list_box.Clear()
        self.repo_list_box.SetItems(options)
        self.show_list(options)

    def show_list(self, options: List[str]):
        total_height = min(len(options) + 1, 5) * (self.repo_list_box.GetCharHeight())
        self.repo_list_box.SetSize((-1, total_height))
        self.repo_list_box.Show()

    def hide_list(self):
        self.repo_list_box.Hide()
