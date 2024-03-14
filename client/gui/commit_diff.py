from typing_extensions import override
import wx

from base_screen import BaseScreen


class CommitDiff(BaseScreen):
    def __init__(self, parent, diff: str):

        self.diff = diff
        super().__init__(parent, 0, 1)

    @override
    def add_children(self, main_sizer):

        diff_textctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        font = wx.Font(
            14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        diff_textctrl.SetFont(font)
        # Split the string into lines
        lines = self.diff.split("\n")

        # Iterate over the lines and set background color based on starting character
        for line in lines:
            if line.startswith("+"):
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.GREEN))
            elif line.startswith("-"):
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
            else:
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            diff_textctrl.AppendText(line + "\n")

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(diff_textctrl, 15, wx.CENTER | wx.EXPAND)
