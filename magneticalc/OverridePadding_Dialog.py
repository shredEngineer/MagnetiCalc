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
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QLabel, QSizePolicy
from magneticalc.Theme import Theme


class OverridePadding_Dialog:
    """ OverridePadding_Dialog class. """

    # Window dimensions
    Width = 400

    # Spinbox limits
    BoundsMin = -1e+3
    BoundsMax = +1e+3

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

        title_label = QLabel("Please specify the sampling volume bounding box")
        title_label.setStyleSheet(f"font-weight: bold; color: {Theme.PrimaryColor}")
        layout.addWidget(title_label)

        layout.addSpacing(8)

        hint_layout = QHBoxLayout()
        units_label = QLabel("Units:")
        units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        hint_layout.addWidget(units_label)
        cm_label = QLabel("cm")
        cm_label.setStyleSheet(f"font-weight: bold;")
        hint_layout.addWidget(cm_label)
        layout.addLayout(hint_layout)
        
        layout.addSpacing(16)

        bounds_layout = [None, None, None]
        bounds_label = [None, None, None]
        self.bounds_min_spinbox = [None, None, None]
        self.bounds_max_spinbox = [None, None, None]

        bounding_box = self.gui.config.get_points("sampling_volume_bounding_box")

        for i in range(3):

            bounds_layout[i] = QHBoxLayout()

            self.bounds_min_spinbox[i] = QSpinBox(self.gui)
            self.bounds_min_spinbox[i].setMinimum(self.BoundsMin)
            self.bounds_min_spinbox[i].setMaximum(self.BoundsMax)
            self.bounds_min_spinbox[i].setValue(bounding_box[0][i])
            self.bounds_min_spinbox[i].valueChanged.connect(self.validate)
            bounds_layout[i].addWidget(self.bounds_min_spinbox[i], alignment=Qt.AlignVCenter)

            bounds_label[i] = QLabel("  ≤  " + ["X", "Y", "Z"][i] + "  ≤  ")
            bounds_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            bounds_layout[i].addWidget(bounds_label[i], alignment=Qt.AlignVCenter)

            self.bounds_max_spinbox[i] = QSpinBox(self.gui)
            self.bounds_max_spinbox[i].setMinimum(self.BoundsMin)
            self.bounds_max_spinbox[i].setMaximum(self.BoundsMax)
            self.bounds_max_spinbox[i].setValue(bounding_box[1][i])
            self.bounds_max_spinbox[i].valueChanged.connect(self.validate)
            bounds_layout[i].addWidget(self.bounds_max_spinbox[i], alignment=Qt.AlignVCenter)

            layout.addLayout(bounds_layout[i])

        layout.addSpacing(16)

        button_box = QHBoxLayout()

        cancel_button = QPushButton(
            Theme.get_icon(self.dialog, "SP_DialogCancelButton"),
            " Cancel"  # Leading space for alignment
        )
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(cancel_button, alignment=Qt.AlignBottom)

        self.apply_button = QPushButton(
            Theme.get_icon(self.dialog, "SP_DialogApplyButton"),
            " Apply"  # Leading space for alignment
        )
        self.apply_button.clicked.connect(self.accept)
        button_box.addWidget(self.apply_button, alignment=Qt.AlignBottom)

        layout.addLayout(button_box)

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
        valid = True
        for i in range(3):
            if self.bounds_min_spinbox[i].value() > self.bounds_max_spinbox[i].value():
                valid = False
                break

        self.apply_button.setEnabled(valid)
