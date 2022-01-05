""" Wire_Widget module. """

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
from typing import Optional, Dict, List, Union
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox
from magneticalc.QDoubleSpinBox2 import QDoubleSpinBox2
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.QLabel2 import QLabel2
from magneticalc.QPushButton2 import QPushButton2
from magneticalc.QSpinBox2 import QSpinBox2
from magneticalc.QTableWidget2 import QTableWidget2
from magneticalc.Debug import Debug
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Theme import Theme
from magneticalc.Wire import Wire


class Wire_Widget(QGroupBox2):
    """ Wire_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    StretchMin = -99
    StretchMax = 99
    StretchStep = 0.1
    StretchPrecision = 2
    RotationalSymmetryCountMin = 1
    RotationalSymmetryCountMax = 99
    RotationalSymmetryRadiusMin = 0
    RotationalSymmetryRadiusMax = 99
    RotationalSymmetryRadiusStep = 0.1
    RotationalSymmetryRadiusPrecision = 2
    RotationalSymmetryOffsetMin = -360
    RotationalSymmetryOffsetMax = 360
    RotationalSymmetryOffsetStep = 1
    RotationalSymmetryOffsetPrecision = 1
    SlicerLimitMin = 0.001
    SlicerLimitMax = 2.0
    SlicerLimitStep = 0.001
    SlicerLimitPrecision = 3
    DcMin = -1e4
    DcMax = +1e4
    DcStep = 0.1
    DcPrecision = 3

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Wire")
        Debug(self, ": Init", init=True)
        self.gui = gui

        # --------------------------------------------------------------------------------------------------------------

        table_icon_label = QIconLabel("Points", "mdi.vector-square", expand=False)
        table_icon_label.addWidget(QLabel2("⟨F2⟩, ⟨ESC⟩", font_size="13px", color=Theme.LiteColor, expand=False))
        table_icon_label.addStretch()
        table_icon_label.addWidget(QPushButton2("", "fa.plus", self.on_table_row_added))
        table_icon_label.addWidget(QLabel2("cm", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(table_icon_label)
        self.table = QTableWidget2(
            self.gui,
            _cell_edited_callback_=self.on_table_cell_edited,
            _selection_changed_callback_=self.gui.redraw,
            _row_deleted_callback_=self.on_table_row_deleted,
            minimum_rows=2
        )
        self.table.set_horizontal_header(["X", "Y", "Z"])
        self.table.set_vertical_prefix("")
        self.table.set_horizontal_types(None)
        self.table.set_horizontal_options([None, None, None])
        self.addWidget(self.table)

        table_total_layout = QHBoxLayout()
        self.table_total_label = QLabel2("", color=Theme.MainColor, align_right=True)
        table_total_layout.addWidget(QLabel2("Total base points:", italic=True, color=Theme.LiteColor))
        table_total_layout.addWidget(self.table_total_label)
        self.addLayout(table_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        stretch_icon_label = QIconLabel("Stretch", "mdi.arrow-all")
        stretch_icon_label.addWidget(QPushButton2("", "fa.eraser", self.clear_stretch))
        stretch_icon_label.addWidget(QLabel2("cm", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(stretch_icon_label)

        self.stretch_spinbox = []
        stretch_layout = QHBoxLayout()
        for i in range(3):
            stretch_spinbox = QDoubleSpinBox2(
                gui=self.gui,
                minimum=self.StretchMin,
                maximum=self.StretchMax,
                step=self.StretchStep,
                precision=self.StretchPrecision,
                value=0,
                value_changed=self.set_stretch
            )
            self.stretch_spinbox.append(stretch_spinbox)
            stretch_layout.addWidget(QLabel2(["X", "Y", "Z"][i] + ":", expand=False))
            stretch_layout.addWidget(stretch_spinbox)
        self.addLayout(stretch_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        rotational_symmetry_icon_label = QIconLabel("Rotational Symmetry", "mdi.rotate-3d-variant")
        rotational_symmetry_icon_label.addWidget(QPushButton2("", "fa.eraser", self.clear_rotational_symmetry))
        self.addLayout(rotational_symmetry_icon_label)
        rotational_symmetry_layout = QHBoxLayout()
        rotational_symmetry_layout_left = QVBoxLayout()
        rotational_symmetry_layout_middle = QVBoxLayout()
        rotational_symmetry_layout_right = QVBoxLayout()
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_left)
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_middle)
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_right)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        rotational_symmetry_layout_left.addWidget(QLabel2("Count:"))
        self.rotational_symmetry_count_spinbox = QSpinBox2(
            minimum=self.RotationalSymmetryCountMin,
            maximum=self.RotationalSymmetryCountMax,
            value=0,
            value_changed=self.set_rotational_symmetry
        )
        rotational_symmetry_layout_middle.addWidget(self.rotational_symmetry_count_spinbox)
        rotational_symmetry_layout_right.addWidget(QLabel2("", width=self.UnitsLabelWidth))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_radius_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.RotationalSymmetryRadiusMin,
            maximum=self.RotationalSymmetryRadiusMax,
            step=self.RotationalSymmetryRadiusStep,
            precision=self.RotationalSymmetryRadiusPrecision,
            value=0,
            value_changed=self.set_rotational_symmetry
        )
        rotational_symmetry_layout_left.addWidget(QLabel2("Radius:"))
        rotational_symmetry_layout_middle.addWidget(self.rotational_symmetry_radius_spinbox)
        rotational_symmetry_count_radius_label = QLabel2("cm", align_right=True, width=self.UnitsLabelWidth)
        rotational_symmetry_layout_right.addWidget(rotational_symmetry_count_radius_label)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_axis_combobox = QComboBox()
        for i, axis in enumerate(["X", "Y", "Z"]):
            self.rotational_symmetry_axis_combobox.addItem(axis)
        rotational_symmetry_layout_left.addWidget(QLabel2("Axis:"))
        rotational_symmetry_layout_middle.addWidget(self.rotational_symmetry_axis_combobox)
        rotational_symmetry_layout_right.addWidget(QLabel2("", width=self.UnitsLabelWidth))
        self.rotational_symmetry_axis_combobox.currentIndexChanged.connect(  # type: ignore
            self.set_rotational_symmetry
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_offset_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.RotationalSymmetryOffsetMin,
            maximum=self.RotationalSymmetryOffsetMax,
            step=self.RotationalSymmetryOffsetStep,
            precision=self.RotationalSymmetryOffsetPrecision,
            value=0,
            value_changed=self.set_rotational_symmetry
        )
        rotational_symmetry_layout_left.addWidget(QLabel2("Offset Angle:"))
        rotational_symmetry_layout_middle.addWidget(self.rotational_symmetry_offset_spinbox)
        rotational_symmetry_offset_units_label = QLabel2("°", align_right=True, width=self.UnitsLabelWidth)
        rotational_symmetry_layout_right.addWidget(rotational_symmetry_offset_units_label)

        self.addLayout(rotational_symmetry_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.close_loop_checkbox = QCheckBox(" Close Loop")
        self.close_loop_checkbox.toggled.connect(  # type: ignore
            lambda: self.set_wire(_close_loop_=self.close_loop_checkbox.isChecked())
        )
        self.addWidget(self.close_loop_checkbox)

        rotational_symmetry_total_layout = QHBoxLayout()
        self.transformed_total_label = QLabel2("", color=Theme.MainColor, align_right=True)
        rotational_symmetry_total_layout.addWidget(
            QLabel2("Total transformed points:", italic=True, color=Theme.LiteColor)
        )
        rotational_symmetry_total_layout.addWidget(self.transformed_total_label)
        self.addLayout(rotational_symmetry_total_layout)
        self.addWidget(
            QPushButton2(
                " Replace base points",
                "mdi.content-copy",
                lambda: self.set_wire(_points_=self.gui.model.wire.get_points_transformed())
            )
        )

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Slicer Limit", "mdi.box-cutter"))
        self.slicer_limit_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.SlicerLimitMin,
            maximum=self.SlicerLimitMax,
            step=self.SlicerLimitStep,
            precision=self.SlicerLimitPrecision,
            value=0,
            value_changed=lambda: self.set_wire(_slicer_limit_=self.slicer_limit_spinbox.value())
        )
        slicer_limit_units_label = QLabel2("cm", align_right=True, width=self.UnitsLabelWidth)
        slicer_limit_layout = QHBoxLayout()
        slicer_limit_layout.addWidget(self.slicer_limit_spinbox)
        slicer_limit_layout.addWidget(slicer_limit_units_label)
        self.addLayout(slicer_limit_layout)

        sliced_total_layout = QHBoxLayout()
        self.sliced_total_label = QLabel2("", color=Theme.MainColor, align_right=True)
        sliced_total_layout.addWidget(QLabel2("Total sliced points:", italic=True, color=Theme.LiteColor))
        sliced_total_layout.addWidget(self.sliced_total_label)
        self.addLayout(sliced_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Wire Current", "fa.cog"))
        self.dc_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.DcMin,
            maximum=self.DcMax,
            step=self.DcStep,
            precision=self.DcPrecision,
            value=0,
            value_changed=lambda: self.set_wire(_dc_=self.dc_spinbox.value())
        )
        dc_layout = QHBoxLayout()
        dc_layout.addWidget(self.dc_spinbox)
        dc_layout.addWidget(QLabel2("A", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(dc_layout)

    def reload(self) -> None:
        """
        Reloads the widget.
        """
        Debug(self, ".reload()", refresh=True)

        self.blockSignals(True)

        for i in range(3):
            self.stretch_spinbox[i].setValue(self.gui.config.get_point("wire_stretch")[i])

        self.rotational_symmetry_count_spinbox.setValue(self.gui.config.get_float("rotational_symmetry_count"))
        self.rotational_symmetry_radius_spinbox.setValue(self.gui.config.get_float("rotational_symmetry_radius"))

        for i, axis in enumerate(["X", "Y", "Z"]):
            if i == self.gui.config.get_int("rotational_symmetry_axis"):
                self.rotational_symmetry_axis_combobox.setCurrentIndex(i)

        self.rotational_symmetry_offset_spinbox.setValue(self.gui.config.get_float("rotational_symmetry_offset"))

        self.close_loop_checkbox.setChecked(self.gui.config.get_bool("wire_close_loop"))

        self.slicer_limit_spinbox.setValue(self.gui.config.get_float("wire_slicer_limit"))
        self.dc_spinbox.setValue(self.gui.config.get_float("wire_dc"))

        self.blockSignals(False)

        # Initially load wire from configuration
        self.set_wire(recalculate=False, readjust_sampling_volume=False, invalidate=False)

        self.update()

    def update(self) -> None:
        """
        Updates the widget.
        """
        Debug(self, ".update()", refresh=True)

        self.update_labels()
        self.update_controls()

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()", refresh=True)

        if self.gui.model.wire.valid:
            self.sliced_total_label.setText(str(len(self.gui.model.wire.get_points_sliced())))
        else:
            self.sliced_total_label.setText("N/A")

    def update_controls(self) -> None:
        """
        Updates the controls.
        """
        Debug(self, ".update_controls()", refresh=True)

        self.indicate_valid(self.gui.model.wire.valid)

    # ------------------------------------------------------------------------------------------------------------------

    def update_table(self) -> None:
        """
        Populates the table.
        """
        Debug(self, ".update_table()")

        points = [[f"{round(col, 2):+0.02f}" for col in row] for row in self.gui.model.wire.get_points_base()]

        self.table.clear_rows()
        self.table.set_vertical_header([str(i + 1) for i in range(len(self.gui.model.wire.get_points_base()))])
        self.table.set_contents(points)
        self.table.select_last_row(focus=False)

        self.table_total_label.setText(str(len(self.gui.model.wire.get_points_base())))

    def on_table_row_added(self) -> None:
        """
        Gets called after a row has been added to the table.
        """
        Debug(self, ".on_table_row_added()")

        # Add a new base point (0, 0, 0) to the wire
        self.set_wire(_points_=list(self.gui.model.wire.get_points_base()) + [np.zeros(3)])
        self.table.select_last_row()

    def on_table_cell_edited(self, value: float, row: int, column: int) -> None:
        """
        Gets called after a table cell has been edited.

        @param value: Cell value
        @param row: Row index
        @param column: Column index
        """
        points = self.gui.model.wire.get_points_base()
        points[row][column] = value
        self.set_wire(_points_=points)

    def on_table_row_deleted(self, index: int) -> None:
        """
        Gets called after a row has been deleted from the table.

        @param index: Row index
        """
        Debug(self, ".on_table_row_deleted()")

        # Delete the wire base point at the given index
        self.set_wire(_points_=np.delete(self.gui.model.wire.get_points_base(), index, axis=0))

    # ------------------------------------------------------------------------------------------------------------------

    def set_stretch(self) -> None:
        """
        Handles changes to stretch transform parameters.
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_stretch()")

        self.set_wire(_stretch_=[self.stretch_spinbox[i].value() for i in range(3)])

    def clear_stretch(self) -> None:
        """
        Clears the stretch values.
        """
        Debug(self, ".clear_stretch()")

        stretch = [1.0, 1.0, 1.0]
        self.set_wire(_stretch_=stretch)
        self.update_stretch(stretch=stretch)

    def update_stretch(self, stretch: List) -> None:
        """
        Updates the stretch controls.

        @param stretch: 3D point
        """
        Debug(self, ".update_stretch()")

        self.blockSignals(True)
        for i in range(3):
            self.stretch_spinbox[i].setValue(stretch[i])
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_rotational_symmetry(self) -> None:
        """
        Handles changes to rotational symmetry transform parameters.
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_rotational_symmetry()")

        self.set_wire(
            _rotational_symmetry_={
                "count" : self.rotational_symmetry_count_spinbox.value(),
                "radius": self.rotational_symmetry_radius_spinbox.value(),
                "axis"  : {"X": 0, "Y": 1, "Z": 2}[self.rotational_symmetry_axis_combobox.currentText()],
                "offset": self.rotational_symmetry_offset_spinbox.value()
            }
        )

    def clear_rotational_symmetry(self) -> None:
        """
        Clears the rotational symmetry values.
        """
        Debug(self, ".clear_rotational_symmetry()")

        rotational_symmetry = {
            "count": 1,
            "radius": 0,
            "axis": 2,
            "offset": 0
        }
        self.set_wire(_rotational_symmetry_=rotational_symmetry)
        self.update_rotational_symmetry(rotational_symmetry=rotational_symmetry)

    def update_rotational_symmetry(self, rotational_symmetry: Dict) -> None:
        """
        Updates the rotational symmetry controls.

        @param rotational_symmetry: Dictionary
        """
        Debug(self, ".update_rotational_symmetry()")

        self.blockSignals(True)
        self.rotational_symmetry_count_spinbox.setValue(rotational_symmetry["count"])
        self.rotational_symmetry_radius_spinbox.setValue(rotational_symmetry["radius"])
        self.rotational_symmetry_axis_combobox.setCurrentIndex(rotational_symmetry["axis"])
        self.rotational_symmetry_offset_spinbox.setValue(rotational_symmetry["offset"])
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_wire(
            self,
            _points_: Optional[Union[List, np.ndarray]] = None,
            _stretch_: Optional[List] = None,
            _rotational_symmetry_: Optional[Dict] = None,
            _close_loop_: Optional[bool] = None,
            _slicer_limit_: Optional[float] = None,
            _dc_: Optional[float] = None,
            invalidate: bool = True,
            recalculate: bool = True,
            readjust_sampling_volume: bool = True
    ) -> None:
        """
        Sets the wire. This will overwrite the currently set wire in the model.
        Any underscored parameter may be left set to None in order to load its default value.

        Note: Currently, only `stretch` and `rotational symmetry` controls are automatically updated by this function.

        @param _points_: Points (List of 3D points)
        @param _stretch_: XYZ stretch transform factors (3D point)
        @param _rotational_symmetry_: Dictionary for rotational symmetry transform
        @param _close_loop_: Enable to transform the wire into a closed loop (append first point)
        @param _slicer_limit_: Slicer limit
        @param _dc_: DC value
        @param invalidate: Enable to invalidate this model hierarchy level
        @param recalculate: Enable to trigger final re-calculation
        @param readjust_sampling_volume: Enable to readjust sampling volume
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_wire()")

        with ModelAccess(self.gui, recalculate):

            should_update_stretch_controls = _stretch_ is not None
            should_update_rotational_symmetry_controls = _rotational_symmetry_ is not None

            points = self.gui.config.set_get_points("wire_points_base", _points_)
            stretch = self.gui.config.set_get_point("wire_stretch", _stretch_)
            close_loop = self.gui.config.set_get_bool("wire_close_loop", _close_loop_)
            slicer_limit = self.gui.config.set_get_float("wire_slicer_limit", _slicer_limit_)
            dc = self.gui.config.set_get_float("wire_dc", _dc_)

            rotational_symmetry = self.gui.config.set_get_dict(
                prefix="rotational_symmetry_",
                suffix="",
                types={"count": "int", "radius": "float", "axis": "int", "offset": "float"},
                values=_rotational_symmetry_,
            )

            self.gui.model.set_wire(
                invalidate=invalidate,
                points=points,
                stretch=stretch,
                rotational_symmetry=rotational_symmetry,
                close_loop=close_loop,
                slicer_limit=slicer_limit,
                dc=dc
            )

            self.update_table()

            if should_update_stretch_controls:
                self.update_stretch(stretch=stretch)

            if should_update_rotational_symmetry_controls:
                self.update_rotational_symmetry(rotational_symmetry=rotational_symmetry)

            self.transformed_total_label.setText(str(len(self.gui.model.wire.get_points_transformed())))

            if readjust_sampling_volume:
                self.gui.sidebar_left.sampling_volume_widget.readjust()
