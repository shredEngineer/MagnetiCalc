""" Model module. """

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
from typing import Optional, Dict, Callable
from sty import fg
from magneticalc.Debug import Debug
from magneticalc.Field import Field
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.Metric import Metric
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Parameters import Parameters
from magneticalc.SamplingVolume import SamplingVolume
from magneticalc.Wire import Wire


class Model:
    """
    Model class.

    The model maintains a strict hierarchy of dependencies:  parameters > metric > field > sampling volume > wire
    When a lower module's data changed, all higher modules are invalidated (i.e. have their calculation results reset).
    """

    # Used by L{Debug}
    DebugColor = fg.yellow

    """ Enable to debug calls to L{invalidate()}. """
    DebugInvalidate = False

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Initializes the model.

        @param gui: GUI
        """
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.wire = Wire()
        self.sampling_volume = SamplingVolume()
        self.metric = Metric()
        self.parameters = Parameters()

        self._field_type_select: int = A_FIELD
        self._field_cache: Dict[int, Field] = {
            A_FIELD: Field(),
            B_FIELD: Field(),
        }

    @property
    def field_type_select(self) -> int:
        """
        @return: Currently selected field type
        """
        return self._field_type_select

    @field_type_select.setter
    def field_type_select(self, field_type: int) -> None:
        """
        Sets the currently selected field type.

        @param field_type: Field type
        """
        Debug(self, f".field_type_select = {field_type}")
        self._field_type_select = field_type

    @property
    def field(self) -> Field:
        """
        @return: Currently selected field
        """
        return self._field_cache[self.field_type_select]

    def get_valid_field(self, field_type: int) -> Optional[Field]:
        """
        Gets a field by type if the field is valid.

        @param field_type: Field type
        @return: Field if valid, None otherwise
        """
        field = self._field_cache[field_type]
        return field if field.valid else None

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def valid(self) -> bool:
        """
        @return: True if model is valid, False otherwise
        """
        return \
            self.wire.valid and \
            self.sampling_volume.valid and \
            self.field.valid and \
            self.metric.valid and \
            self.parameters.valid

    def invalidate(
            self,
            do_wire: bool = False,
            do_sampling_volume: bool = False,
            do_field: bool = False,
            do_metric: bool = False,
            do_parameters: bool = False,
            do_all: bool = False
    ) -> None:
        """
        Invalidates multiple hierarchy levels at once, in descending order of hierarchy.

        @param do_wire: Enable to invalidate wire
        @param do_sampling_volume: Enable to invalidate sampling volume
        @param do_field: Enable to invalidate all fields
        @param do_metric: Enable to invalidate metric
        @param do_parameters: Enable to invalidate parameters
        @param do_all: Enable to invalidate all hierarchy levels
        """
        if self.DebugInvalidate:
            subject = {
                "wire": do_wire,
                "sampling_volume": do_sampling_volume,
                "field": do_field,
                "metric": do_metric,
                "parameters": do_parameters,
                "all": do_all
            }
            string = ", ".join([name for name, condition in subject.items() if condition])
            Debug(self, f".invalidate({string})")

        if do_all or do_parameters:
            if self.parameters.valid:
                self.parameters.valid = False
                self.on_parameters_invalid()

        if do_all or do_metric:
            if self.metric.valid:
                self.metric.valid = False
                self.on_metric_invalid()

        if do_all or do_field:
            valid_fields = [field for field_type, field in self._field_cache.items() if field.valid]
            if any(valid_fields):
                for field in valid_fields:
                    field.valid = False
                self.on_field_invalid()

        if do_all or do_sampling_volume:
            if self.sampling_volume.valid:
                self.sampling_volume.valid = False
                self.on_sampling_volume_invalid()

        if do_all or do_wire:
            if self.wire.valid:
                self.wire.valid = False
                self.on_wire_invalid()

    def set_wire(
            self,
            invalidate: bool,
            *args,
            **kwargs
    ) -> None:
        """
        Sets the wire.

        @param invalidate: Enable to invalidate this model hierarchy level
        """
        Debug(self, ".set_wire()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_wire=invalidate,
                do_sampling_volume=True,
                do_field=True,
                do_metric=True,
                do_parameters=True
            )
            self.wire.set(*args, **kwargs)

    def set_sampling_volume(
            self,
            invalidate: bool,
            *args,
            **kwargs
    ) -> None:
        """
        Sets the sampling volume.

        @param invalidate: Enable to invalidate this model hierarchy level
        """
        Debug(self, ".set_sampling_volume()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_sampling_volume=invalidate,
                do_field=True,
                do_metric=True,
                do_parameters=True
            )
            self.sampling_volume.set(*args, **kwargs)

    def set_field(
            self,
            invalidate: bool,
            field_type: int,
            *args,
            **kwargs
    ) -> None:
        """
        Sets the field.

        @param invalidate: Enable to invalidate this model hierarchy level
        @param field_type: Field type
        """
        Debug(self, ".set_field()")

        with ModelAccess(self.gui, recalculate=False):

            self.field_type_select = field_type

            self.invalidate(
                do_field=invalidate,
                do_metric=True,
                do_parameters=True
            )

            self.field.set(field_type=field_type, *args, **kwargs)

    def set_metric(
            self,
            invalidate: bool,
            *args,
            **kwargs
    ) -> None:
        """
        Sets the metric.

        @param invalidate: Enable to invalidate this model hierarchy level
        """
        Debug(self, ".set_metric()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_metric=invalidate,
                do_parameters=True
            )
            self.metric.set(*args, **kwargs)

    def set_parameters(
            self,
            invalidate: bool,
            *args,
            **kwargs
    ) -> None:
        """
        Sets the parameters.

        @param invalidate: Enable to invalidate this model hierarchy level
        """
        Debug(self, ".set_parameters()")

        with ModelAccess(self.gui, recalculate=False):

            self.invalidate(
                do_parameters=invalidate
            )
            self.parameters.set(*args, **kwargs)

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

        self.gui.sidebar_left.wire_widget.update()
        self.gui.menu.update()

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

        Note: Field label creation is triggered on-demand inside L{VisPyCanvas.redraw()}, not here.
        """
        Debug(self, ".on_metric_valid()")

        self.gui.sidebar_right.metric_widget.update()

    def on_parameters_valid(self) -> None:
        """
        Gets called when the parameters were successfully calculated.
        """
        Debug(self, ".on_parameters_valid()")

        self.gui.sidebar_right.parameters_widget.update()

    # ------------------------------------------------------------------------------------------------------------------

    def on_wire_invalid(self) -> None:
        """
        Gets called when the wire was invalidated.
        """
        Debug(self, ".on_wire_invalid()")

        self.gui.sidebar_left.wire_widget.update()
        self.gui.menu.update()

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

        self.gui.sidebar_right.metric_widget.update()
        self.gui.vispy_canvas.delete_field_labels()

    def on_parameters_invalid(self) -> None:
        """
        Gets called when the parameters were invalidated.
        """
        Debug(self, ".on_parameters_invalid()")

        self.gui.sidebar_right.parameters_widget.update()
