from typing_extensions import Optional, override
from base_screen import BaseScreen
import wx
from gui_run_request import gui_run_request
from client_protocol import Issue, pack_create_issue, pack_update_issue

from main import MainFrame


class IssueEditor(BaseScreen):
    def __init__(
        self,
        parent: MainFrame,
        initial_issue: Optional[Issue],
        connection_token: str,
        repo: str,
    ):
        """
        Initializes a new instance of the IssueEditor class.

        Args:
            parent (MainFrame): The parent frame of the IssueEditor.
            initial_issue (Optional[Issue]): An optional Issue object representing the initial issue.
            connection_token (str): A string representing the connection token.
            repo (str): A string representing the repository.

        Initializes the IssueEditor with the given parent frame, initial issue, connection token, and repository.
        Sets the initial_issue, connection_token, and repo attributes.
        Calls the parent class's __init__ method with the provided parameters and title "Issue".

        """
        self.initial_issue = initial_issue
        self.connection_token = connection_token
        self.repo = repo
        super().__init__(parent, 1, 2, title="Issue")

    @override
    def add_children(self, main_sizer):

        # Title Field
        self.title_field = wx.TextCtrl(self)
        title_font = wx.Font(
            20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        self.title_field.SetFont(title_font)
        self.title_field.SetHint("Title")

        main_sizer.Add(
            self.title_field, proportion=0, flag=wx.EXPAND | wx.ALL, border=10
        )

        # Content Field
        self.content_field = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        if self.initial_issue:
            self.content_field.WriteText(self.initial_issue["content"])
            self.title_field.WriteText(self.initial_issue["title"])

        main_sizer.Add(
            self.content_field, proportion=1, flag=wx.EXPAND | wx.ALL, border=10
        )

        # Submit Button
        submit_button = wx.Button(self, label="Submit")
        submit_button.Bind(wx.EVT_BUTTON, self.on_submit)
        main_sizer.Add(submit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

    def on_submit(self, _):
        """
        A function that handles form submission. It retrieves the title and content from the form fields. 
        If there is an initial issue, it updates the issue with the new title and content. 
        If there is no initial issue, it creates a new issue with the provided title and content.
        """
        title = self.title_field.GetValue()
        content = self.content_field.GetValue()

        def on_finished(_):
            self.GetParent().pop_screen()

        if self.initial_issue:

            gui_run_request(
                self,
                pack_update_issue(
                    self.initial_issue["id"],
                    self.connection_token,
                    title,
                    content,
                ),
                on_finished,
            )
        else:

            def on_finished(_):
                self.GetParent().pop_screen()
                pass

            gui_run_request(
                self,
                pack_create_issue(self.repo, self.connection_token, title, content),
                on_finished,
            )
