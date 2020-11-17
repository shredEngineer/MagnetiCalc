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
from magneticalc.Theme import Theme


class Model:
    """
    Model class.
    The model maintains a strict hierarchy of dependencies:  parameters > metric > field > sampling volume > wire
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
        self.parameters = None       # Will be initialized by Parameters_Widget

    def __str__(self) -> str:
        """
        Returns the model state as a string; may be used for debugging.

        @return: String
        """
        return \
            f"Wire           : {'VALID' if self.wire.is_valid() else '------'}\n" + \
            f"SamplingVolume : {'VALID' if self.sampling_volume.is_valid() else '------'}\n" + \
            f"Field          : {'VALID' if self.field.is_valid() else '------'}\n" + \
            f"Metric         : {'VALID' if self.metric.is_valid() else '------'}" + \
            f"Parameters     : {'VALID' if self.parameters.is_valid() else '------'}"

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self.wire.is_valid() and \
            self.sampling_volume.is_valid() and \
            self.field.is_valid() and \
            self.metric.is_valid() and \
            self.parameters.is_valid()

    def invalidate(
            self,
            do_wire: bool = False,
            do_sampling_volume: bool = False,
            do_field: bool = False,
            do_metric: bool = False,
            do_parameters: bool = False
    ):
        """
        Invalidates multiple modules at once, in descending order of hierarchy.

        @param do_wire: Enable to invalidate wire
        @param do_sampling_volume: Enable to invalidate sampling volume
        @param do_field: Enable to invalidate field
        @param do_metric: Enable to invalidate metric
        @param do_parameters: Enable to invalidate parameters
        """
        if do_parameters:
            if self.parameters is not None:
                if self.parameters.is_valid():
                    self.parameters.invalidate()
                    self.on_parameters_invalid()

        if do_metric:
            if self.metric is not None:
                if self.metric.is_valid():
                    self.metric.invalidate()
                    self.on_metric_invalid()

        if do_field:
            if self.field is not None:
                if self.field.is_valid():
                    self.field.invalidate()
                    self.on_field_invalid()

        if do_sampling_volume:
            if self.sampling_volume is not None:
                if self.sampling_volume.is_valid():
                    self.sampling_volume.invalidate()
                    self.on_sampling_volume_invalid()

        if do_wire:
            if self.wire is not None:
                if self.wire.is_valid():
                    self.wire.invalidate()
                    self.wire.on_wire_invalid()

    def set_wire(self, wire, invalidate_self: bool):
        """
        Sets the wire.

        @param wire: Wire
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        self.wire = wire
        self.invalidate(do_sampling_volume=True, do_field=True, do_metric=True, do_parameters=True)
        if invalidate_self:
            self.on_wire_invalid()

    def set_sampling_volume(self, sampling_volume, invalidate_self: bool):
        """
        Sets the sampling volume.

        @param sampling_volume: Sampling volume
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        self.sampling_volume = sampling_volume
        self.invalidate(do_field=True, do_metric=True, do_parameters=True)
        if invalidate_self:
            self.on_sampling_volume_invalid()

    def set_field(self, field, invalidate_self: bool):
        """
        Sets the field.

        @param field: Field
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        self.field = field
        self.invalidate(do_metric=True, do_parameters=True)
        if invalidate_self:
            self.on_field_invalid()

    def set_metric(self, metric, invalidate_self: bool):
        """
        Sets the metric.

        @param metric: Metric
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        self.metric = metric
        self.invalidate(do_parameters=True)
        if invalidate_self:
            self.on_metric_invalid()

    def set_parameters(self, parameters, invalidate_self: bool):
        """
        Sets the parameters.

        @param parameters: Parameters
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        self.parameters = parameters
        if invalidate_self:
            self.on_parameters_invalid()

    # ------------------------------------------------------------------------------------------------------------------

    def calculate_wire(self, progress_callback):
        """
        Calculates the wire.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_wire()", color=Theme.PrimaryColor)
        self.invalidate(do_sampling_volume=True, do_field=True, do_metric=True)
        return self.wire.recalculate(progress_callback)

    def calculate_sampling_volume(self, label_resolution, progress_callback):
        """
        Calculates the sampling volume.

        @param label_resolution: Label resolution
        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_sampling_volume()", color=Theme.PrimaryColor)
        self.invalidate(do_field=True, do_metric=True)
        return self.sampling_volume.recalculate(label_resolution, progress_callback)

    def calculate_field(self, progress_callback, num_cores: int):
        """
        Calculates the field.

        @param progress_callback: Progress callback
        @param num_cores: Number of CPU cores to use
        @return: True if successful, False if interrupted
        """
        Debug(self, f".calculate_field(num_cores={num_cores})", color=Theme.PrimaryColor)
        self.invalidate(do_metric=True)
        return self.field.recalculate(self.wire, self.sampling_volume, progress_callback, num_cores)

    def calculate_metric(self, progress_callback):
        """
        Calculates the metric.

        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".calculate_metric()", color=Theme.PrimaryColor)
        return self.metric.recalculate(self.sampling_volume, self.field, progress_callback)

    def calculate_parameters(self, progress_callback):
        """
        Calculates the parameters.

        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".calculate_parameters()", color=Theme.PrimaryColor)
        return self.parameters.recalculate(self.wire, self.sampling_volume, self.field, progress_callback)

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_valid(self):
        """
        Gets called when the wire was successfully calculated.
        """
        self.gui.sidebar_left.wire_widget.update_labels()

    def on_sampling_volume_valid(self):
        """
        Gets called when the sampling volume was successfully calculated.
        """
        self.gui.sidebar_left.sampling_volume_widget.update_labels()

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

        # The field labels are now created on-demand inside VispyCanvas.redraw()
        # self.gui.vispy_canvas.create_field_labels()

    def on_parameters_valid(self):
        """
        Gets called when the parameters were successfully calculated.
        """
        self.gui.sidebar_right.parameters_widget.update_labels()

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_invalid(self):
        """
        Gets called when the wire was invalidated.
        """
        self.gui.sidebar_left.wire_widget.update_labels()

    def on_sampling_volume_invalid(self):
        """
        Gets called when the sampling volume was invalidated.
        """
        self.gui.sidebar_left.sampling_volume_widget.update_labels()

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

    def on_parameters_invalid(self):
        """
        Gets called when the parameters were invalidated.
        """
        self.gui.sidebar_right.parameters_widget.update_labels()
