import wx
import wx.html2
from typing import cast
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter


class FileContent(wx.Panel):
    def __init__(self, parent, file_content: str, file_name: str):
        super().__init__(parent)

        lexer = get_lexer_for_filename(file_name)

        # python -c "from pygments.styles import get_all_styles; styles = list(get_all_styles()); print(*styles, sep='\n')"
        formatter = HtmlFormatter(
            full=True,
            style="gruvbox-dark",
            cssstyles=f"font-size: 25px;",
        )
        formatted_content = highlight(file_content, lexer, formatter)

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        file_styled_text = cast(wx.html2.WebView, wx.html2.WebView.New(self))
        file_styled_text.SetPage(formatted_content, "")

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(return_button, 0, wx.CENTER | wx.EXPAND)

        main_sizer.Add(file_styled_text, 15, wx.CENTER | wx.EXPAND)
        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)

        outer_sizer.Add(main_sizer, 10, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)
