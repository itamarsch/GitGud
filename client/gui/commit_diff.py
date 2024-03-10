import wx


class CommitDiff(wx.Panel):
    def __init__(self, parent, diff: str):
        super().__init__(parent)

        return_button = wx.Button(self, label="Return")
        return_button.Bind(wx.EVT_BUTTON, lambda _: self.GetParent().pop_screen())

        diff_textctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Split the string into lines
        lines = diff.split("\n")

        # Iterate over the lines and set background color based on starting character
        for line in lines:
            if line.startswith("+"):
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.GREEN))
            elif line.startswith("-"):
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
            else:
                diff_textctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            diff_textctrl.AppendText(line + "\n")

        # Main Panel Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(return_button, 0, wx.CENTER | wx.EXPAND)

        main_sizer.Add(diff_textctrl, 15, wx.CENTER | wx.EXPAND)
        main_sizer.AddStretchSpacer(1)

        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        outer_sizer.AddStretchSpacer(1)

        outer_sizer.Add(main_sizer, 10, wx.CENTER | wx.EXPAND)

        outer_sizer.AddStretchSpacer(1)

        self.SetSizerAndFit(outer_sizer)
