from typing import List, cast
from typing_extensions import Optional, override
from base_screen import BaseScreen
import wx
from gitgud_types import Json
from gui_run_request import gui_run_request
from client_protocol import (
    PullRequest,
    pack_branches,
    pack_create_pull_request,
    pack_update_pull_request,
)

from main import MainFrame


class PullRequestEditor(BaseScreen):
    def __init__(
        self,
        parent: MainFrame,
        initial_issue: Optional[PullRequest],
        connection_token: str,
        repo: str,
    ):
        """
        Initializes a new instance of the PullRequestEditor class.

        Args:
            parent (MainFrame): The parent frame of the PullRequestEditor.
            initial_issue (Optional[PullRequest]): The initial pull request to edit, if any.
            connection_token (str): The connection token for the PullRequestEditor.
            repo (str): The repository name for the PullRequestEditor.

        Returns:
            None
        """
        self.branches: List[str] = []
        self.initial_pr = initial_issue
        self.connection_token = connection_token
        self.repo = repo
        super().__init__(parent, 1, 4, width=1, title="Pull Request")

    @override
    def add_children(self, main_sizer):

        text_field_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_field_sizer.AddStretchSpacer(1)

        # Title Field
        self.title_field = wx.TextCtrl(self)
        title_font = wx.Font(
            20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        text_field_sizer.Add(self.title_field, 1)
        text_field_sizer.AddStretchSpacer(1)

        self.title_field.SetFont(title_font)
        self.title_field.SetHint("Title")

        self.from_branches = wx.ComboBox(self, choices=[])
        self.from_branches.SetHint("From branch")

        self.into_branches = wx.ComboBox(self, choices=[])
        self.into_branches.SetHint("Into branch")

        main_sizer.Add(text_field_sizer, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        branches_sizer = wx.BoxSizer(wx.HORIZONTAL)
        branches_sizer.AddStretchSpacer(4)
        branches_sizer.Add(self.from_branches, 1, wx.EXPAND)
        branches_sizer.AddSpacer(5)
        arrow = wx.StaticText(self, label="->")
        branches_sizer.Add(arrow, 0, wx.CENTER)
        branches_sizer.AddSpacer(5)
        branches_sizer.Add(self.into_branches, 1, wx.EXPAND)
        branches_sizer.AddStretchSpacer(4)

        main_sizer.Add(branches_sizer, 0, wx.EXPAND)
        main_sizer.AddSpacer(5)

        def on_branches_received(response: Json):
            """
            Set the branches received from the JSON response to the appropriate attributes.
            Clear and append the branches to the from_branches and into_branches.
            If initial_pr is True, set the selection based on the initial PR's fromBranch and intoBranch.
            """
            self.branches = cast(List[str], response["branches"])
            self.from_branches.Clear()
            self.from_branches.Append(self.branches)

            self.into_branches.Clear()
            self.into_branches.Append(self.branches)

            if self.initial_pr:
                from_index: int = self.into_branches.FindString(
                    self.initial_pr["fromBranch"]
                )
                into_index: int = self.into_branches.FindString(
                    self.initial_pr["intoBranch"]
                )

                self.from_branches.SetSelection(from_index)
                self.into_branches.SetSelection(into_index)

        gui_run_request(
            self, pack_branches(self.repo, self.connection_token), on_branches_received
        )

        if self.initial_pr:
            self.title_field.WriteText(self.initial_pr["title"])

        # Submit Button
        submit_button = wx.Button(self, label="Submit")
        submit_button.Bind(wx.EVT_BUTTON, self.on_submit)
        main_sizer.Add(submit_button, 0, wx.ALIGN_CENTER | wx.ALL)

    def on_submit(self, _):
        """
        A function that handles form submission. Retrieves title and branch selections, then either updates an existing pull request or creates a new one based on the initial_pr.
        """
        title = self.title_field.GetValue()
        if not self.branches:
            return

        from_branch = self.branches[self.from_branches.GetCurrentSelection()]
        into_branch = self.branches[self.into_branches.GetCurrentSelection()]

        def on_finished(_):
            self.GetParent().pop_screen()

        if self.initial_pr:

            gui_run_request(
                self,
                pack_update_pull_request(
                    self.initial_pr["id"],
                    self.connection_token,
                    title,
                    from_branch,
                    into_branch,
                ),
                on_finished,
            )
        else:

            def on_finished(_):
                self.GetParent().pop_screen()
                pass

            gui_run_request(
                self,
                pack_create_pull_request(
                    self.repo, self.connection_token, title, from_branch, into_branch
                ),
                on_finished,
            )
