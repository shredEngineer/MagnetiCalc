""" CalculationThread module. """

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
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import cpu_count
from magneticalc.Debug import Debug
from magneticalc.ModelAccess import ModelAccess

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class CalculationThread(QThread):
    """
    CalculationThread class.
    The calculation thread implements an offloaded pipeline of subsequent calculation subtasks.
    The pipeline may be interrupted at (almost) any time, thereby exiting this thread.
    """

    # Progress update signal
    _progress_update = pyqtSignal(int)

    # Valid state signals
    _wire_valid = pyqtSignal()
    _sampling_volume_valid = pyqtSignal()
    _field_valid = pyqtSignal()
    _metric_valid = pyqtSignal()
    _parameters_valid = pyqtSignal()

    def __init__(self, gui: GUI) -> None:
        """
        Initializes calculation thread.

        @param gui: GUI
        """
        QThread.__init__(self)
        Debug(self, ": Init")
        self.gui = gui

        # Connect progress update signal and create callback:

        # noinspection PyUnresolvedReferences
        self._progress_update.connect(lambda x: self.gui.statusbar.set_progress(x))
        # noinspection PyUnresolvedReferences
        self.progress_callback = self._progress_update.emit

        # Connect valid state signals to corresponding handlers:

        # noinspection PyUnresolvedReferences
        self._wire_valid.connect(self.on_wire_valid)
        # noinspection PyUnresolvedReferences
        self._sampling_volume_valid.connect(self.on_sampling_volume_valid)
        # noinspection PyUnresolvedReferences
        self._field_valid.connect(self.on_field_valid)
        # noinspection PyUnresolvedReferences
        self._metric_valid.connect(self.on_metric_valid)
        # noinspection PyUnresolvedReferences
        self._parameters_valid.connect(self.on_parameters_valid)

    def run(self) -> None:
        """
        Thread main function.
        """
        Debug(self, ".run()")

        with ModelAccess(self.gui, recalculate=False):

            if not self.gui.model.wire.is_valid():
                self.gui.calculation_status.emit("Calculating Wire Segments...")

                if not self.gui.model.calculate_wire(self.progress_callback):
                    self.on_finished(False)
                    return

                # noinspection PyUnresolvedReferences
                self._wire_valid.emit()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not self.gui.model.sampling_volume.is_valid():
                self.gui.calculation_status.emit("Calculating Sampling Volume...")

                if not self.gui.model.calculate_sampling_volume(self.progress_callback):
                    self.on_finished(False)
                    return

                # noinspection PyUnresolvedReferences
                self._sampling_volume_valid.emit()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not self.gui.model.field.is_valid():
                self.gui.calculation_status.emit("Calculating Field...")

                num_cores = self.gui.config.get_int("num_cores")
                if num_cores == 0:
                    # "Auto" setting
                    num_cores = max(1, cpu_count() - 1)

                success = self.gui.model.calculate_field(self.progress_callback, num_cores)

                if not success:
                    self.on_finished(False)
                    return

                # noinspection PyUnresolvedReferences
                self._field_valid.emit()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not self.gui.model.metric.is_valid():
                self.gui.calculation_status.emit("Calculating Metric...")

                if not self.gui.model.calculate_metric(self.progress_callback):
                    self.on_finished(False)
                    return

                # noinspection PyUnresolvedReferences
                self._metric_valid.emit()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not self.gui.model.parameters.is_valid():
                self.gui.calculation_status.emit("Calculating Parameters...")

                if not self.gui.model.calculate_parameters(self.progress_callback):
                    self.on_finished(False)
                    return

                # noinspection PyUnresolvedReferences
                self._parameters_valid.emit()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.on_finished(True)

    # ------------------------------------------------------------------------------------------------------------------

    def on_finished(self, success: bool) -> None:
        """
        Signals that the calculation finished.

        @param success: True if calculation was successful, False otherwise
        """
        Debug(self, f".on_finished(success={success})")

        # We cannot directly call this; we won't be able to modify the UI thread (which we'd really like to do somehow):
        # self.gui.calculation_stopped(success)

        # Instead, we use a signal; however, this results in slightly delayed execution, even after joining this thread;
        # the execution of  self.gui.on_calculation_exited()  will later be skipped when it sees another thread running.
        self.gui.calculation_exited.emit(success)

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_valid(self) -> None:
        """
        Gets called when the wire was successfully calculated.
        """
        Debug(self, ".on_wire_valid()")
        self.gui.model.on_wire_valid()
        self.gui.vispy_canvas.redraw()

    def on_sampling_volume_valid(self) -> None:
        """
        Gets called when the sampling volume was successfully calculated.
        """
        Debug(self, ".on_sampling_volume_valid()")
        self.gui.model.on_sampling_volume_valid()
        self.gui.vispy_canvas.redraw()

    def on_field_valid(self) -> None:
        """
        Gets called when the field was successfully calculated.
        """
        Debug(self, ".on_field_valid()")
        self.gui.model.on_field_valid()
        self.gui.vispy_canvas.redraw()

    def on_metric_valid(self) -> None:
        """
        Gets called when the metric was successfully calculated.
        """
        Debug(self, ".on_metric_valid()")
        self.gui.model.on_metric_valid()
        self.gui.vispy_canvas.redraw()

    def on_parameters_valid(self) -> None:
        """
        Gets called when the parameters were successfully calculated.
        """
        Debug(self, ".on_parameters_valid()")
        self.gui.model.on_parameters_valid()
        self.gui.vispy_canvas.redraw()
