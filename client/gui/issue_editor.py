from typing_extensions import override
from base_screen import BaseScreen
import wx

from main import MainFrame


class IssueViewer(BaseScreen):
    def __init__(self, parent: MainFrame):
        super().__init__(parent, 2, 1, title="Issue")

    @override
    def add_children(self, main_sizer):

        # Title Field
        self.title_field = wx.TextCtrl(self)

        main_sizer.Add(
            self.title_field, proportion=0, flag=wx.EXPAND | wx.ALL, border=10
        )

        # Content Field
        self.content_field = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        main_sizer.Add(
            self.content_field, proportion=1, flag=wx.EXPAND | wx.ALL, border=10
        )

        # Submit Button
        submit_button = wx.Button(self, label="Submit")
        submit_button.Bind(wx.EVT_BUTTON, self.OnSubmit)
        main_sizer.Add(submit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

    def OnSubmit(self, event):
        title = self.title_field.GetValue()
        content = self.content_field.GetValue()

        # Here you can implement your custom logic for submitting the issue
        # For now, let's just print the title and content
        print("Title:", title)
        print("Content:", content)
