""" OverridePadding_Dialog module. """

#  ISC License
#
#  Copyright (c) 2020–2021, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

from __future__ import annotations
from magneticalc.QDialog2 import QDialog2
from magneticalc.QHBoxLayout2 import QHBoxLayout2
from magneticalc.QLabel2 import QLabel2
from magneticalc.QSpinBox2 import QSpinBox2
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class OverridePadding_Dialog(QDialog2):
    """ OverridePadding_Dialog class. """

    # Spinbox limits
    BoundsRange = [-1000, +1000]

    def __init__(self, gui: GUI) -> None:
        """
        Initializes "Override Padding" dialog.

        @param gui: GUI
        """
        QDialog2.__init__(self, title="Override Padding", width=420)
        Debug(self, ": Init")
        self.gui = gui

        self.addWidget(
            QLabel2("Please specify the sampling volume bounding box", bold=True, color=Theme.MainColor)
        )
        self.addSpacing(8)
        self.addLayout(QHBoxLayout2(QLabel2("Units:", expand=False), QLabel2("cm", bold=True)))
        self.addSpacing(16)

        bounding_box = self.gui.config.get_points("sampling_volume_bounding_box")
        # noinspection PyTypeChecker
        self.bounds_min_spinbox = [QSpinBox2(*self.BoundsRange, bounding_box[0][i], self.validate) for i in range(3)]
        # noinspection PyTypeChecker
        self.bounds_max_spinbox = [QSpinBox2(*self.BoundsRange, bounding_box[1][i], self.validate) for i in range(3)]

        for i in range(3):
            text = "  ≤  " + ["X", "Y", "Z"][i] + "  ≤  "
            self.addLayout(
                QHBoxLayout2(self.bounds_min_spinbox[i], QLabel2(text, expand=False), self.bounds_max_spinbox[i])
            )

        self.addSpacing(16)

        self.buttons = self.addButtons({
            "Cancel": ("fa.close", self.reject),
            "Apply": ("fa.save", self.accept),
        })
        self.buttons[1].setFocus()
        self.validate()

    def validate(self) -> None:
        """
        Validates the bounding box values and enables/disables the "Apply" button accordingly.
        """
        self.buttons["Apply"].setEnabled(
            all([self.bounds_min_spinbox[i].value() <= self.bounds_max_spinbox[i].value() for i in range(3)])
        )
