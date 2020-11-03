""" Model module. """

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

from magneticalc.Debug import Debug


class Model:
    """
    Model class.
    The model maintains a strict hierarchy of dependencies:  metric > field > sampling volume > wire
    When a lower module's data changed, all higher modules are invalidated (i.e. have their calculation results reset).
    """

    def __init__(self, gui):
        """
        Initializes the model.

        @param gui: GUI
        """
        Debug(self, ": Init")

        self.gui = gui

        self.wire = None             # Will be initialized by Wire_Widget
        self.sampling_volume = None  # Will be initialized by SamplingVolume_Widget
        self.field = None            # Will be initialized by Field_Widget
        self.metric = None           # Will be initialized by Metric_Widget

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self.wire.is_valid() and \
            self.sampling_volume.is_valid() and \
            self.field.is_valid() and \
            self.metric.is_valid()

    def invalidate(self, do_wire=False, do_sampling_volume=False, do_field=False, do_metric=False):
        """
        Invalidates multiple modules at once.

        @param do_wire: Enable to invalidate wire
        @param do_sampling_volume: Enable to invalidate sampling volume
        @param do_field: Enable to invalidate field
        @param do_metric: Enable to invalidate metric
        """
        if do_wire:
            if self.wire is not None:
                if self.wire.is_valid():
                    self.wire.invalidate()
                    self.wire.on_wire_invalid()

        if do_sampling_volume:
            if self.sampling_volume is not None:
                if self.sampling_volume.is_valid():
                    self.sampling_volume.invalidate()
                    self.on_sampling_volume_invalid()

        if do_field:
            if self.field is not None:
                if self.field.is_valid():
                    self.field.invalidate()
                    self.on_field_invalid()

        if do_metric:
            if self.metric is not None:
                if self.metric.is_valid():
                    self.metric.invalidate()
                    self.on_metric_invalid()

    def set_wire(self, wire):
        """
        Sets the wire.

        @param wire: Wire
        """
        self.wire = wire
        self.invalidate(do_sampling_volume=True, do_field=True, do_metric=True)

    def set_sampling_volume(self, sampling_volume):
        """
        Sets the sampling volume.

        @param sampling_volume: Sampling volume
        """
        self.sampling_volume = sampling_volume
        self.invalidate(do_field=True, do_metric=True)

    def set_field(self, field):
        """
        Sets the field.

        @param field: Field
        """
        self.field = field
        self.invalidate(do_metric=True)

    def set_metric(self, metric):
        """
        Sets the metric.

        @param metric: Metric
        """
        self.metric = metric

    # ------------------------------------------------------------------------------------------------------------------

    def calculate_wire(self, progress_callback):
        """
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_wire()", color=(0, 0, 255))
        self.invalidate(do_sampling_volume=True, do_field=True, do_metric=True)
        return self.wire.recalculate(progress_callback)

    def calculate_sampling_volume(self, progress_callback):
        """
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_sampling_volume()", color=(0, 0, 255))
        self.invalidate(do_field=True, do_metric=True)
        return self.sampling_volume.recalculate(progress_callback)

    def calculate_field(self, progress_callback, num_cores):
        """
        @return: True if successful, False if interrupted
        """
        Debug(self, f".calculate_field(num_cores={num_cores})", color=(0, 0, 255))
        self.invalidate(do_metric=True)
        return self.field.recalculate(self.wire, self.sampling_volume, progress_callback, num_cores)

    def calculate_metric(self, progress_callback):
        """
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_metric()", color=(0, 0, 255))
        return self.metric.recalculate(self.wire, self.sampling_volume, self.field, progress_callback)

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_valid(self):
        """
        Gets called when the wire was successfully calculated.
        """
        self.gui.sidebar_left.wire_widget.update_sliced_total_label()

    def on_sampling_volume_valid(self):
        """
        Gets called when the sampling volume was successfully calculated.
        """
        self.gui.sidebar_left.sampling_volume_widget.update_total_label()

    def on_field_valid(self):
        """
        Gets called when the field was successfully calculated.
        """
        self.gui.sidebar_right.field_widget.update_labels()

    def on_metric_valid(self):
        """
        Gets called when the metric was successfully calculated.
        """
        self.gui.sidebar_right.metric_widget.update_labels()
        self.gui.vispy_canvas.create_field_labels()

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_invalid(self):
        """
        Gets called when the wire was invalidated.
        """
        self.gui.sidebar_left.wire_widget.update_sliced_total_label()

    def on_sampling_volume_invalid(self):
        """
        Gets called when the sampling volume was invalidated.
        """
        self.gui.sidebar_left.sampling_volume_widget.update_total_label()

    def on_field_invalid(self):
        """
        Gets called when the field was invalidated.
        """
        self.gui.sidebar_right.field_widget.update_labels()

    def on_metric_invalid(self):
        """
        Gets called when the metric was invalidated.
        """
        self.gui.sidebar_right.metric_widget.update_labels()
        self.gui.vispy_canvas.delete_field_labels()
