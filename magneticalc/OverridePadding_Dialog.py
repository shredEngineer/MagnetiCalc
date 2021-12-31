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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from magneticalc.QtWidgets2 import QSpinBox2, QLabel2, QHBoxLayout2, QPushButton2
from magneticalc.Theme import Theme


class OverridePadding_Dialog:
    """ OverridePadding_Dialog class. """

    # Window dimensions
    Width = 420

    # Spinbox limits
    BoundsRange = [-1000, +1000]

    def __init__(self, gui) -> None:
        """
        Prepares the 'Override Padding' dialog.

        @param gui: GUI
        """
        self.gui = gui

        self.success = None

        self.dialog = QDialog()
        self.dialog.setWindowTitle("Override Padding")

        layout = QVBoxLayout()
        self.dialog.setMinimumWidth(self.Width)
        self.dialog.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        layout.addWidget(
            QLabel2("Please specify the sampling volume bounding box", bold=True, color=Theme.PrimaryColor)
        )

        layout.addSpacing(8)
        layout.addLayout(QHBoxLayout2(QLabel2("Units:", fixed=True), QLabel2("cm", bold=True)))
        layout.addSpacing(16)

        bounding_box = self.gui.config.get_points("sampling_volume_bounding_box")
        self.bounds_min_spinbox = [QSpinBox2(*self.BoundsRange, bounding_box[0][i], self.validate) for i in range(3)]
        self.bounds_max_spinbox = [QSpinBox2(*self.BoundsRange, bounding_box[1][i], self.validate) for i in range(3)]

        for i in range(3):
            text = "  ≤  " + ["X", "Y", "Z"][i] + "  ≤  "
            layout.addLayout(QHBoxLayout2(self.bounds_min_spinbox[i], QLabel2(text), self.bounds_max_spinbox[i]))

        layout.addSpacing(16)

        self.apply_button = QPushButton2(self.dialog, "SP_DialogApplyButton", " Apply", self.accept)
        layout.addLayout(
            QHBoxLayout2(
                QPushButton2(self.dialog, "SP_DialogCancelButton", " Cancel", self.reject),
                self.apply_button
            )
        )

        self.apply_button.setFocus()
        self.validate()

    # ------------------------------------------------------------------------------------------------------------------

    def show(self) -> None:
        """
        Shows this dialog.
        """
        self.success = self.dialog.exec() == 1

    def reject(self) -> None:
        """
        User chose to abort.
        """
        self.dialog.reject()

    def accept(self) -> None:
        """
        User chose to resume.
        """
        self.dialog.accept()

    # ------------------------------------------------------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validates the bounding box values and enables/disables the "Apply" button accordingly.
        """
        valid = all([self.bounds_min_spinbox[i].value() <= self.bounds_max_spinbox[i].value() for i in range(3)])
        self.apply_button.setEnabled(valid)
