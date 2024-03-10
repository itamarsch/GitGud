import wx
import wx.html2
from typing import Callable, List, cast
from gui.issue import IssueViewer
from gitgud_types import Json
from gui.gui_run_request import gui_run_request

from client_protocol import Issue, pack_delete_issue, pack_view_issues


class Issues(wx.Panel):
    def __init__(self, parent, repo: str, connection_token: str):
        super().__init__(parent)
        self.repo = repo
        self.connection_token = connection_token
        self.request_issues()

        self.issues: List[Issue] = []

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        self.issues_list = wx.ListBox(self, choices=[])
        self.issues_list.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)

        main_sizer.Add(return_button, 0, wx.LEFT)
        main_sizer.Add(self.issues_list, 15, wx.CENTER | wx.EXPAND)

        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 8, wx.CENTER | wx.EXPAND)
        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def on_right_click(self, event):
        # Get the index of the item right-clicked
        index = self.issues_list.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.issues_list.Select(index)
            self.create_popup_menu(event)

    def create_popup_menu(self, event):
        menu = wx.Menu()
        delete = menu.Append(wx.ID_ANY, "Delete")
        view = menu.Append(wx.ID_ANY, "View")
        self.Bind(wx.EVT_MENU, self.on_deleted, delete)
        self.Bind(wx.EVT_MENU, self.on_issue_view, view)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_deleted(self, event):
        issue_index = self.issues_list.GetSelection()
        issue_id = cast(Issue, self.issues[issue_index])["id"]

        def on_finished(_: Json):
            self.request_issues()

        gui_run_request(
            self, pack_delete_issue(issue_id, self.connection_token), on_finished
        )

    def on_issue_view(self, event):
        issue_index = self.issues_list.GetSelection()
        issue = cast(Issue, self.issues[issue_index])

        self.GetParent().push_screen(IssueViewer(self.GetParent(), issue))

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
