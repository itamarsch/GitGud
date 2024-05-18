import wx
from client_comm import ClientComm
from typing import Callable, Optional, TypeVar, cast, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from base_screen import BaseScreen
else:
    BaseScreen = TypeVar("BaseScreen")


class MainFrame(wx.Frame):

    def __init__(self, client_com: ClientComm, connection_token: Optional[str]):
        super().__init__(None, title="GitGud")

        self.client_com = client_com

        self.screens: List[BaseScreen] = []

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        if connection_token:
            from gui.repo_screen import RepoScreen

            self.push_screen(lambda: RepoScreen(self, connection_token))
        else:
            from gui.register import RegisterPanel

            self.push_screen(lambda: RegisterPanel(self))
        self.Maximize()

        self.Show()

    def push_screen(self, screen_fn: Callable[[], BaseScreen]):
        """
        Pushes a new screen onto the screen stack and sets it as the active screen.
        Hides the previous screen if there is one.
        Parameters:
            screen_fn: A Callable that returns a BaseScreen, representing the function to generate the new screen.
        Returns:
            None
        """
        if self.screens:
            self.screens[-1].Hide()
            self.sizer.Remove(0)

        from base_screen import BaseScreen

        self.screens.append(cast(BaseScreen, None))
        self.screens[-1] = screen_fn()
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def pop_screen(self):
        """
        Pops the top screen, hides it, and then shows the new top screen.
        """
        self.screens[-1].Hide()
        self.screens.pop()
        self.screens[-1].Show()
        self.screens[-1].on_reload()
        self.sizer.Remove(0)
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def change_screen(self, panel: Callable[[], BaseScreen]):
        """
        Changes the current screen to the one provided by the panel parameter.

        Parameters:
            panel (Callable[[], BaseScreen]): A function that returns a BaseScreen instance.

        Returns:
            None
        """
        self.screens[-1].Hide()
        self.screens[-1] = panel()
        self.screens[-1].Show()
        self.sizer.Remove(0)
        self.sizer.Add(self.screens[-1], 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
