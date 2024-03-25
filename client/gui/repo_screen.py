from typing_extensions import override
import wx
from typing import cast
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
            repo_options.Add(widget, 1, wx.EXPAND)
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
        query = event.GetEventObject().GetValue()
        if query:

            def on_finished(result: Json):
                options = result["repos"]

                self.repo_suggestions.Clear()
                self.repo_suggestions.SetItems(options)

            gui_run_request(self, pack_search_repo(query), on_finished)

    def on_search_result_selected(self, _):
        selection = self.repo_suggestions.GetSelection()
        if selection != wx.NOT_FOUND:
            repo = self.repo_suggestions.GetString(selection)
            self.repo_text.Clear()
            self.repo_text.WriteText(repo)
            self.on_repo_enter(None)

    def on_repo_enter(self, _):

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
        selection = self.branches_list.GetSelection()
        if selection != wx.NOT_FOUND:
            branch = self.branches_list.GetString(selection)
            if branch == branches_placeholder:
                return
            self.branch = branch
            self.directory = ""
            self.request_directory_structure()

    def on_commits_screen_button(self, _):
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
        if not self.repo:
            wx.MessageBox("Please fill in fields")
            return

        self.GetParent().push_screen(
            lambda: Issues(self.GetParent(), self.repo, self.connection_token)
        )

    def on_pr_screen_button(self, _):
        if not self.repo:
            wx.MessageBox("Please fill in fields")
            return

        self.GetParent().push_screen(
            lambda: PullRequests(self.GetParent(), self.repo, self.connection_token)
        )

    def copy_repo_url(self, _):
        if self.repo:
            pyperclip.copy(f"git@itamarfedora:{self.repo}.git")

    def on_file_selected(self, _):
        selection = self.directory_list.GetSelection()
        if selection != wx.NOT_FOUND:

            file_name = cast(str, self.directory_list.GetString(selection))
            if file_name.endswith("/"):
                self.directory += file_name
                self.request_directory_structure()
                return

            def on_finished(result: bytes):
                try:
                    file_content_str = result.decode()
                    self.GetParent().push_screen(
                        lambda: FileContent(
                            self.GetParent(), file_content_str, file_name
                        )
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
    dirs = [dir for dir in path.split("/") if dir]

    double_dots = [dir for dir in dirs if dir == ".."]

    return len(double_dots) == len(dirs) / 2
