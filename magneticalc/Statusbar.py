""" Statusbar module. """

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

from __future__ import annotations
from typing import Optional
from multiprocessing import cpu_count
from sty import fg
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QComboBox, QProgressBar, QLabel
from magneticalc.QPushButton2 import QPushButton2
from magneticalc.Config import get_jit_enabled
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class Statusbar:
    """ Statusbar class. """

    # Used by L{Debug}
    DebugColor = fg.blue

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Initializes statusbar.

        @param gui: GUI
        """
        Debug(self, ": Init", init=True)
        self.gui = gui

        self._valid = True  # Note: Needs to be true initially, otherwise the first L{invalidate()} would have no effect
        self._canceled = False

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Start button
        self._start_button = QPushButton2(" ⟨F5⟩ ", "fa.play-circle", self.start, css="padding: 3px; font-size: 13px;")

        # Cancel button
        self._cancel_button = QPushButton2("⟨ESC⟩", "fa.stop-circle", self.cancel, css="padding: 3px; font-size: 13px;")

        # Auto-calculation checkbox
        self._auto_calculation_checkbox = QCheckBox("Auto-Calculation")
        self._auto_calculation_checkbox.toggled.connect(self._auto_calculation_changed)  # type: ignore

        # Number-of-cores combobox
        self._cores_combobox = QComboBox()

        if get_jit_enabled():

            # "Auto" setting
            num_cores_auto = max(1, cpu_count() - 1)

            for i in range(0, cpu_count() + 1):
                if i == 0:
                    self._cores_combobox.addItem(
                        f"Auto ({num_cores_auto} Core" + ("s" if num_cores_auto > 1 else "") + ")"
                    )
                else:
                    self._cores_combobox.addItem(f"{i} Core" + ("s" if i > 1 else ""))

            self._cores_combobox.currentIndexChanged.connect(  # type: ignore
                lambda: self.gui.config.set_int("num_cores", self._cores_combobox.currentIndex())
            )

        else:

            self._cores_combobox.addItem("JIT Disabled")
            self._cores_combobox.setEnabled(False)

        # Progress bar
        self._progressbar = QProgressBar()

        # Status text
        self._label = QLabel()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Populate statusbar layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self._start_button)
        self.layout.addSpacing(4)
        self.layout.addWidget(self._cancel_button)
        self.layout.addSpacing(4)
        self.layout.addWidget(self._auto_calculation_checkbox)
        self.layout.addSpacing(-4)
        self.layout.addWidget(self._cores_combobox)
        self.layout.addSpacing(4)
        self.layout.addWidget(self._progressbar)
        self.layout.addSpacing(4)
        self.layout.addWidget(self._label)
        self.layout.setContentsMargins(8, 2, 10, 2)

        container_widget = QWidget()
        container_widget.setLayout(self.layout)
        gui.statusBar().addPermanentWidget(container_widget, stretch=10)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        gui.statusBar().setSizeGripEnabled(False)

    def reload(self) -> None:
        """
        Reloads the statusbar.
        """
        Debug(self, ".reload()", refresh=True)

        self.gui.blockSignals(True)

        self._auto_calculation_checkbox.setChecked(self.gui.config.get_bool("auto_calculation"))
        if 0 > self.gui.config.get_int("num_cores") > cpu_count():
            self.gui.config.set_int("num_cores", 0)

        if get_jit_enabled():
            for i in range(0, cpu_count() + 1):
                if i == self.gui.config.get_int("num_cores"):
                    self._cores_combobox.setCurrentIndex(i)

        self.gui.blockSignals(False)

        self.invalidate()

    # ------------------------------------------------------------------------------------------------------------------

    def _auto_calculation_changed(self) -> None:
        """
        Handles changed auto-calculation setting.
        """
        if self.gui.signalsBlocked():
            return

        self._canceled = False

        self.gui.config.set_bool("auto_calculation", self._auto_calculation_checkbox.isChecked())
        if self._auto_calculation_checkbox.isChecked():
            if not self.gui.model.valid:
                self.gui.recalculate()

    # ------------------------------------------------------------------------------------------------------------------

    def arm(self) -> None:
        """
        "Arms" the statusbar before calculation.
        """
        Debug(self, f".arm()")

        self._valid = False
        self._canceled = False

        self._start_button.setEnabled(False)
        self._cancel_button.setEnabled(True)
        self._auto_calculation_checkbox.setEnabled(False)

        if get_jit_enabled():
            self._cores_combobox.setEnabled(False)

        self._progressbar.setValue(0)
        self.set_progressbar_color(fg_color=Theme.MainColor)

    def disarm(self, success: bool) -> None:
        """
        "Disarms" the statusbar after calculation.

        @param success: Reflects calculation success or failure
        """
        Debug(self, f".disarm(success={success})")

        self._valid = success
        self._canceled = not success

        self._start_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._auto_calculation_checkbox.setEnabled(True)

        if get_jit_enabled():
            self._cores_combobox.setEnabled(True)

        self.set_text("Complete." if success else "Canceled!")
        self.set_progressbar_color(fg_color=Theme.SuccessColor if success else Theme.FailureColor)

        if success:
            self._progressbar.setValue(100)

    def invalidate(self) -> None:
        """
        "Invalidates" the statusbar.
        """

        # Don't invalidate more than once
        if not self._valid:
            return

        # Don't invalidate after cancellation
        if self._canceled:
            self._canceled = False
            return

        Debug(self, ".invalidate()")

        self._valid = False

        self._start_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._auto_calculation_checkbox.setEnabled(True)

        if get_jit_enabled():
            self._cores_combobox.setEnabled(True)

        self.set_text("Pending Calculation")
        self.set_progressbar_color(fg_color=Theme.LiteColor, bg_color=Theme.LiteColor)
        self._progressbar.setValue(0)

    def start(self) -> None:
        """
        Starts the calculation.
        """
        Debug(self, ".start()")

        self.gui.recalculate()
        self.disarm(True)

    def cancel(self) -> None:
        """
        Cancels the ongoing calculation.
        """
        Debug(self, ".cancel()")

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

    def set_progressbar_color(self, fg_color: str, bg_color: Optional[str] = None) -> None:
        """
        Sets the progressbar color & style.

        @param fg_color: Foreground color
        @param bg_color: Background color (optional)
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
                background-color: {bg_color if bg_color is not None else "#000000"};
                font-size: 13px;
            }}
            QProgressBar::chunk {{
                padding: 0px;
                background-color: {fg_color};
                text-align: center;
            }}"""
        )
