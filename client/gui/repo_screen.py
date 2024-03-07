import wx
from typing import cast
from gui.file_screen import FileContent
from client_protocol import pack_branches, pack_file_request, pack_project_directory
from gui.gui_run_request import gui_request_file, gui_run_request

from gitgud_types import Json


class RepoScren(wx.Panel):
    def __init__(self, parent, connection_token: str):
        super().__init__(parent)
        self.connection_token = connection_token
        self.directory = ""
        self.branch = ""

        # Username
        repo_label = wx.StaticText(self, label="Repo")
        self.repo_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)

        self.repo_text.Bind(wx.EVT_TEXT_ENTER, self.on_repo_enter)

        branches_label = wx.StaticText(self, label="Branches")

        self.branches_list = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.branches_list.Bind(wx.EVT_COMBOBOX, self.on_branch_selected)

        self.directory_list = wx.ListBox(self, choices=[])
        self.directory_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_file_selected)

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(repo_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.repo_text, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(branches_label, 0, wx.CENTER | wx.EXPAND)
        main_sizer.Add(self.branches_list, 0, wx.CENTER | wx.EXPAND)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.directory_list, 2, wx.CENTER | wx.EXPAND)

        main_sizer.AddStretchSpacer(5)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)
        outer_sizer.Add(main_sizer, 8, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)

    def on_repo_enter(self, _):
        def on_finished(response: Json):
            self.branches_list.Clear()
            self.branches_list.Append(response["branches"])

        self.repo = self.repo_text.GetValue()

        gui_run_request(
            self,
            pack_branches(self.repo, self.connection_token),
            on_finished,
        )

        pass

    def on_branch_selected(self, _):
        selection = self.branches_list.GetSelection()
        if selection != wx.NOT_FOUND:
            self.branch = self.branches_list.GetString(selection)
            self.directory = ""
            self.request_directory_structure()

    def on_file_selected(self, _):
        selection = self.directory_list.GetSelection()
        if selection != wx.NOT_FOUND:

            file_name = cast(str, self.directory_list.GetString(selection))
            if file_name.endswith("/"):
                self.directory += file_name
                self.request_directory_structure()
                return

            def on_finished(result: bytes):
                try:
                    file_content_str = result.decode()
                    self.GetParent().push_screen(
                        FileContent(self.GetParent(), file_content_str, file_name)
                    )
                except (UnicodeDecodeError, AttributeError):
                    wx.MessageBox("File not string :(")

            gui_request_file(
                self,
                pack_file_request(
                    self.repo,
                    self.connection_token,
                    self.directory + file_name,
                    self.branch,
                ),
                on_finished,
            )

    def request_directory_structure(self):
        def on_finished(result: Json):
            self.directory_list.Clear()
            if not is_base_directory(self.directory):
                self.directory_list.Append("../")
            self.directory_list.Append(result["files"])
            pass

        gui_run_request(
            self,
            pack_project_directory(
                self.directory,
                self.repo_text.GetValue(),
                self.branch,
                self.connection_token,
            ),
            on_finished,
        )


def is_base_directory(path: str) -> bool:
    dirs = [dir for dir in path.split("/") if dir]

    double_dots = [dir for dir in dirs if dir == ".."]

    return len(double_dots) == len(dirs) / 2
