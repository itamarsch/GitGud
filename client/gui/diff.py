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

        self.diff_richtextctrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)

        font = wx.Font(
            14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        self.diff_richtextctrl.SetFont(font)

        self.write_and_color_diff()



        main_sizer.Add(self.diff_richtextctrl, 15, wx.CENTER | wx.EXPAND)

    def write_and_color_diff(self):
        """
        This function writes and color-codes the lines of a difference string in the rich text control. 
        Lines starting with '+' are colored green, those starting with '-' are red, and the rest are black.
        """
        self.diff_richtextctrl.Clear()
        lines = self.diff.split("\n")
        for line in lines:
            if line.startswith("+"):
                self.diff_richtextctrl.BeginTextColour(wx.GREEN)
            elif line.startswith("-"):
                self.diff_richtextctrl.BeginTextColour(wx.RED)
            else:
                self.diff_richtextctrl.BeginTextColour(wx.BLACK)
            self.diff_richtextctrl.WriteText(line + "\n")
            self.diff_richtextctrl.EndTextColour()
