""" Model module. """

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
from typing import Optional, Dict, Any, Callable
from sty import fg
from magneticalc.Debug import Debug
from magneticalc.Field_Types import field_type_to_str
from magneticalc.ModelAccess import ModelAccess

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.Field import Field
    from magneticalc.GUI import GUI
    from magneticalc.Metric import Metric
    from magneticalc.Parameters import Parameters
    from magneticalc.SamplingVolume import SamplingVolume
    from magneticalc.Wire import Wire


class Model:
    """
    Model class.

    The model maintains a strict hierarchy of dependencies:  parameters > metric > field > sampling volume > wire
    When a lower module's data changed, all higher modules are invalidated (i.e. have their calculation results reset).

    Note: The model maintains a cache for fields of different types, with at most one selected ("active") field.
    Property decorators maintain coherency between the selected field type and the contents of the field cache.
    The currently selected field is accessed using the L{field} property.
    Invalidating the currently selected field also invalidates all the other cached fields.
    """

    # Used by L{Debug}
    DebugColor = fg.yellow

    def __init__(self, gui: GUI) -> None:
        """
        Initializes the model.

        @param gui: GUI
        """
        Debug(self, ": Init")
        self.gui = gui

        self.wire = None                                    # Set in L{set_wire}            via L{Wire_Widget}
        self.sampling_volume = None                         # Set in L{set_sampling_volume} via L{SamplingVolume_Widget}

        self.metric = None                                  # Set in L{set_metric}          via L{Metric_Widget}
        self.parameters = None                              # Set in L{set_parameters}      via L{Parameters_Widget}

        # Field cache and currently selected field
        self._selected_field_type: Optional[int] = None     # Set in L{set_field}           via L{Field_Widget}
        self._field_cache: Dict[int, Field] = {}            # Set in L{set_field}           via L{Field_Widget}

    @property
    def field(self) -> Optional[Field]:
        """
        Returns the currently selected field if it is cached.

        @return: Field if cached, None otherwise
        """
        return self._field_cache.get(self._selected_field_type, None)

    @field.setter
    def field(self, field: Field) -> None:
        """
        Sets the currently selected field.

        @param field: Field
        """
        self._selected_field_type = field.get_type()
        self._field_cache[self._selected_field_type] = field

    def get_valid_field(self, field_type: int) -> Optional[Field]:
        """
        Gets a field if it is cached and valid.

        @param field_type: Field type
        @return: Field if cached and valid, None otherwise
        """
        field = self._field_cache.get(field_type, None)
        return (field if field.is_valid() else None) if field is not None else None

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def safe_valid(obj: Any) -> bool:
        """
        Safely checks the validity state of a possibly uninitialized object within the model.
        """
        return obj.is_valid() if obj is not None else False

    def __str__(self) -> str:
        """
        Returns the model validity state as a string.

        @return: String
        """
        name_obj_map = {
            "Wire": self.wire,
            "SamplingVolume": self.sampling_volume,
            "Field": self.field,
            "Metric": self.metric,
            "Parameters": self.parameters
        }
        return ", ".join([name for name, obj in name_obj_map.items() if self.safe_valid(obj)])

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self.safe_valid(self.wire) and \
            self.safe_valid(self.sampling_volume) and \
            self.safe_valid(self.field) and \
            self.safe_valid(self.metric) and \
            self.safe_valid(self.parameters)

    def invalidate(
            self,
            do_wire: bool = False,
            do_sampling_volume: bool = False,
            do_field: bool = False,
            do_metric: bool = False,
            do_parameters: bool = False
    ) -> None:
        """
        Invalidates multiple modules at once, in descending order of hierarchy.

        @param do_wire: Enable to invalidate wire
        @param do_sampling_volume: Enable to invalidate sampling volume
        @param do_field: Enable to invalidate all fields (the currently selected field and all the other cached fields)
        @param do_metric: Enable to invalidate metric
        @param do_parameters: Enable to invalidate parameters
        """
        Debug(self, ".invalidate()")

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
            did_field_invalidation = False
            for field_type, field in self._field_cache.items():
                if field.is_valid():
                    field.invalidate()
                    Debug(self, f".invalidate(): Invalidated {field_type_to_str(field_type)}")
                    did_field_invalidation = True
            if did_field_invalidation:
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
                    self.on_wire_invalid()

    def set_wire(self, wire: Wire, invalidate_self: bool) -> None:
        """
        Sets the wire.

        @param wire: Wire
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        Debug(self, ".set_wire()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_wire=invalidate_self,
                do_sampling_volume=True,
                do_field=True,
                do_metric=True,
                do_parameters=True
            )
            self.wire = wire

    def set_sampling_volume(self, sampling_volume: SamplingVolume, invalidate_self: bool) -> None:
        """
        Sets the sampling volume.

        @param sampling_volume: Sampling volume
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        Debug(self, ".set_sampling_volume()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_sampling_volume=invalidate_self,
                do_field=True,
                do_metric=True,
                do_parameters=True
            )
            self.sampling_volume = sampling_volume

    def set_field(self, field: Field, invalidate_self: bool) -> None:
        """
        Sets the field.

        @param field: Field
        @param invalidate_self: Enable to invalidate the old object (including the cache) before setting a new one
        """
        Debug(self, ".set_field()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_field=invalidate_self,
                do_metric=True,
                do_parameters=True
            )
            self.field = field

    def set_metric(self, metric: Metric, invalidate_self: bool) -> None:
        """
        Sets the metric.

        @param metric: Metric
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        Debug(self, ".set_metric()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_metric=invalidate_self,
                do_parameters=True
            )
            self.metric = metric

    def set_parameters(self, parameters: Parameters, invalidate_self: bool) -> None:
        """
        Sets the parameters.

        @param parameters: Parameters
        @param invalidate_self: Enable to invalidate the old object before setting a new one
        """
        Debug(self, ".set_parameters()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_parameters=invalidate_self
            )
            self.parameters = parameters

    # ------------------------------------------------------------------------------------------------------------------

    def calculate_wire(self, progress_callback: Callable) -> None:
        """
        Calculates the wire.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_wire()")

        self.invalidate(do_sampling_volume=True, do_field=True, do_metric=True)
        return self.wire.recalculate(progress_callback)

    def calculate_sampling_volume(self, progress_callback: Callable) -> bool:
        """
        Calculates the sampling volume.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".calculate_sampling_volume()")

        self.invalidate(do_field=True, do_metric=True)
        return self.sampling_volume.recalculate(progress_callback)

    def calculate_field(self, progress_callback: Callable, num_cores: int) -> bool:
        """
        Calculates the field.

        @param progress_callback: Progress callback
        @param num_cores: Number of CPU cores to use
        @return: True if successful, False if interrupted
        """
        Debug(self, f".calculate_field(num_cores={num_cores})")

        self.invalidate(do_metric=True)
        return self.field.recalculate(self.wire, self.sampling_volume, progress_callback, num_cores)

    def calculate_metric(self, progress_callback: Callable) -> bool:
        """
        Calculates the metric.

        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".calculate_metric()")

        return self.metric.recalculate(self.sampling_volume, self.field, progress_callback)

    def calculate_parameters(self, progress_callback: Callable) -> bool:
        """
        Calculates the parameters.

        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".calculate_parameters()")

        return self.parameters.recalculate(self.wire, self.sampling_volume, self.field, progress_callback)

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_valid(self) -> None:
        """
        Gets called when the wire was successfully calculated.
        """
        Debug(self, ".on_wire_valid()")

        self.gui.sidebar_left.wire_widget.update_labels()
        self.gui.menu.update_wire_menu()

    def on_sampling_volume_valid(self) -> None:
        """
        Gets called when the sampling volume was successfully calculated.
        """
        Debug(self, ".on_sampling_volume_valid()")

        self.gui.sidebar_left.sampling_volume_widget.update()
        self.gui.sidebar_right.display_widget.update()
        self.gui.sidebar_right.display_widget.prevent_excessive_field_labels(choice=False)

    def on_field_valid(self) -> None:
        """
        Gets called when the field was successfully calculated.
        """
        Debug(self, ".on_field_valid()")

        self.gui.sidebar_right.field_widget.update()

    def on_metric_valid(self) -> None:
        """
        Gets called when the metric was successfully calculated.
        """
        Debug(self, ".on_metric_valid()")

        self.gui.sidebar_right.metric_widget.update_labels()

        # The field labels are now created on-demand inside VispyCanvas.redraw()
        # self.gui.vispy_canvas.create_field_labels()

    def on_parameters_valid(self) -> None:
        """
        Gets called when the parameters were successfully calculated.
        """
        Debug(self, ".on_parameters_valid()")

        self.gui.sidebar_right.parameters_widget.update_labels()

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_invalid(self) -> None:
        """
        Gets called when the wire was invalidated.
        """
        Debug(self, ".on_wire_invalid()")

        self.gui.sidebar_left.wire_widget.update_labels()
        self.gui.menu.update_wire_menu()

    def on_sampling_volume_invalid(self) -> None:
        """
        Gets called when the sampling volume was invalidated.
        """
        Debug(self, ".on_sampling_volume_invalid()")

        self.gui.sidebar_left.sampling_volume_widget.update()

    def on_field_invalid(self) -> None:
        """
        Gets called when the field was invalidated.
        """
        Debug(self, ".on_field_invalid()")

        self.gui.sidebar_right.field_widget.update()

    def on_metric_invalid(self) -> None:
        """
        Gets called when the metric was invalidated.
        """
        Debug(self, ".on_metric_invalid()")

        self.gui.sidebar_right.metric_widget.update_labels()
        self.gui.vispy_canvas.delete_field_labels()

    def on_parameters_invalid(self) -> None:
        """
        Gets called when the parameters were invalidated.
        """
        Debug(self, ".on_parameters_invalid()")

        self.gui.sidebar_right.parameters_widget.update_labels()
