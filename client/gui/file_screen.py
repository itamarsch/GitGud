import wx
import wx.html2
import pygments
from typing import cast
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.formatters import HtmlFormatter


class FileContent(wx.Panel):
    def __init__(self, parent, file_content: str, file_name: str):
        super().__init__(parent)

        lexer = get_lexer_for_filename(file_name)

        formatter = HtmlFormatter(full=True)
        formatted_content = highlight(file_content, lexer, formatter)

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        file_styled_text = cast(wx.html2.WebView, wx.html2.WebView.New(self))
        file_styled_text.SetBackgroundColour(self.GetBackgroundColour())
        file_styled_text.SetPage(formatted_content, "")

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)

        main_sizer.Add(return_button, 0, wx.CENTER | wx.EXPAND)

        main_sizer.Add(file_styled_text, 1, wx.CENTER | wx.EXPAND)

        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)

        outer_sizer.Add(main_sizer, 1, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)
