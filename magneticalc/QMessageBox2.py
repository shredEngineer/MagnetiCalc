""" QMessageBox2 module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from PyQt5.Qt import QSize
from PyQt5.QtWidgets import QMessageBox
from magneticalc.QDialog2 import QDialog2
from magneticalc.QIconLabel import QIconLabel
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class QMessageBox2(QDialog2):
    """ QMessageBox2 class. """

    def __init__(
            self,
            title: str,
            text: str,
            icon,
            buttons,
            default_button
    ) -> None:
        """
        Initializes a message box.

        @param title: Title
        @param text: Text
        @param icon: Icon
        @param buttons: Buttons
        @param default_button: Default button
        """
        QDialog2.__init__(self, title=title)
        Debug(self, ": Init", init=True)

        self.choice = 0

        # Map QMessageBox icon flag to QtAwesome icon ID and color
        icons_map = {
            QMessageBox.Information:    ("fa.info-circle", Theme.MainColor),
            QMessageBox.Question:       ("fa.question-circle", Theme.QuestionColor),
            QMessageBox.Warning:        ("fa.exclamation-circle", Theme.FailureColor),
        }
        icon_id, color = icons_map.get(icon, "")

        self.addSpacing(10)

        self.addLayout(
            QIconLabel(
                text=text,
                icon=icon_id,
                text_color=Theme.DialogTextColor,
                icon_color=color,
                icon_size=QSize(48, 48)
            )
        )

        self.addSpacing(15)

        # Map QMessageBox button flags to {Text: (Icon, Callback)} pairs as expected by L{QButtons}
        buttons_map = {
            QMessageBox.No      : {"No"     : ("fa.close", lambda: self.accepting(QMessageBox.No))},
            QMessageBox.Discard : {"Discard": ("fa.trash", lambda: self.accepting(QMessageBox.Discard))},
            QMessageBox.Cancel  : {"Cancel" : ("fa.close", lambda: self.accepting(QMessageBox.Cancel))},
            QMessageBox.Ok      : {"Ok"     : ("fa.check", lambda: self.accepting(QMessageBox.Ok))},
            QMessageBox.Save    : {"Save"   : ("fa.save", lambda: self.accepting(QMessageBox.Save))},
            QMessageBox.Yes     : {"Yes"    : ("fa.check", lambda: self.accepting(QMessageBox.Yes))},
        }

        index = 0
        default_button_index = None

        buttons_dict = {}
        for button_flag, button_dict in buttons_map.items():
            if button_flag & buttons:
                buttons_dict.update(button_dict)
                if button_flag == default_button:
                    default_button_index = index
                index += 1

        button_list = self.addButtons(buttons_dict)

        # Set default button
        for i, button in button_list.items():
            if i == default_button_index:
                button.setFocus()

        self.rejected.connect(  # type: ignore
            self.rejecting
        )

        self.show()

    def accepting(self, button_flag: int) -> None:
        """
        Sets the choice and accepts the dialog.
        """
        Debug(self, ".accepting()", success=True)
        self.choice = button_flag
        self.accept()

    def rejecting(self) -> None:
        """
        Gets called when the user hits the ESC key.
        """
        Debug(self, ".rejecting()", warning=True)
