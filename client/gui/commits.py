import wx
import wx.html2
from typing import Callable, List, cast
from gitgud_types import Json
from gui.gui_run_request import gui_run_request

from client_protocol import Commit, pack_commits


class Commits(wx.Panel):
    def __init__(self, parent, repo: str, connection_token: str, branch: str):
        super().__init__(parent)

        self.repo = repo
        self.connection_token = connection_token
        self.branch = branch
        self.page = 0
        self.request_commits()

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        self.commits_list = wx.ListBox(self, choices=[])

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)

        main_sizer.Add(return_button, 0, wx.LEFT)
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

        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 8, wx.CENTER | wx.EXPAND)
        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def change_page(self, page: int):
        self.page = page
        self.page_text.SetLabel(str(page))
        self.request_commits()

    def request_commits(self):
        def on_finished(result: Json):
            commits = cast(List[Commit], result["commits"])
            self.commits_list.Clear()
            self.commits_list.Append(commits_as_str(commits))

        gui_run_request(
            self,
            pack_commits(self.repo, self.connection_token, self.branch, self.page),
            on_finished,
        )


def commits_as_str(commits: List[Commit]) -> List[str]:
    new_line = "\n"
    commit_to_str: Callable[[Commit], str] = (
        lambda commit: f"{commit['authour']}: {commit['message'].replace(new_line, '.')} {new_line}{commit['date']} {commit['hash'][0:6]}"
    )
    return list(map(commit_to_str, commits))
