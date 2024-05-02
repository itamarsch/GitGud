from typing_extensions import override
import wx
from typing import List, cast
from base_screen import BaseScreen
from gui.commits import Commits
from gui.file_screen import FileContent
from gui.issues import Issues
from client_protocol import (
    pack_branches,
    pack_commits,
    pack_file_request,
    pack_project_directory,
    pack_search_repo,
)
from gui.pull_requests import PullRequests
from gui.repo_create import RepoCreate
from gui_run_request import gui_request_file, gui_run_request
import pyperclip
from gitgud_types import Json
from main import MainFrame

branches_placeholder = "Select a branch"


class RepoScreen(BaseScreen):
    def __init__(self, parent: MainFrame, connection_token: str):
        self.connection_token = connection_token
        self.directory = ""
        self.branch = ""
        self.repo = ""
        super().__init__(parent, 1, 1, title="Repo")

    @override
    def add_children(self, main_sizer):
        # Username
        repo_label = wx.StaticText(self, label="Repo")
        self.repo_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)

        self.repo_text.Bind(wx.EVT_TEXT, self.on_text_changed)
        self.repo_text.Bind(wx.EVT_TEXT_ENTER, self.on_repo_enter)

        self.repo_suggestions = wx.ListBox(self)
        self.repo_suggestions.Bind(
            wx.EVT_LISTBOX_DCLICK, self.on_search_result_selected
        )

        repo_options = wx.BoxSizer(wx.HORIZONTAL)

        self.branches_list = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.branches_list.Bind(wx.EVT_COMBOBOX, self.on_branch_selected)

        commits_button = wx.Button(self, label="Commits")
        commits_button.Bind(wx.EVT_BUTTON, self.on_commits_screen_button)

        issues_button = wx.Button(self, label="Issues")
        issues_button.Bind(wx.EVT_BUTTON, self.on_issues_screen_button)

        pull_requests_button = wx.Button(self, label="Pull requests")
        pull_requests_button.Bind(wx.EVT_BUTTON, self.on_pr_screen_button)

        copy_git_url_button = wx.Button(self, label="Copy repo url")
        copy_git_url_button.Bind(wx.EVT_BUTTON, self.copy_repo_url)

        repo_create_button = wx.Button(self, label="Create repo")
        repo_create_button.Bind(
            wx.EVT_BUTTON,
            lambda _: self.GetParent().push_screen(
                lambda: RepoCreate(self.GetParent(), self.connection_token)
            ),
        )

        repo_options_widget = [
            self.repo_suggestions,
            self.branches_list,
            commits_button,
            issues_button,
            pull_requests_button,
            copy_git_url_button,
            repo_create_button,
        ]
        for i, widget in enumerate(repo_options_widget):
            repo_options.Add(widget, 2, wx.EXPAND)
            if i != len(repo_options_widget) - 1:
                repo_options.AddSpacer(5)

        self.directory_list = wx.ListBox(self, choices=[])
        self.directory_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_file_selected)
        font = wx.Font(
            12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        self.directory_list.SetFont(font)

        main_sizer.Add(repo_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.repo_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(repo_options, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.directory_list, 10, wx.CENTER | wx.EXPAND)

    def on_text_changed(self, event):
        """
        Handle the text changed event, perform a search for repository suggestions based on the entered query and display them.

        """
        query = event.GetEventObject().GetValue()
        if query:

            def on_finished(result: Json):
                options = result["repos"]

                self.repo_suggestions.Clear()
                self.repo_suggestions.SetItems(options)

            gui_run_request(self, pack_search_repo(query), on_finished)

    def on_search_result_selected(self, _):
        """
        Handle the event when a search result is selected. Updates the repository text and triggers the on_repo_enter method.
        """
        selection = self.repo_suggestions.GetSelection()
        if selection != wx.NOT_FOUND:
            repo = self.repo_suggestions.GetString(selection)
            self.repo_text.Clear()
            self.repo_text.WriteText(repo)
            self.on_repo_enter(None)

    def on_repo_enter(self, _):
        """
        A function that a called once a rpeo is selected.
        It retreives the selected repo and requests the branches.
        """

        def on_finished(response: Json):
            self.branches_list.Clear()
            self.branches_list.Append(branches_placeholder)
            self.branches_list.Append(response["branches"])
            self.branches_list.SetSelection(0)
            self.branch = ""
            self.directory_list.Clear()

        self.repo = self.repo_text.GetValue()

        gui_run_request(
            self,
            pack_branches(self.repo, self.connection_token),
            on_finished,
        )

    def on_branch_selected(self, _):
        """
        This function handles the event when a branch is selected.
        It gets the selected branch from the list and updates the 'branch' and 'directory' attributes accordingly.
        It then calls 'request_directory_structure' to update the directory structure based on the new branch.
        """
        selection = self.branches_list.GetSelection()
        if selection != wx.NOT_FOUND:
            branch = self.branches_list.GetString(selection)
            if branch == branches_placeholder:
                return
            self.branch = branch
            self.directory = ""
            self.request_directory_structure()

    def on_commits_screen_button(self, _):
        """
        A function that handles button clicks on the commits screen.
        Checks if repository and branch are filled, shows a message box if not, then pushes the commits screen using the parent's connection token and repo information.
        """
        if not self.repo or not self.branch:
            wx.MessageBox("Please fill in fields")
            return

        self.GetParent().push_screen(
            lambda: Commits(
                self.GetParent(),
                self.connection_token,
                lambda page: pack_commits(
                    self.repo, self.connection_token, self.branch, page
                ),
                self.repo,
            )
        )

    def on_issues_screen_button(self, _):
        """
        Handles the button click on the issues screen and navigates to the issues screen with the given repository and connection token.
        """
        if not self.repo:
            wx.MessageBox("Please fill in fields")
            return

        self.GetParent().push_screen(
            lambda: Issues(self.GetParent(), self.repo, self.connection_token)
        )

    def on_pr_screen_button(self, _):
        """
        A function that handles the button click event on the pull request screen.
        It checks if the repository is filled, displays a message box if it's empty,
        and then pushes a new screen for pull requests
        """
        if not self.repo:
            wx.MessageBox("Please fill in fields")
            return

        self.GetParent().push_screen(
            lambda: PullRequests(self.GetParent(), self.repo, self.connection_token)
        )

    def copy_repo_url(self, _):
        """
        A function that copies the repository URL to the clipboard if a repository is set.
        """
        if self.repo:
            pyperclip.copy(f"git@fedora:{self.repo}.git")

    def on_file_selected(self, _):
        """
        A function that handles the event when a file is selected.
        It retrieves the selected file, checks if it's a directory, and based on that either updates the current directory and requests the directory structure or requests the selected file.
        """
        selection = self.directory_list.GetSelection()
        if selection != wx.NOT_FOUND:

            file_name = cast(str, self.directory_list.GetString(selection))
            if file_name.endswith("/"):
                self.directory += file_name
                self.request_directory_structure()
            else:
                self.request_file(file_name)

    def request_file(self, file_name: str):
        """
        Requests a file with the given file name and displays its content in the GUI.

        Parameters:
            file_name (str): The name of the file to request.

        Returns:
            None
        """

        def on_finished(result: bytes):
            try:
                file_content_str = result.decode()
                self.GetParent().push_screen(
                    lambda: FileContent(self.GetParent(), file_content_str, file_name)
                )
            except (UnicodeDecodeError, AttributeError):
                wx.MessageBox("File not string :(")

        gui_request_file(
            self,
            pack_file_request(
                self.repo,
                self.connection_token,
                self.directory + file_name,
                self.branch,
            ),
            on_finished,
        )

    def request_directory_structure(self):
        """
        Request the directory structure and update the directory list in the GUI.

        Parameters:
            self: The instance of the class.

        Returns:
            None
        """

        def on_finished(result: Json):
            self.directory_list.Clear()
            if not is_base_directory(self.directory):
                self.directory_list.Append("../")
            self.directory_list.Append(result["files"])
            pass

        gui_run_request(
            self,
            pack_project_directory(
                self.directory,
                self.repo_text.GetValue(),
                self.branch,
                self.connection_token,
            ),
            on_finished,
        )


def is_base_directory(path: str) -> bool:
    """
    A function to check if the given path represents a base directory.

    Parameters:
    path (str): The path to be checked.

    Returns:
    bool: True if the path represents a base directory, False otherwise.
    """
    dirs = [dir for dir in path.split("/") if dir]

    double_dots = [dir for dir in dirs if dir == ".."]

    return len(double_dots) == len(dirs) / 2
