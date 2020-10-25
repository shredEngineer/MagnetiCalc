""" Statusbar module. """

#  ISC License
#
#  Copyright (c) 2020, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QCheckBox, QComboBox, QProgressBar, QLabel
from multiprocessing import cpu_count


class Statusbar:
    """ Statusbar class. """

    def __init__(self, gui):
        """
        Initializes statusbar.

        @param gui: GUI
        """
        self.gui = gui

        # Cancel button
        self.cancel_button = QPushButton(qta.icon("fa.window-close"), "", self.gui)
        self.cancel_button.clicked.connect(self.cancel)

        # Auto-calculation checkbox
        self.auto_calculation_checkbox = QCheckBox("Auto-Calculation")
        self.auto_calculation_checkbox.setChecked(self.gui.config.get_bool("auto_calculation"))
        self.auto_calculation_checkbox.stateChanged.connect(self.auto_calculation_changed)

        # Number-of-cores combobox
        self.cores_combobox = QComboBox()

        # "Auto" setting
        num_cores_auto = max(1, cpu_count() - 1)

        if 0 > self.gui.config.get_int("num_cores") > cpu_count():
            self.gui.config.set_int("num_cores", 0)

        for i in range(0, cpu_count() + 1):
            if i == 0:
                self.cores_combobox.addItem(f"Auto ({num_cores_auto} Core" + ("s" if num_cores_auto > 1 else "") + ")")
            else:
                self.cores_combobox.addItem(f"{i} Core" + ("s" if i > 1 else ""))
            if i == self.gui.config.get_int("num_cores"):
                self.cores_combobox.setCurrentIndex(i)

        self.cores_combobox.currentIndexChanged.connect(
            lambda: self.gui.config.set_int("num_cores", self.cores_combobox.currentIndex())
        )

        # Progress bar
        self.progressbar = QProgressBar()

        # Status text
        self.label = QLabel()

        # Populate statusbar layout
        layout = QHBoxLayout()
        layout.addWidget(self.cancel_button, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self.auto_calculation_checkbox, alignment=Qt.AlignVCenter)
        layout.addSpacing(-4)
        layout.addWidget(self.cores_combobox, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self.progressbar, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self.label, alignment=Qt.AlignVCenter)
        layout.setContentsMargins(8, 2, 10, 2)

        # noinspection PyArgumentList
        container_widget = QWidget()
        container_widget.setLayout(layout)
        gui.statusBar().addPermanentWidget(container_widget, stretch=10)

        gui.statusBar().setSizeGripEnabled(False)

    def arm(self):
        """
        "Arms" the statusbar before calculation.
        """
        self.cancel_button.setEnabled(True)
        self.auto_calculation_checkbox.setEnabled(False)
        self.cores_combobox.setEnabled(False)
        self.progressbar.setValue(0)

    def disarm(self, success):
        """
        "Disarms" the statusbar after calculation.

        @param success: Reflects calculation success or failure
        """
        self.cancel_button.setEnabled(False)
        self.auto_calculation_checkbox.setEnabled(True)
        self.cores_combobox.setEnabled(True)
        self.text("Ready." if success else "Canceled!")

        if success:
            self.progressbar.setValue(100)

    def cancel(self):
        """
        Cancels the ongoing calculation.
        """
        self.gui.interrupt_calculation()
        self.disarm(False)

    def text(self, text):
        """
        Updates the statusbar text.

        @param text: Text
        """
        self.label.setText(text)

    def auto_calculation_changed(self):
        """
        Handles changed auto-calculation setting.
        """
        self.gui.config.set_bool("auto_calculation", self.auto_calculation_checkbox.isChecked())
        if self.auto_calculation_checkbox.isChecked():
            if not self.gui.model.is_valid():
                self.gui.recalculate()
