from typing import List
from typing_extensions import override
from base_screen import BaseScreen
import wx


class CodeBlock(wx.StaticText):
    def __init__(self, parent, label):
        super().__init__(parent, label=label, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font = wx.Font(
            16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        self.SetFont(font)
        self.SetBackgroundColour(
            wx.Colour(240, 240, 240)
        )  # Setting background color to light gray
        self.SetForegroundColour(wx.Colour(0, 0, 0))


class SSHHelp(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, 3, 3, title="SSH Help")

    def text_explanation(self, text: str) -> List[wx.StaticText]:
        font = wx.Font(
            20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        lines = text.splitlines()
        texts = []
        for line in lines:
            static_text = wx.StaticText(self, label=f"{line}")
            static_text.SetFont(font)
            texts.append(static_text)
        return texts

    @override
    def add_children(self, main_sizer: wx.BoxSizer):

        intorduction = "To communicate with the git server you need to create an ssh key.\nThis guide will explain how to create one."
        intorduction_text = self.text_explanation(intorduction)

        ssh_keygen_intoduction = (
            "To create an ssh key open Git bash and run the following command:"
        )

        ssh_keygen_introduction_text = self.text_explanation(ssh_keygen_intoduction)

        ssh_keygen_command = "ssh-keygen"
        ssh_keygen_command_text = CodeBlock(self, f"{ssh_keygen_command}")

        ssh_keygen_explanation = "This command will firstly ask which directory you want to store the ssh key in. The default is ~/.ssh an is what this example uses.\nAfterwards it will ask for a passphrase to protect the key.\nYou can leave the passphrase blank if you don't want to enter a passphrase on each push/clone/pull."

        ssh_keygen_explanation_text = self.text_explanation(ssh_keygen_explanation)

        copy_ssh_key_explanation = "To copy the *public* key that the application will store run the following command:"
        copy_ssh_key_text = self.text_explanation(copy_ssh_key_explanation)

        copy_ssh_key_command = "cat ~/.ssh/id_ed25519.pub | clip"
        copy_ssh_key_command_text = CodeBlock(self, f"{copy_ssh_key_command}")

        paste_ssh_key_explanation = "After you have copied the key you can paste it in the SSH key field in the previous screen."
        paste_ssh_key_text = self.text_explanation(paste_ssh_key_explanation)

        for line in intorduction_text:
            main_sizer.Add(line, 0, wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddStretchSpacer(2)

        for line in ssh_keygen_introduction_text:
            main_sizer.Add(line, 0, wx.ALIGN_CENTER_HORIZONTAL)

        main_sizer.Add(ssh_keygen_command_text, 0, wx.ALIGN_CENTER_HORIZONTAL)

        for line in ssh_keygen_explanation_text:
            main_sizer.Add(line, 0, wx.ALIGN_CENTER_HORIZONTAL)

        main_sizer.AddStretchSpacer(2)
        for line in copy_ssh_key_text:
            main_sizer.Add(line, 0, wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.Add(copy_ssh_key_command_text, 0, wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddStretchSpacer(2)

        for line in paste_ssh_key_text:
            main_sizer.Add(line, 0, wx.ALIGN_CENTER_HORIZONTAL)
