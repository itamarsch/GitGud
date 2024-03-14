from typing import cast
import wx

from main import MainFrame


class BaseScreen(wx.Panel):

    def __init__(self, parent, top: int, bottom: int, width: int = 10):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(top)

        self.add_children(main_sizer)

        main_sizer.AddStretchSpacer(bottom)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if self.GetParent().screens:

            return_button_sizer = wx.BoxSizer(wx.VERTICAL)
            return_button = wx.Button(self, label="🡐")
            return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())
            return_button_sizer.Add(return_button, 0, wx.LEFT)

            outer_sizer.Add(return_button_sizer, 1, wx.EXPAND)
        else:
            outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, width, wx.CENTER | wx.EXPAND)
        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def GetParent(self) -> MainFrame:
        return cast(MainFrame, super().GetParent())

    def add_children(self, main_sizer: wx.BoxSizer):
        pass
