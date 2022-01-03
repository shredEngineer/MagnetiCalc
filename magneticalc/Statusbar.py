""" Statusbar module. """

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
from multiprocessing import cpu_count
from sty import fg
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QCheckBox, QComboBox, QProgressBar, QLabel
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Statusbar:
    """ Statusbar class. """

    # Used by L{Debug}
    DebugColor = fg.blue

    def __init__(self, gui: GUI) -> None:
        """
        Initializes statusbar.

        @param gui: GUI
        """
        Debug(self, ": Init")
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Start button
        self._start_button = QPushButton(qta.icon("fa.play-circle"), " ⟨F5⟩ ", self.gui)
        self._start_button.setStyleSheet(f"padding: 3px; font-size: 13px;")
        # noinspection PyUnresolvedReferences
        self._start_button.clicked.connect(self.start)

        # Cancel button
        self._cancel_button = QPushButton(qta.icon("fa.stop-circle"), "⟨ESC⟩", self.gui)
        self._cancel_button.setStyleSheet(f"padding: 3px; font-size: 13px;")
        # noinspection PyUnresolvedReferences
        self._cancel_button.clicked.connect(self.cancel)

        # Auto-calculation checkbox
        self._auto_calculation_checkbox = QCheckBox("Auto-Calculation")
        # noinspection PyUnresolvedReferences
        self._auto_calculation_checkbox.toggled.connect(self._auto_calculation_changed)

        # Number-of-cores combobox
        self._cores_combobox = QComboBox()

        # "Auto" setting
        num_cores_auto = max(1, cpu_count() - 1)

        for i in range(0, cpu_count() + 1):
            if i == 0:
                self._cores_combobox.addItem(f"Auto ({num_cores_auto} Core" + ("s" if num_cores_auto > 1 else "") + ")")
            else:
                self._cores_combobox.addItem(f"{i} Core" + ("s" if i > 1 else ""))

        # noinspection PyUnresolvedReferences
        self._cores_combobox.currentIndexChanged.connect(
            lambda: self.gui.config.set_int("num_cores", self._cores_combobox.currentIndex())
        )

        # Progress bar
        self._progressbar = QProgressBar()

        # Status text
        self._label = QLabel()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Populate statusbar layout
        layout = QHBoxLayout()
        layout.addWidget(self._start_button, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self._cancel_button, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self._auto_calculation_checkbox, alignment=Qt.AlignVCenter)
        layout.addSpacing(-4)
        layout.addWidget(self._cores_combobox, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self._progressbar, alignment=Qt.AlignVCenter)
        layout.addSpacing(4)
        layout.addWidget(self._label, alignment=Qt.AlignVCenter)
        layout.setContentsMargins(8, 2, 10, 2)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        gui.statusBar().addPermanentWidget(container_widget, stretch=10)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        gui.statusBar().setSizeGripEnabled(False)

        self.reinitialize()

    def reinitialize(self) -> None:
        """
        Re-initializes the statusbar.
        """
        Debug(self, ".reinitialize()")

        self.gui.blockSignals(True)

        self._auto_calculation_checkbox.setChecked(self.gui.config.get_bool("auto_calculation"))
        if 0 > self.gui.config.get_int("num_cores") > cpu_count():
            self.gui.config.set_int("num_cores", 0)

        for i in range(0, cpu_count() + 1):
            if i == self.gui.config.get_int("num_cores"):
                self._cores_combobox.setCurrentIndex(i)

        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def _auto_calculation_changed(self) -> None:
        """
        Handles changed auto-calculation setting.
        """
        if self.gui.signalsBlocked():
            return

        self.gui.config.set_bool("auto_calculation", self._auto_calculation_checkbox.isChecked())
        if self._auto_calculation_checkbox.isChecked():
            if not self.gui.model.is_valid():
                self.gui.recalculate()

    # ------------------------------------------------------------------------------------------------------------------

    def arm(self) -> None:
        """
        "Arms" the statusbar before calculation.
        """
        Debug(self, f".arm()")

        self._start_button.setEnabled(False)
        self._cancel_button.setEnabled(True)
        self._auto_calculation_checkbox.setEnabled(False)
        self._cores_combobox.setEnabled(False)
        self._progressbar.setValue(0)
        self.set_progressbar_color(Theme.MainColor)

    def disarm(self, success: bool) -> None:
        """
        "Disarms" the statusbar after calculation.

        @param success: Reflects calculation success or failure
        """
        Debug(self, f".disarm(success={success})")

        self._start_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._auto_calculation_checkbox.setEnabled(True)
        self._cores_combobox.setEnabled(True)
        self.set_text("Ready." if success else "Canceled!")
        self.set_progressbar_color(Theme.SuccessColor if success else Theme.FailureColor)

        if success:
            self._progressbar.setValue(100)

    def start(self) -> None:
        """
        Starts the calculation.
        """
        Debug(self, f".start()")

        self.gui.recalculate()
        self.disarm(True)

    def cancel(self) -> None:
        """
        Cancels the ongoing calculation.
        """
        Debug(self, f".cancel()")

        self.gui.interrupt_calculation()
        self.disarm(False)

    def set_text(self, text: str) -> None:
        """
        Updates the statusbar text.

        @param text: Text
        """
        Debug(self, f": {text}")

        self._label.setText(text)

    def set_progress(self, percentage: int) -> None:
        """
        Updates the progress percentage.

        @param percentage: Percentage
        """
        self._progressbar.setValue(percentage)

    def set_progressbar_color(self, color: str) -> None:
        """
        Sets the progressbar color & style.

        @param color: Color
        """
        self._progressbar.setStyleSheet(
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
