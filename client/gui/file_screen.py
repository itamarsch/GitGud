from typing_extensions import override
import pygments.util
import wx
import wx.html2
from typing import cast
from pygments import highlight
from pygments.lexer import RegexLexer
from pygments.token import Text
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from base_screen import BaseScreen
from main import MainFrame


class NoopLexer(RegexLexer):
    """
    A pygments kexer that does nothing for unkown file types
    """
    name = "null"
    aliases = []
    filenames = []

    tokens = {
        "root": [
            (r".+", Text),  # Match anything as Text
        ],
    }


class FileContent(BaseScreen):
    def __init__(self, parent: MainFrame, file_content: str, file_name: str):
        self.file_content = file_content
        self.file_name = file_name
        super().__init__(parent, 0, 0)

    @override
    def add_children(self, main_sizer):
        formatted_content = self.get_highlighted_html()


        file_styled_text = cast(wx.html2.WebView, wx.html2.WebView.New(self))
        file_styled_text.SetPage(formatted_content, "")

        main_sizer.Add(file_styled_text, 15, wx.CENTER | wx.EXPAND)

    def get_highlighted_html(self) -> str:
        """
        Get the highlighted HTML content of the file using Pygments.
        """
        try:
            lexer = get_lexer_for_filename(self.file_name)
        except pygments.util.ClassNotFound:
            lexer = NoopLexer()

        # python -c "from pygments.styles import get_all_styles; styles = list(get_all_styles()); print(*styles, sep='\n')"
        formatter = HtmlFormatter(
            full=True, style="gruvbox-dark", cssstyles=f"font-size: 25px;", linenos=True
        )
        return highlight(self.file_content, lexer, formatter)

