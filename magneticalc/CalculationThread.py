""" CalculationThread module. """

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
from PyQt5.QtCore import QThread
from multiprocessing import cpu_count
from magneticalc.Debug import Debug


class CalculationThread(QThread):
    """
    CalculationThread class.
    The calculation thread implements an offloaded pipeline of subsequent calculation subtasks.
    The pipeline may be interrupted at (almost) any time, thereby exiting this thread.
    """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Initializes calculation thread.

        @param gui: GUI
        """
        QThread.__init__(self)
        Debug(self, ": Init", init=True)
        self.gui = gui

    def run(self) -> None:
        """
        Thread main function.
        """
        Debug(self, ".run()")

        if not self.gui.model.wire.valid:
            self.gui.calculation_status_signal.emit("Calculating Wire Segments … (1/5)")

            if not self.gui.model.calculate_wire(
                progress_callback=self.gui.calculation_progress_update_signal.emit
            ):
                self.gui.calculation_exited_signal.emit(False)
                return

            self.gui.wire_valid_changed_signal.emit(True)  # type: ignore

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.sampling_volume.valid:
            self.gui.calculation_status_signal.emit("Calculating Sampling Volume … (2/5)")

            if not self.gui.model.calculate_sampling_volume(
                    progress_callback=self.gui.calculation_progress_update_signal.emit
            ):
                self.gui.calculation_exited_signal.emit(False)
                return

            self.gui.sampling_volume_valid_changed_signal.emit(True)  # type: ignore

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.field.valid:
            self.gui.calculation_status_signal.emit("Calculating Field … (3/5)")

            num_cores = self.gui.project.get_int("num_cores")
            if num_cores == 0:
                # "Auto" setting
                num_cores = max(1, cpu_count() - 1)

            backend_type = self.gui.project.get_int("backend_type")

            if not self.gui.model.calculate_field(
                progress_callback=self.gui.calculation_progress_update_signal.emit,
                num_cores=num_cores,
                backend_type=backend_type
            ):
                self.gui.calculation_exited_signal.emit(False)
                return

            self.gui.field_valid_changed_signal.emit(True)  # type: ignore

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.metric.valid:
            self.gui.calculation_status_signal.emit("Calculating Metric … (4/5)")

            if not self.gui.model.calculate_metric(
                progress_callback=self.gui.calculation_progress_update_signal.emit,
            ):
                self.gui.calculation_exited_signal.emit(False)
                return

            self.gui.parameters_valid_changed_signal.emit(True)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.parameters.valid:
            self.gui.calculation_status_signal.emit("Calculating Parameters … (5/5)")

            if not self.gui.model.calculate_parameters(
                progress_callback=self.gui.calculation_progress_update_signal.emit,
            ):
                self.gui.calculation_exited_signal.emit(False)
                return

            self.gui.parameters_valid_changed_signal.emit(True)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.gui.calculation_exited_signal.emit(True)
