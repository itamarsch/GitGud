from typing_extensions import override
import wx
from base_screen import BaseScreen
from client_protocol import Issue


class IssueViewer(BaseScreen):
    def __init__(self, parent, issue: Issue):
        self.issue = issue
        super().__init__(parent, 0, 1)

    @override
    def add_children(self, main_sizer):

        title_font = wx.Font(
            20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title_sizer.AddStretchSpacer(1)

        title = wx.StaticText(self)
        title.SetFont(title_font)
        title.SetLabel(self.issue["title"])
        title.Center()

        title_sizer.Add(title, 0, wx.EXPAND)

        title_sizer.AddStretchSpacer(1)

        content = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        content_font = wx.Font(
            17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        content.SetFont(content_font)
        content.WriteText(self.issue["content"])

        username = wx.StaticText(self, label=f"By: {self.issue['username']}")

        main_sizer.Add(title_sizer, 2, wx.CENTER | wx.EXPAND)
        main_sizer.Add(username, 1)

        main_sizer.Add(content, 15, wx.CENTER | wx.EXPAND)
