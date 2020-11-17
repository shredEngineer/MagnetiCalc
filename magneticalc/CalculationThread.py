""" CalculationThread module. """

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

from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import cpu_count


class CalculationThread(QThread):
    """
    CalculationThread class.
    The calculation thread implements an offloaded pipeline of subsequent calculation subtasks.
    The pipeline may be interrupted at (almost) any time, thereby exiting this thread.
    """

    # Progress update signal
    progress_update = pyqtSignal(int)

    def __init__(self, gui):
        """
        Initializes calculation thread.

        @param gui: GUI
        """
        QThread.__init__(self)

        self.gui = gui

        # Connect progress update signal and create callback
        self.progress_update.connect(lambda x: self.gui.statusbar.progressbar.setValue(x))
        self.progress_callback = self.progress_update.emit

    def run(self):
        """
        Thread main function.
        """

        if not self.gui.model.wire.is_valid():
            self.gui.calculation_status.emit("Calculating Wire Segments...")

            if not self.gui.model.calculate_wire(self.progress_callback):
                self.trigger_finished(False)
                return

            self.trigger_on_wire_valid()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.sampling_volume.is_valid():
            self.gui.calculation_status.emit("Calculating Sampling Volume...")

            label_resolution = self.gui.config.get_int("label_resolution")

            if not self.gui.model.calculate_sampling_volume(label_resolution, self.progress_callback):
                self.trigger_finished(False)
                return

            self.trigger_on_sampling_volume_valid()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.field.is_valid():
            self.gui.calculation_status.emit("Calculating Field...")

            num_cores = self.gui.config.get_int("num_cores")
            if num_cores == 0:
                # "Auto" setting
                num_cores = max(1, cpu_count() - 1)

            success = self.gui.model.calculate_field(self.progress_callback, num_cores)

            if not success:
                self.trigger_finished(False)
                return

            self.trigger_on_field_valid()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.metric.is_valid():
            self.gui.calculation_status.emit("Calculating Metric...")

            if not self.gui.model.calculate_metric(self.progress_callback):
                self.trigger_finished(False)
                return

            self.trigger_on_metric_valid()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if not self.gui.model.parameters.is_valid():
            self.gui.calculation_status.emit("Calculating Parameters...")

            if not self.gui.model.calculate_parameters(self.progress_callback):
                self.trigger_finished(False)
                return

            self.trigger_on_parameters_valid()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.trigger_finished(True)

    # ------------------------------------------------------------------------------------------------------------------

    def trigger_finished(self, success: bool):
        """
        Signals that the calculation finished.

        @param success: True if calculation was successful, False otherwise
        """

        # We cannot directly call this; we won't be able to modify the UI thread (which we'd really like to do somehow):
        # self.gui.calculation_stopped(success)

        # Instead, we use a signal; however, this results in slightly delayed execution, even after joining this thread;
        # the execution of  self.gui.on_calculation_exited()  will later be skipped when it sees another thread running.
        self.gui.calculation_exited.emit(success)

    # ------------------------------------------------------------------------------------------------------------------

    def trigger_on_wire_valid(self):
        """
        Gets called when the wire was successfully calculated.
        """
        self.gui.model.on_wire_valid()
        self.gui.vispy_canvas.redraw()

    def trigger_on_sampling_volume_valid(self):
        """
        Gets called when the sampling volume was successfully calculated.
        """
        self.gui.model.on_sampling_volume_valid()
        self.gui.vispy_canvas.redraw()

    def trigger_on_field_valid(self):
        """
        Gets called when the field was successfully calculated.
        """
        self.gui.model.on_field_valid()
        self.gui.vispy_canvas.redraw()

    def trigger_on_metric_valid(self):
        """
        Gets called when the metric was successfully calculated.
        """
        self.gui.model.on_metric_valid()
        self.gui.vispy_canvas.redraw()

    def trigger_on_parameters_valid(self):
        """
        Gets called when the parameters were successfully calculated.
        """
        self.gui.model.on_parameters_valid()
        self.gui.vispy_canvas.redraw()
