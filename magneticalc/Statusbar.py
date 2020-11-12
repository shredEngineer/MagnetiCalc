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
from multiprocessing import cpu_count
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QCheckBox, QComboBox, QProgressBar, QLabel
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class Statusbar:
    """ Statusbar class. """

    def __init__(self, gui):
        """
        Initializes statusbar.

        @param gui: GUI
        """
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Start button
        self.start_button = QPushButton(qta.icon("fa.play-circle"), "", self.gui)
        self.start_button.setText(" ⟨F5⟩ ")
        self.start_button.setStyleSheet(f"padding: 3px; font-size: 13px;")
        self.start_button.clicked.connect(self.start)

        # Cancel button
        self.cancel_button = QPushButton(qta.icon("fa.stop-circle"), "", self.gui)
        self.cancel_button.setText("⟨ESC⟩")
        self.cancel_button.setStyleSheet(f"padding: 3px; font-size: 13px;")
        self.cancel_button.clicked.connect(self.cancel)

        # Auto-calculation checkbox
        self.auto_calculation_checkbox = QCheckBox("Auto-Calculation")
        self.auto_calculation_checkbox.stateChanged.connect(self._auto_calculation_changed)

        # Number-of-cores combobox
        self.cores_combobox = QComboBox()

        # "Auto" setting
        num_cores_auto = max(1, cpu_count() - 1)

        for i in range(0, cpu_count() + 1):
            if i == 0:
                self.cores_combobox.addItem(f"Auto ({num_cores_auto} Core" + ("s" if num_cores_auto > 1 else "") + ")")
            else:
                self.cores_combobox.addItem(f"{i} Core" + ("s" if i > 1 else ""))

        self.cores_combobox.currentIndexChanged.connect(
            lambda: self.gui.config.set_int("num_cores", self.cores_combobox.currentIndex())
        )

        # Progress bar
        self.progressbar = QProgressBar()

        # Status text
        self.label = QLabel()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Populate statusbar layout
        layout = QHBoxLayout()
        layout.addWidget(self.start_button, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
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

        container_widget = QWidget()
        container_widget.setLayout(layout)
        gui.statusBar().addPermanentWidget(container_widget, stretch=10)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        gui.statusBar().setSizeGripEnabled(False)

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the statusbar.
        """
        Debug(self, ".reinitialize()")

        self.gui.blockSignals(True)

        self.auto_calculation_checkbox.setChecked(self.gui.config.get_bool("auto_calculation"))
        if 0 > self.gui.config.get_int("num_cores") > cpu_count():
            self.gui.config.set_int("num_cores", 0)

        for i in range(0, cpu_count() + 1):
            if i == self.gui.config.get_int("num_cores"):
                self.cores_combobox.setCurrentIndex(i)

        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def _auto_calculation_changed(self):
        """
        Handles changed auto-calculation setting.
        """
        if self.gui.signalsBlocked():
            return

        self.gui.config.set_bool("auto_calculation", self.auto_calculation_checkbox.isChecked())
        if self.auto_calculation_checkbox.isChecked():
            if not self.gui.model.is_valid():
                self.gui.recalculate()

    # ------------------------------------------------------------------------------------------------------------------

    def arm(self):
        """
        "Arms" the statusbar before calculation.
        """
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.auto_calculation_checkbox.setEnabled(False)
        self.cores_combobox.setEnabled(False)
        self.progressbar.setValue(0)
        self.set_progressbar_color(Theme.PrimaryColor)

    def disarm(self, success: bool):
        """
        "Disarms" the statusbar after calculation.

        @param success: Reflects calculation success or failure
        """
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.auto_calculation_checkbox.setEnabled(True)
        self.cores_combobox.setEnabled(True)
        self.text("Ready." if success else "Canceled!")
        self.set_progressbar_color(Theme.SuccessColor if success else Theme.WarningColor)

        if success:
            self.progressbar.setValue(100)

    def start(self):
        """
        Starts the calculation.
        """
        self.gui.recalculate()
        self.disarm(True)

    def cancel(self):
        """
        Cancels the ongoing calculation.
        """
        self.gui.interrupt_calculation()
        self.disarm(False)

    def text(self, text: str):
        """
        Updates the statusbar text.

        @param text: Text
        """
        self.label.setText(text)

    def set_progressbar_color(self, color: str):
        """
        Sets the progressbar color & style.

        @param color: Color
        """
        self.progressbar.setStyleSheet(
            f"""
            QProgressBar
            {{
                border: 1px solid #888888;
                border-radius: 5px;
                color: #ffffff;
                text-align: center;
                padding: 0px;
                height: 23px;
                background-color: #111111;
                font-size: 13px;
            }}
            QProgressBar::chunk {{
                padding: 0px;
                background-color: {color};
                text-align: center;
            }}"""
        )
