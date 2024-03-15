from typing import cast
from typing_extensions import Optional
import wx

from main import MainFrame


class BaseScreen(wx.Panel):

    def __init__(
        self,
        parent: MainFrame,
        top: int,
        bottom: int,
        width: int = 10,
        title: Optional[str] = None,
    ):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        if title:
            title_text = wx.StaticText(self, label=title)

            title_font = wx.Font(
                40, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )
            title_text.SetFont(title_font)
            main_sizer.Add(title_text, top, wx.ALIGN_CENTER_HORIZONTAL)
        else:
            main_sizer.AddStretchSpacer(top)

        self.add_children(main_sizer)

        main_sizer.AddStretchSpacer(bottom)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if len(self.GetParent().screens) > 1:

            return_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            return_button = wx.Button(self, label="🡐")
            return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())
            return_button_sizer.Add(return_button, 1, wx.LEFT)
            return_button_sizer.AddStretchSpacer(1)

            outer_sizer.Add(return_button_sizer, 1, wx.EXPAND | wx.TOP)
        else:
            outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, width, wx.CENTER | wx.EXPAND)
        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def GetParent(self) -> MainFrame:
        return cast(MainFrame, super().GetParent())

    def add_children(self, main_sizer: wx.BoxSizer):
        pass
