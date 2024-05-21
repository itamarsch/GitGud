from typing import List, Optional
from typing_extensions import override
import wx
import wx.richtext

from base_screen import BaseScreen
from gitgud_types import Json
from main import MainFrame
import json


class Diff(BaseScreen):
    def __init__(self, parent: MainFrame, diff: bytes):
        """
        Initializes a new instance of the Diff class.

        Args:
            parent (MainFrame): The parent frame of the Diff.
            diff (bytes): The diff data.

        Initializes the Diff with the given parent frame and diff data.
        Sets the diff attribute to the provided diff data.
        Calls the parent class's __init__ method with the provided parameters.

        """

        self.diff = diff
        super().__init__(parent, 0, 1)

    @override
    def add_children(self, main_sizer):

        try:
            diff: Optional[Json] = json.loads(self.diff.decode())
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            diff: Optional[Json] = None

        self.diff_richtextctrl = wx.richtext.RichTextCtrl(
            self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER
        )
        font = wx.Font(
            14,
            wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        self.diff_richtextctrl.SetFont(font)

        self.diff_richtextctrl.SetBackgroundColour(wx.Colour("#1d2021"))

        if diff:
            self.write_and_color_diff(diff)

        main_sizer.Add(self.diff_richtextctrl, 15, wx.CENTER | wx.EXPAND)

    def add_file_header(self, file: Json):
        """
        Adds a file header to the diff rich text control based on the file type.

        Args:
            file (Json): A JSON object representing the file.

        Returns:
            None

        Raises:
            None

        Side Effects:
            - Modifies the text color of the diff rich text control based on the file type.
            - Writes the file header to the diff rich text control.
        """
        file_type = file["type"]
        if file_type == "Remove":
            self.diff_richtextctrl.BeginTextColour(wx.RED)
            self.diff_richtextctrl.WriteText(f"Removed: {file['file_removed']} \n")
        elif file_type == "Add":
            self.diff_richtextctrl.BeginTextColour(wx.GREEN)
            self.diff_richtextctrl.WriteText(f"Added: {file['file_added']} \n")
        elif file_type == "Rename":
            self.diff_richtextctrl.BeginTextColour(wx.BLUE)
            self.diff_richtextctrl.WriteText(
                f"Renamed: {file['from']} -> {file['to']} \n"
            )
        elif file_type == "Modified":
            self.diff_richtextctrl.BeginTextColour(wx.YELLOW)
            self.diff_richtextctrl.WriteText(f"Modified: {file['file_modified']}\n")
        self.diff_richtextctrl.EndTextColour()

    def add_hunk(self, hunk: Json):
        """
        Adds a hunk to the diff rich text control based on the provided JSON object.

        Parameters:
            hunk (Json): A JSON object representing the hunk.

        Returns:
            None

        Side Effects:
            - Modifies the text color of the diff rich text control based on the line type.
            - Writes the line numbers and values to the diff rich text control.
        """
        lines = hunk["lines"]

        for line in lines:
            line_type = line["type"]
            if line_type == "Add":
                self.diff_richtextctrl.BeginTextColour(wx.GREEN)
            elif line_type == "Remove":
                self.diff_richtextctrl.BeginTextColour(wx.RED)
            elif line_type == "Context":
                self.diff_richtextctrl.BeginTextColour(wx.WHITE)
            source_line_no: Optional[int] = line["source_line_no"]
            target_line_no: Optional[int] = line["target_line_no"]

            source_line_no_text = (
                line_number_padding * " "
                if not source_line_no
                else str(source_line_no).ljust(line_number_padding)
            )
            target_line_no_text = (
                line_number_padding * " "
                if not target_line_no
                else str(target_line_no).ljust(line_number_padding)
            )

            self.diff_richtextctrl.WriteText(
                source_line_no_text + "|" + target_line_no_text
            )
            self.diff_richtextctrl.WriteText(line["value"] + "\n")
            self.diff_richtextctrl.EndTextColour()

    def write_and_color_diff(self, diff: Json):
        """
        Write and color the diff to the diff rich text control.

        Parameters:
            diff (Json): A JSON object representing the diff.

        Returns:
            None

        Side Effects:
            - Clears the diff rich text control.
            - Writes the diff files to the diff rich text control.
            - Writes the diff hunks to the diff rich text control.
        """
        self.diff_richtextctrl.Clear()
        files: List[Json] = diff["diff"]
        for i, file in enumerate(files):
            if i != 0:
                self.diff_richtextctrl.WriteText(f"\n" * 5)

            self.add_file_header(file)

            hunks = file["hunks"]
            for i, hunk in enumerate(hunks):

                if i != 0:
                    self.diff_richtextctrl.BeginTextColour(wx.WHITE)
                    self.diff_richtextctrl.WriteText(f"{sep}\n\n")
                    self.diff_richtextctrl.EndTextColour()
                self.add_hunk(hunk)


sep = "-------------"
line_number_padding = 5
