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
        self.Layout()

    def on_reload(self):
        """ 
        Function that can be overrided by the child class.
        This function is called once a screen is reloaded after a pop of a screen on top of it
        """
        pass


    def GetParent(self) -> MainFrame:
        """
        A method for getting the parent of the `BaseScreen` which os always a `MainFrame`

        """
        return cast(MainFrame, super().GetParent())

    def add_children(self, main_sizer: wx.BoxSizer):
        """
        Function that should be overrided by the child class.
        Adds all ui widgets to the main sizer

        Parameters:
            main_sizer (wx.BoxSizer): The main sizer to add children to.
        """
        pass
