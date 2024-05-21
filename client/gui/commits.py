from typing_extensions import override
import wx
import wx.html2
from typing import Callable, List, cast
from base_screen import BaseScreen
from gui.diff import Diff
from gitgud_types import Json
from gui_run_request import gui_request_file
import json

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
        """
        Initializes a new instance of the Commits class.

        Args:
            parent (MainFrame): The parent frame of the Commits.
            connection_token (str): The connection token for the Commits.
            pack_commit_request (Callable[[int], Json]): A callable that takes an integer page number and returns a Json object representing a commit request.
            repo (str): The name of the repository.

        Returns:
            None
        """
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
        """
        Handles the event when a commit is selected.

        This function is called when a commit is selected in the commits list. It retrieves the selected commit and
        opens a new screen to display the diff of the selected commit.

        Parameters:
            _ (Any): Unused parameter.

        Returns:
            None
        """
        index = self.commits_list.GetSelection()

        commit = cast(Commit, self.commits[index])

        def on_finished(diff: bytes):
            self.GetParent().push_screen(lambda: Diff(self.GetParent(), diff))

        gui_request_file(
            self,
            pack_diff(self.repo, self.connection_token, commit["hash"]),
            on_finished,
        )

    def request_commits(self):
        """
        Requests commits from the server and updates the list of commits on the GUI.

        This function sends a request to the server to retrieve the specific page of commits from a given repository branch.

        Parameters:
            self (Commits): The instance of the `Commits` class.

        Returns:
            None
        """
        def on_finished(result: bytes):

            commits = cast(List[Commit], json.loads(result)["commits"])
            self.commits = commits
            self.commits_list.Clear()
            self.commits_list.Append(commits_as_str(commits))

        gui_request_file(
            self,
            self.pack_request(self.page),
            on_finished,
        )


def commits_as_str(commits: List[Commit]) -> List[str]:
    """
    Convert a list of Commit objects into a list of strings.

    Args:
        commits (List[Commit]): A list of Commit objects to be converted.

    Returns:
        List[str]: A list of strings representing each Commit object.

    This function takes a list of Commit objects and converts them into a list of strings. Each string represents a Commit object and contains the author, message, date, and hash of the commit. 
    The message is formatted by replacing new lines with periods. The hash is truncated to the first 8 characters.+
    """
    new_line = "\n"
    commit_to_str: Callable[[Commit], str] = (
        lambda commit: f"{commit['authour']}: {commit['message'].replace(new_line, '.')} {new_line}{commit['date']} {commit['hash'][0:8]}"
    )
    return list(map(commit_to_str, commits))
