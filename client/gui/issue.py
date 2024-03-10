import wx
from client_protocol import Issue


class IssueViewer(wx.Panel):
    def __init__(self, parent, issue: Issue):
        super().__init__(parent)

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        title_font = wx.Font(
            20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title_sizer.AddStretchSpacer(1)

        title = wx.StaticText(self)
        title.SetFont(title_font)
        title.SetLabel(issue["title"])
        title.Center()

        title_sizer.Add(title, 0, wx.EXPAND)

        title_sizer.AddStretchSpacer(1)

        content = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        content.Disable()

        content_font = wx.Font(
            17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        content.SetFont(content_font)
        content.WriteText(issue["content"])

        username = wx.StaticText(self, label=f"By: {issue['username']}")

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(return_button, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(title_sizer, 2, wx.CENTER | wx.EXPAND)
        main_sizer.Add(username, 1)

        main_sizer.Add(content, 15, wx.CENTER | wx.EXPAND)
        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)

        outer_sizer.Add(main_sizer, 10, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)
