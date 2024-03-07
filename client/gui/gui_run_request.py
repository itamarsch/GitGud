from typing import Callable, cast
from gitgud_types import Json
from threading import Thread
import wx

from main import MainFrame


def gui_request_file(
    panel: wx.Panel, request: Json, on_finished: Callable[[bytes], None]
):

    parent = cast(MainFrame, panel.GetParent())

    def run_request(request: Json):
        result = parent.client_com.run_request(request)
        if "error" in result:
            print(result)

        file_content = parent.client_com.file_request(result["token"], result["port"])
        wx.CallAfter(on_finished, file_content)

    Thread(target=run_request, args=(request,)).start()


def gui_run_request(
    panel: wx.Panel, request: Json, on_finished: Callable[[Json], None]
):
    parent = cast(MainFrame, panel.GetParent())

    def run_request(request: Json):
        result = parent.client_com.run_request(request)
        wx.CallAfter(on_finished, result)

    Thread(target=run_request, args=(request,)).start()
