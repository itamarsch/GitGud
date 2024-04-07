from typing import Callable, cast
from base_screen import BaseScreen
from gitgud_types import Json
from threading import Thread
import wx

from main import MainFrame


def gui_request_file(
    panel: BaseScreen, request: Json, on_finished: Callable[[bytes], None]
):
    """
    A function that sends a file request to the GUI, runs the request, and calls the on_finished callback with the file content.
    
    Parameters:
        panel (BaseScreen): The panel to send the request.
        request (Json): The request to send.
        on_finished (Callable[[bytes], None]): The callback function to call with the file content.
    """

    parent = panel.GetParent()

    def run_request(request: Json):
        result = parent.client_com.run_request(request)
        if "error" in result:
            wx.CallAfter(wx.MessageBox, f"Error: {result['error']}")
            return

        file_content = parent.client_com.file_request(result["token"], result["port"])
        wx.CallAfter(on_finished, file_content)

    Thread(target=run_request, args=(request,)).start()


def gui_run_request(
    panel: BaseScreen,
    request: Json,
    on_finished: Callable[[Json], None],
    message_box_error=True,
):
    """
    A function to run a request in a GUI environment and handle the response asynchronously.

    Parameters:
        panel (BaseScreen): The screen panel where the request will be executed.
        request (Json): The request to be executed.
        on_finished (Callable[[Json], None]): A callback function to handle the response when the request is finished.
        message_box_error (bool, optional): A flag to show error messages in a message box. Defaults to True.
    """
    parent = panel.GetParent()

    def run_request(request: Json):
        result = parent.client_com.run_request(request)
        if message_box_error and "error" in result:

            wx.CallAfter(wx.MessageBox, f"Error: {result['error']}")

        else:
            wx.CallAfter(on_finished, result)

    Thread(target=run_request, args=(request,)).start()
