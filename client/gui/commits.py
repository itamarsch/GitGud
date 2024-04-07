from typing_extensions import override
import wx
import wx.html2
from typing import Callable, List, cast
from base_screen import BaseScreen
from gui.diff import Diff
from gitgud_types import Json
from gui_run_request import gui_request_file, gui_run_request

from client_protocol import Commit, pack_diff
from main import MainFrame


class Commits(BaseScreen):
    def __init__(
        self,
        parent: MainFrame,
        connection_token: str,
        pack_commit_request: Callable[[int], Json],
        repo: str,
    ):
        self.repo = repo
        self.connection_token = connection_token
        self.pack_request = pack_commit_request
        self.page = 0
        self.commits: List[Commit] = []
        super().__init__(parent, 1, 1, title="Commits")

    @override
    def add_children(self, main_sizer):

        self.commits_list = wx.ListBox(self, choices=[])
        self.commits_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_commit_select)

        self.request_commits()
        main_sizer.Add(self.commits_list, 15, wx.CENTER | wx.EXPAND)

        pages_buttons = wx.BoxSizer(wx.HORIZONTAL)

        previous_button = wx.Button(self, label="<<")
        previous_button.Bind(
            wx.EVT_BUTTON, lambda _: self.change_page(max(0, self.page - 1))
        )
        self.page_text = wx.StaticText(self, label=str(self.page))
        next_button = wx.Button(self, label=">>")
        next_button.Bind(wx.EVT_BUTTON, lambda _: self.change_page(self.page + 1))

        pages_buttons.AddStretchSpacer(3)
        pages_buttons.Add(previous_button, 2, wx.EXPAND)
        pages_buttons.AddStretchSpacer(1)
        pages_buttons.Add(self.page_text, 0, wx.ALIGN_CENTER_VERTICAL)
        pages_buttons.AddStretchSpacer(1)
        pages_buttons.Add(next_button, 2, wx.EXPAND)
        pages_buttons.AddStretchSpacer(3)

        main_sizer.Add(pages_buttons, 1, wx.CENTER | wx.EXPAND)

    def change_page(self, page: int):
        """
        Request commits of new page and change the page number displayed on the page_text label to the given page. 
        
        Parameters:
            page (int): The new page number to be displayed.  
        """
        self.page = page
        self.page_text.SetLabel(str(page))
        self.request_commits()

    def on_commit_select(self, _):

        index = self.commits_list.GetSelection()

        commit = cast(Commit, self.commits[index])

        def on_finished(diff: bytes):
            self.GetParent().push_screen(lambda: Diff(self.GetParent(), diff.decode()))

        gui_request_file(
            self,
            pack_diff(self.repo, self.connection_token, commit["hash"]),
            on_finished,
        )

    def request_commits(self):
        def on_finished(result: Json):
            commits = cast(List[Commit], result["commits"])
            self.commits = commits
            self.commits_list.Clear()
            self.commits_list.Append(commits_as_str(commits))

        gui_run_request(
            self,
            self.pack_request(self.page),
            on_finished,
        )


def commits_as_str(commits: List[Commit]) -> List[str]:
    new_line = "\n"
    commit_to_str: Callable[[Commit], str] = (
        lambda commit: f"{commit['authour']}: {commit['message'].replace(new_line, '.')} {new_line}{commit['date']} {commit['hash'][0:6]}"
    )
    return list(map(commit_to_str, commits))
