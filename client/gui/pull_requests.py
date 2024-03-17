from typing_extensions import override
import wx
import wx.html2
from typing import Callable, List, cast
from base_screen import BaseScreen
from gitgud_types import Json
from gui.pr_editor import PullRequestEditor
from gui_run_request import gui_run_request

from client_protocol import (
    PullRequest,
    pack_delete_pr,
    pack_view_prs,
)
from main import MainFrame


class PullRequests(BaseScreen):
    def __init__(self, parent: MainFrame, repo: str, connection_token: str):
        self.repo = repo
        self.connection_token = connection_token

        self.prs: List[PullRequest] = []
        super().__init__(parent, 1, 1, title="Pull Requests")

    @override
    def on_load(self):
        self.request_prs()

    @override
    def add_children(self, main_sizer):
        self.pr_list = wx.ListBox(self, choices=[])
        self.pr_list.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.request_prs()
        create_pr = wx.Button(self, label="Create pr")
        create_pr.Bind(
            wx.EVT_BUTTON,
            lambda _: self.GetParent().push_screen(
                lambda: PullRequestEditor(
                    self.GetParent(), None, self.connection_token, self.repo
                )
            ),
        )
        main_sizer.Add(create_pr, 0, wx.RIGHT)

        main_sizer.Add(self.pr_list, 15, wx.CENTER | wx.EXPAND)

    def on_right_click(self, event):
        # Get the index of the item right-clicked
        index = self.pr_list.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.pr_list.Select(index)
            self.create_popup_menu(event)

    def create_popup_menu(self, _):
        menu = wx.Menu()
        delete = menu.Append(wx.ID_ANY, "Delete")
        view = menu.Append(wx.ID_ANY, "View")
        edit = menu.Append(wx.ID_ANY, "Edit")
        self.Bind(wx.EVT_MENU, self.on_deleted, delete)
        self.Bind(wx.EVT_MENU, self.on_issue_view, view)
        self.Bind(wx.EVT_MENU, self.on_pr_edit, edit)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_deleted(self, _):
        pr_index: int = self.pr_list.GetSelection()
        pr_id = self.prs[pr_index]["id"]

        def on_finished(_: Json):
            self.request_prs()

        gui_run_request(self, pack_delete_pr(pr_id, self.connection_token), on_finished)

    def on_issue_view(self, _):
        pr_index: int = self.pr_list.GetSelection()
        pr = self.prs[pr_index]

        # self.GetParent().push_screen(lambda: IssueViewer(self.GetParent(), pr))

    def on_pr_edit(self, _):
        pr_index: int = self.pr_list.GetSelection()
        pr = self.prs[pr_index]

        self.GetParent().push_screen(
            lambda: PullRequestEditor(
                self.GetParent(), pr, self.connection_token, self.repo
            )
        )

    def request_prs(self):
        def on_finished(result: Json):
            pull_requests = cast(List[PullRequest], result["pullRequests"])
            self.prs = pull_requests
            self.pr_list.Clear()
            self.pr_list.Append(pr_as_str(pull_requests))

        gui_run_request(
            self,
            pack_view_prs(self.repo, self.connection_token),
            on_finished,
        )


def pr_as_str(prs: List[PullRequest]) -> List[str]:
    pr_as_str: Callable[[PullRequest], str] = (
        lambda pr: f"{pr['title']}\n{pr['username']}\n{pr['fromBranch']} -> {pr['intoBranch']}"
    )
    return list(map(pr_as_str, prs))
