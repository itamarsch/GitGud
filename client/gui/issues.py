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
        """
        Initializes a new instance of the Issues class.

        Args:
            parent (MainFrame): The parent frame of the Issues.
            repo (str): The repository name.
            connection_token (str): The connection token for the Issues.

        Initializes the Issues with the given parent frame, repository name, and connection token.
        Sets the issues attribute to an empty list.
        Calls the parent class's __init__ method with the provided parameters.

        """
        self.repo = repo
        self.connection_token = connection_token

        self.issues: List[Issue] = []
        super().__init__(parent, 1, 1, title="Issues")

    @override
    def on_reload(self):
        """
        Request issues on reload of screen because prs may have been deleted or edited
        """
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
        """
        Handle the right-click event on the issues list.

        Args:
            event (wx.MouseEvent): The right-click event.

        Returns:
            None
        """
        # Get the index of the item right-clicked
        index = self.issues_list.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.issues_list.Select(index)
            self.create_popup_menu(event)

    def create_popup_menu(self, _):
        """
        Create a popup menu with options for Delete, View, and Edit. 
        Bind event handlers for each option to corresponding methods. 
        Display the menu and destroy it after it's used.
        """
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
        """
        A function that handles when an item is deleted. 
        It retrieves the index of the selected issue, gets the corresponding issue ID. It then initiates the deletion request and calls the function to request updated issues.
        """
        issue_index = self.issues_list.GetSelection()
        issue_id = cast(Issue, self.issues[issue_index])["id"]

        def on_finished(_: Json):
            self.request_issues()

        gui_run_request(
            self, pack_delete_issue(issue_id, self.connection_token), on_finished
        )

    def on_issue_view(self, _):
        """
        A function that handles the action when an issue is viewed. 
        It retrieves the selected issue from a list, then pushes a screen to view the selected issue.
        """
        issue_index = self.issues_list.GetSelection()
        issue = cast(Issue, self.issues[issue_index])

        self.GetParent().push_screen(lambda: IssueViewer(self.GetParent(), issue))

    def on_issue_edit(self, _):
        """
        Retrieves the index of the selected issue from the issues_list,
        Retrieves the selected issue from the issues list using the obtained index.
        Pushes the IssueEditor screen
        """
        issue_index = self.issues_list.GetSelection()
        issue = cast(Issue, self.issues[issue_index])

        self.GetParent().push_screen(
            lambda: IssueEditor(
                self.GetParent(), issue, self.connection_token, self.repo
            )
        )

    def request_issues(self):
        """
        Generate a request for issues and update the GUI with the retrieved information.
        """
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
    """
    Convert a list of issues into a list of strings representing each issue's title and username.

    Args:
        issues (List[Issue]): A list of issues.

    Returns:
        List[str]: A list of strings representing each issue's title and username.
    """
    issue_as_str: Callable[[Issue], str] = (
        lambda issue: f"{issue['title']}\n{issue['username']}"
    )
    return list(map(issue_as_str, issues))
