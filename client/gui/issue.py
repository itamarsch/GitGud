from typing_extensions import override
import wx
from base_screen import BaseScreen
from client_protocol import Issue
from main import MainFrame


class IssueViewer(BaseScreen):
    def __init__(self, parent: MainFrame, issue: Issue):
        """
        Initializes a new instance of the IssueViewer class.

        Args:
            parent (MainFrame): The parent frame of the IssueViewer.
            issue (Issue): The issue to be displayed.

        Returns:
            None
        """
        self.issue = issue
        super().__init__(parent, 2, 1, title=self.issue["title"])

    @override
    def add_children(self, main_sizer):

        content = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        content_font = wx.Font(
            17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        content.SetFont(content_font)
        content.WriteText(self.issue["content"])

        username = wx.StaticText(self, label=f"By: {self.issue['username']}")

        main_sizer.Add(username, 1)

        main_sizer.Add(content, 15, wx.CENTER | wx.EXPAND)
