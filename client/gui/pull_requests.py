from typing_extensions import override
import wx
import wx.html2
from typing import Callable, List, cast
from base_screen import BaseScreen
from gitgud_types import Json
from gui.commits import Commits
from gui.diff import Diff
from gui.pr_editor import PullRequestEditor
from gui_run_request import gui_request_file, gui_run_request

from client_protocol import (
    PullRequest,
    pack_delete_pr,
    pack_pr_commits,
    pack_view_prs,
    pack_pull_request_diff,
)
from main import MainFrame


class PullRequests(BaseScreen):
    def __init__(self, parent: MainFrame, repo: str, connection_token: str):
        """
        Initializes a new instance of the PullRequests class.

        Args:
            parent (MainFrame): The parent frame of the PullRequests.
            repo (str): The repository name.
            connection_token (str): The connection token for the PullRequests.

        Initializes the PullRequests with the given parent frame, repository name, and connection token.
        Sets the prs attribute to an empty list.
        Calls the parent class's __init__ method with the provided parameters.
        """
        self.repo = repo
        self.connection_token = connection_token

        self.prs: List[PullRequest] = []
        super().__init__(parent, 1, 1, title="Pull Requests")

    @override
    def on_reload(self):
        """
        Request pr on reload of screen because prs may have been deleted or edited
        """
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
        """
        Handles the right-click event on the list.

        Args:
            event (wx.MouseEvent): The right-click event.

        Returns:
            None
        """
        # Get the index of the item right-clicked
        index = self.pr_list.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.pr_list.Select(index)
            self.create_popup_menu(event)

    def create_popup_menu(self, _):
        """
        Create a popup menu with options to Delete, Diff, Commits, and Edit.
        Bind event handlers for each menu option.
        Display the menu and destroy it after it's used.
        """
        menu = wx.Menu()
        delete = menu.Append(wx.ID_ANY, "Delete")
        diff = menu.Append(wx.ID_ANY, "Diff")
        commits = menu.Append(wx.ID_ANY, "Commits")
        edit = menu.Append(wx.ID_ANY, "Edit")
        self.Bind(wx.EVT_MENU, self.on_pr_deleted, delete)
        self.Bind(wx.EVT_MENU, self.on_pr_diff, diff)
        self.Bind(wx.EVT_MENU, self.on_pr_edit, edit)
        self.Bind(wx.EVT_MENU, self.on_pr_commits_request, commits)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_pr_commits_request(self, _):
        """
        A function that handles the request for PR commits. Retrieves the PR index from the selection,
        extracts the PR ID, and pushes the Commits screen to display commits related to the selected PR.
        """
        pr_index: int = self.pr_list.GetSelection()
        pr_id = self.prs[pr_index]["id"]
        self.GetParent().push_screen(
            lambda: Commits(
                self.GetParent(),
                self.connection_token,
                lambda page: pack_pr_commits(pr_id, page, self.connection_token),
                self.repo,
            )
        )

    def on_pr_deleted(self, _):
        """
        A callback function to handle pull request deletion.
        """
        pr_index: int = self.pr_list.GetSelection()
        pr_id = self.prs[pr_index]["id"]

        def on_finished(_: Json):
            self.request_prs()

        gui_run_request(self, pack_delete_pr(pr_id, self.connection_token), on_finished)

    def on_pr_diff(self, _):
        """
        A function that handles the PR diff request by retrieving the selected PR, fetching the diff, and displaying it.
        """
        pr_index: int = self.pr_list.GetSelection()
        pr = self.prs[pr_index]

        def on_finished(diff: bytes):
            self.GetParent().push_screen(lambda: Diff(self.GetParent(), diff))

        gui_request_file(
            self, pack_pull_request_diff(pr["id"], self.connection_token), on_finished
        )

    def on_pr_edit(self, _):
        """
        A function to handle the event of editing a pull request.
        It retrieves the selected pull request from the list, and then it pushes a PullRequestEditor screen.
        """
        pr_index: int = self.pr_list.GetSelection()
        pr = self.prs[pr_index]

        self.GetParent().push_screen(
            lambda: PullRequestEditor(
                self.GetParent(), pr, self.connection_token, self.repo
            )
        )

    def request_prs(self):
        """
        A function that requests pull requests and updates the PR list.
        """

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
    """
    Convert a list of PullRequest objects into a list of strings.

    Args:
        prs (List[PullRequest]): A list of PullRequest objects.

    Returns:
        List[str]: A list of strings representing the PullRequest objects. Each string contains the title, username, and branch information of a PullRequest object.

    """
    pr_as_str: Callable[[PullRequest], str] = (
        lambda pr: f"{pr['title']}\n{pr['username']}\n{pr['fromBranch']} -> {pr['intoBranch']}"
    )
    return list(map(pr_as_str, prs))
