from typing_extensions import override
import wx
import wx.richtext

from base_screen import BaseScreen
from main import MainFrame


class Diff(BaseScreen):
    def __init__(self, parent: MainFrame, diff: str):

        self.diff = diff
        super().__init__(parent, 0, 1)

    @override
    def add_children(self, main_sizer):

        diff_richtextctrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)

        font = wx.Font(
            14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        diff_richtextctrl.SetFont(font)

        # Clear existing content
        diff_richtextctrl.Clear()

        # Split the string into lines
        lines = self.diff.split("\n")

        for line in lines:
            if line.startswith("+"):
                diff_richtextctrl.BeginTextColour(wx.GREEN)
            elif line.startswith("-"):
                diff_richtextctrl.BeginTextColour(wx.RED)
            else:
                diff_richtextctrl.BeginTextColour(wx.BLACK)
            diff_richtextctrl.WriteText(line + "\n")
            diff_richtextctrl.EndTextColour()


        main_sizer.Add(diff_richtextctrl, 15, wx.CENTER | wx.EXPAND)
