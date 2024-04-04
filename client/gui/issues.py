from typing_extensions import override
import wx
import wx.html2
from typing import Callable, List, cast
from base_screen import BaseScreen
from gui.issue import IssueViewer
from gitgud_types import Json
from gui.issue_editor import IssueEditor
from gui_run_request import gui_run_request

from client_protocol import Issue, pack_delete_issue, pack_view_issues
from main import MainFrame


class Issues(BaseScreen):
    def __init__(self, parent: MainFrame, repo: str, connection_token: str):
        self.repo = repo
        self.connection_token = connection_token

        self.issues: List[Issue] = []
        super().__init__(parent, 1, 1, title="Issues")

    @override
    def on_load(self):
        self.request_issues()

    @override
    def add_children(self, main_sizer):
        self.issues_list = wx.ListBox(self, choices=[])
        self.issues_list.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.request_issues()
        create_issue = wx.Button(self, label="Create issue")
        create_issue.Bind(
            wx.EVT_BUTTON,
            lambda _: self.GetParent().push_screen(
                lambda: IssueEditor(
                    self.GetParent(), None, self.connection_token, self.repo
                )
            ),
        )
        main_sizer.Add(create_issue, 0, wx.RIGHT)

        main_sizer.Add(self.issues_list, 15, wx.CENTER | wx.EXPAND)

    def on_right_click(self, event):
        # Get the index of the item right-clicked
        index = self.issues_list.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.issues_list.Select(index)
            self.create_popup_menu(event)

    def create_popup_menu(self, _):
        menu = wx.Menu()
        delete = menu.Append(wx.ID_ANY, "Delete")
        view = menu.Append(wx.ID_ANY, "View")
        edit = menu.Append(wx.ID_ANY, "Edit")
        self.Bind(wx.EVT_MENU, self.on_deleted, delete)
        self.Bind(wx.EVT_MENU, self.on_issue_view, view)
        self.Bind(wx.EVT_MENU, self.on_issue_edit, edit)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_deleted(self, _):
        issue_index = self.issues_list.GetSelection()
        issue_id = cast(Issue, self.issues[issue_index])["id"]

        def on_finished(_: Json):
            self.request_issues()

        gui_run_request(
            self, pack_delete_issue(issue_id, self.connection_token), on_finished
        )

    def on_issue_view(self, _):
        issue_index = self.issues_list.GetSelection()
        issue = cast(Issue, self.issues[issue_index])

        self.GetParent().push_screen(lambda: IssueViewer(self.GetParent(), issue))

    def on_issue_edit(self, _):
        issue_index = self.issues_list.GetSelection()
        issue = cast(Issue, self.issues[issue_index])

        self.GetParent().push_screen(
            lambda: IssueEditor(
                self.GetParent(), issue, self.connection_token, self.repo
            )
        )

    def request_issues(self):
        def on_finished(result: Json):
            issues = cast(List[Issue], result["issues"])
            self.issues = issues
            self.issues_list.Clear()
            self.issues_list.Append(issue_as_str(issues))

        gui_run_request(
            self,
            pack_view_issues(self.repo, self.connection_token),
            on_finished,
        )


def issue_as_str(issues: List[Issue]) -> List[str]:
    issue_as_str: Callable[[Issue], str] = (
        lambda issue: f"{issue['title']}\n{issue['username']}"
    )
    return list(map(issue_as_str, issues))
