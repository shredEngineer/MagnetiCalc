""" Wire_Widget module. """

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
from typing import Optional, Dict, List, Union
import numpy as np
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import \
    QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QLabel, QSizePolicy, QCheckBox
from magneticalc.Debug import Debug
from magneticalc.QIconLabel import QIconLabel
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.ModelAccess import ModelAccess
from magneticalc.QTableWidget2 import QTableWidget2
from magneticalc.Theme import Theme
from magneticalc.Wire import Wire

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


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
    SlicerLimitMinimum = 0.001
    SlicerLimitMaximum = 2.0
    SlicerLimitStep = 0.001
    SlicerLimitPrecision = 3
    DcMinimum = -1e4
    DcMaximum = +1e4
    DcStep = 0.1
    DcPrecision = 3

    def __init__(self, gui: GUI) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Wire")
        Debug(self, ": Init")
        self.gui = gui

        # --------------------------------------------------------------------------------------------------------------

        table_icon_label = QIconLabel("Points", "mdi.vector-square", final_stretch=False)
        table_shortcut_label = QLabel("⟨F2⟩, ⟨ESC⟩")
        table_shortcut_label.setStyleSheet(f"font-size: 13px; color: {Theme.LiteColor}")
        table_icon_label.addWidget(table_shortcut_label)
        table_icon_label.addStretch()
        table_add_button = QPushButton()
        table_add_button.setIcon(qta.icon("fa.plus"))
        # noinspection PyUnresolvedReferences
        table_add_button.clicked.connect(self.on_table_row_added)
        table_icon_label.addWidget(table_add_button)
        table_units_label = QLabel("cm")
        table_units_label.setAlignment(Qt.AlignRight)
        table_units_label.setFixedWidth(self.UnitsLabelWidth)
        table_icon_label.addWidget(table_units_label)
        self.addLayout(table_icon_label)
        self.table = QTableWidget2(
            self.gui,
            cell_edited_callback=self.on_table_cell_edited,
            selection_changed_callback=self.gui.redraw,
            row_deleted_callback=self.on_table_row_deleted,
            minimum_rows=2
        )
        self.table.set_horizontal_header(["X", "Y", "Z"])
        self.table.set_vertical_prefix("")
        self.table.set_horizontal_types(None)
        self.table.set_horizontal_options([None, None, None])
        self.addWidget(self.table)

        table_total_layout = QHBoxLayout()
        table_total_label_left = QLabel("Total base points:")
        table_total_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.table_total_label = QLabel("")
        self.table_total_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.table_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table_total_layout.addWidget(table_total_label_left, alignment=Qt.AlignVCenter)
        table_total_layout.addWidget(self.table_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(table_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        stretch_icon_label = QIconLabel("Stretch", "mdi.arrow-all")
        stretch_clear_button = QPushButton()
        stretch_clear_button.setIcon(qta.icon("fa.eraser"))
        # noinspection PyUnresolvedReferences
        stretch_clear_button.clicked.connect(self.clear_stretch)
        stretch_icon_label.addWidget(stretch_clear_button)
        stretch_units_label = QLabel("cm")
        stretch_units_label.setAlignment(Qt.AlignRight)
        stretch_units_label.setFixedWidth(self.UnitsLabelWidth)
        stretch_icon_label.addWidget(stretch_units_label)
        self.addLayout(stretch_icon_label)

        self.stretch_spinbox = [None, None, None]
        stretch_label = [None, None, None]
        stretch_layout = QHBoxLayout()
        for i in range(3):
            self.stretch_spinbox[i] = QDoubleSpinBox(self.gui)
            self.stretch_spinbox[i].setLocale(self.gui.locale)
            self.stretch_spinbox[i].setMinimum(self.StretchMin)
            self.stretch_spinbox[i].setMaximum(self.StretchMax)
            self.stretch_spinbox[i].setSingleStep(self.StretchStep)
            self.stretch_spinbox[i].setDecimals(self.StretchPrecision)
            # noinspection PyUnresolvedReferences
            self.stretch_spinbox[i].valueChanged.connect(self.set_stretch)
            stretch_label[i] = QLabel(["X", "Y", "Z"][i] + ":")
            stretch_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            stretch_layout.addWidget(stretch_label[i], alignment=Qt.AlignVCenter)
            stretch_layout.addWidget(self.stretch_spinbox[i], alignment=Qt.AlignVCenter)
        self.addLayout(stretch_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        rotational_symmetry_icon_label = QIconLabel("Rotational Symmetry", "mdi.rotate-3d-variant")
        rotational_symmetry_clear_button = QPushButton()
        rotational_symmetry_clear_button.setIcon(qta.icon("fa.eraser"))
        # noinspection PyUnresolvedReferences
        rotational_symmetry_clear_button.clicked.connect(self.clear_rotational_symmetry)
        rotational_symmetry_icon_label.addWidget(rotational_symmetry_clear_button)
        self.addLayout(rotational_symmetry_icon_label)
        rotational_symmetry_layout = QHBoxLayout()
        rotational_symmetry_layout_left = QVBoxLayout()
        rotational_symmetry_layout_middle = QVBoxLayout()
        rotational_symmetry_layout_right = QVBoxLayout()
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_left)
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_middle)
        rotational_symmetry_layout.addLayout(rotational_symmetry_layout_right)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_count_spinbox = QSpinBox()
        self.rotational_symmetry_count_spinbox.setMinimum(self.RotationalSymmetryCountMin)
        self.rotational_symmetry_count_spinbox.setMaximum(self.RotationalSymmetryCountMax)
        count_label = QLabel("Count:")
        count_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(count_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_count_spinbox,
            alignment=Qt.AlignVCenter
        )
        # noinspection PyUnresolvedReferences
        self.rotational_symmetry_count_spinbox.valueChanged.connect(self.set_rotational_symmetry)
        rotational_symmetry_layout_right.addWidget(QLabel(""))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_radius_spinbox = QDoubleSpinBox(self.gui)
        self.rotational_symmetry_radius_spinbox.setLocale(self.gui.locale)
        self.rotational_symmetry_radius_spinbox.setMinimum(self.RotationalSymmetryRadiusMin)
        self.rotational_symmetry_radius_spinbox.setMaximum(self.RotationalSymmetryRadiusMax)
        self.rotational_symmetry_radius_spinbox.setDecimals(self.RotationalSymmetryRadiusPrecision)
        self.rotational_symmetry_radius_spinbox.setSingleStep(self.RotationalSymmetryRadiusStep)
        radius_label = QLabel("Radius:")
        radius_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(radius_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_radius_spinbox,
            alignment=Qt.AlignVCenter
        )
        rotational_symmetry_count_radius_label = QLabel("cm")
        rotational_symmetry_count_radius_label.setAlignment(Qt.AlignRight)
        rotational_symmetry_count_radius_label.setFixedWidth(self.UnitsLabelWidth)
        rotational_symmetry_layout_right.addWidget(rotational_symmetry_count_radius_label, alignment=Qt.AlignVCenter)
        # noinspection PyUnresolvedReferences
        self.rotational_symmetry_radius_spinbox.valueChanged.connect(self.set_rotational_symmetry)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_axis_combobox = QComboBox()
        for i, axis in enumerate(["X", "Y", "Z"]):
            self.rotational_symmetry_axis_combobox.addItem(axis)
        axis_label = QLabel("Axis:")
        axis_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(axis_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_axis_combobox,
            alignment=Qt.AlignVCenter
        )
        rotational_symmetry_layout_right.addWidget(QLabel(""))
        # noinspection PyUnresolvedReferences
        self.rotational_symmetry_axis_combobox.currentIndexChanged.connect(self.set_rotational_symmetry)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_offset_spinbox = QDoubleSpinBox(self.gui)
        self.rotational_symmetry_offset_spinbox.setLocale(self.gui.locale)
        self.rotational_symmetry_offset_spinbox.setMinimum(self.RotationalSymmetryOffsetMin)
        self.rotational_symmetry_offset_spinbox.setMaximum(self.RotationalSymmetryOffsetMax)
        self.rotational_symmetry_offset_spinbox.setDecimals(self.RotationalSymmetryOffsetPrecision)
        self.rotational_symmetry_offset_spinbox.setSingleStep(self.RotationalSymmetryOffsetStep)
        Offset_label = QLabel("Offset Angle:")
        Offset_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(Offset_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_offset_spinbox,
            alignment=Qt.AlignVCenter
        )
        rotational_symmetry_offset_units_label = QLabel("°")
        rotational_symmetry_offset_units_label.setAlignment(Qt.AlignRight)
        rotational_symmetry_offset_units_label.setFixedWidth(self.UnitsLabelWidth)
        rotational_symmetry_layout_right.addWidget(rotational_symmetry_offset_units_label, alignment=Qt.AlignVCenter)
        # noinspection PyUnresolvedReferences
        self.rotational_symmetry_offset_spinbox.valueChanged.connect(self.set_rotational_symmetry)

        self.addLayout(rotational_symmetry_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.close_loop_checkbox = QCheckBox(" Close Loop")
        # noinspection PyUnresolvedReferences
        self.close_loop_checkbox.toggled.connect(
            lambda: self.set_wire(close_loop=self.close_loop_checkbox.isChecked())
        )
        self.addWidget(self.close_loop_checkbox)

        rotational_symmetry_total_layout = QHBoxLayout()
        rotational_symmetry_total_label_left = QLabel("Total transformed points:")
        rotational_symmetry_total_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.transformed_total_label = QLabel("")
        self.transformed_total_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.transformed_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rotational_symmetry_total_layout.addWidget(
            rotational_symmetry_total_label_left,
            alignment=Qt.AlignVCenter
        )
        rotational_symmetry_total_layout.addWidget(self.transformed_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(rotational_symmetry_total_layout)

        replace_base_points_button = QPushButton(" Replace base points")
        replace_base_points_button.setIcon(qta.icon("mdi.content-copy"))
        # noinspection PyUnresolvedReferences
        replace_base_points_button.clicked.connect(
            lambda: self.set_wire(points=self.gui.model.wire.get_points_transformed())
        )
        self.addWidget(replace_base_points_button)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Slicer Limit", "mdi.box-cutter"))
        self.slicer_limit_spinbox = QDoubleSpinBox(self.gui)
        self.slicer_limit_spinbox.setLocale(self.gui.locale)
        self.slicer_limit_spinbox.setMinimum(self.SlicerLimitMinimum)
        self.slicer_limit_spinbox.setMaximum(self.SlicerLimitMaximum)
        self.slicer_limit_spinbox.setDecimals(self.SlicerLimitPrecision)
        self.slicer_limit_spinbox.setSingleStep(self.SlicerLimitStep)
        # noinspection PyUnresolvedReferences
        self.slicer_limit_spinbox.valueChanged.connect(
            lambda: self.set_wire(slicer_limit=self.slicer_limit_spinbox.value())
        )
        slicer_limit_units_label = QLabel("cm")
        slicer_limit_units_label.setAlignment(Qt.AlignRight)
        slicer_limit_units_label.setFixedWidth(self.UnitsLabelWidth)
        slicer_limit_layout = QHBoxLayout()
        slicer_limit_layout.addWidget(self.slicer_limit_spinbox, alignment=Qt.AlignVCenter)
        slicer_limit_layout.addWidget(slicer_limit_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(slicer_limit_layout)

        sliced_total_layout = QHBoxLayout()
        sliced_total_label_left = QLabel("Total sliced points:")
        sliced_total_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.sliced_total_label = QLabel("")
        self.sliced_total_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.sliced_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sliced_total_layout.addWidget(sliced_total_label_left, alignment=Qt.AlignVCenter)
        sliced_total_layout.addWidget(self.sliced_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(sliced_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        self.dc_spinbox = QDoubleSpinBox(self.gui)
        self.dc_spinbox.setLocale(self.gui.locale)
        self.addLayout(QIconLabel("Wire Current", "fa.cog"))
        self.dc_spinbox.setMinimum(self.DcMinimum)
        self.dc_spinbox.setMaximum(self.DcMaximum)
        self.dc_spinbox.setSingleStep(self.DcStep)
        self.dc_spinbox.setDecimals(self.DcPrecision)
        # noinspection PyUnresolvedReferences
        self.dc_spinbox.valueChanged.connect(lambda: self.set_wire(dc=self.dc_spinbox.value()))
        dc_layout = QHBoxLayout()
        dc_layout.addWidget(self.dc_spinbox, alignment=Qt.AlignVCenter)
        dc_unit_label = QLabel("A")
        dc_unit_label.setAlignment(Qt.AlignRight)
        dc_unit_label.setFixedWidth(self.UnitsLabelWidth)
        dc_layout.addWidget(dc_unit_label, alignment=Qt.AlignVCenter)
        self.addLayout(dc_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.reinitialize()

    def reinitialize(self) -> None:
        """
        Re-initializes the widget.
        """
        Debug(self, ".reinitialize()")

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
        self.set_wire(recalculate=False, readjust_sampling_volume=False, invalidate_self=False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_wire(
            self,
            points: Optional[Union[List, np.ndarray]] = None,
            stretch: Optional[List] = None,
            rotational_symmetry: Optional[Dict] = None,
            close_loop: Optional[bool] = None,
            slicer_limit: Optional[float] = None,
            dc: Optional[float] = None,
            recalculate: bool = True,
            readjust_sampling_volume: bool = True,
            invalidate_self: bool = True
    ) -> None:
        """
        Sets the wire. This will overwrite the currently set wire in the model.
        Any parameter may be left set to None in order to load its default value.

        Note: Currently, only `stretch` and `rotational symmetry` controls are automatically updated by this function.

        @param points: Points (List of 3D points)
        @param stretch: XYZ stretch transform factors (3D point)
        @param rotational_symmetry: Dictionary for rotational symmetry transform
        @param close_loop: Enable to transform the wire into a closed loop (append first point)
        @param slicer_limit: Slicer limit
        @param dc: DC value
        @param recalculate: Enable to trigger final re-calculation
        @param readjust_sampling_volume: Enable to readjust sampling volume
        @param invalidate_self: Enable to invalidate the old wire before setting a new one
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_wire()")

        with ModelAccess(self.gui, recalculate):

            should_update_stretch_controls = stretch is not None
            should_update_rotational_symmetry_controls = rotational_symmetry is not None

            points = self.gui.config.set_get_points("wire_points_base", points)
            stretch = self.gui.config.set_get_point("wire_stretch", stretch)
            close_loop = self.gui.config.set_get_bool("wire_close_loop", close_loop)
            slicer_limit = self.gui.config.set_get_float("wire_slicer_limit", slicer_limit)
            dc = self.gui.config.set_get_float("wire_dc", dc)

            rotational_symmetry = self.gui.config.set_get_dict(
                prefix="rotational_symmetry_",
                suffix="",
                types={"count": "int", "radius": "float", "axis": "int", "offset": "float"},
                values=rotational_symmetry,
            )

            self.gui.model.set_wire(
                Wire(
                    points=points,
                    stretch=stretch,
                    rotational_symmetry=rotational_symmetry,
                    close_loop=close_loop,
                    slicer_limit=slicer_limit,
                    dc=dc
                ),
                invalidate_self=invalidate_self
            )

            self.update_table()

            if should_update_stretch_controls:
                self.update_stretch(stretch=stretch)

            if should_update_rotational_symmetry_controls:
                self.update_rotational_symmetry(rotational_symmetry=rotational_symmetry)

            self.transformed_total_label.setText(str(len(self.gui.model.wire.get_points_transformed())))

            if readjust_sampling_volume:
                self.gui.sidebar_left.sampling_volume_widget.readjust()

    # ------------------------------------------------------------------------------------------------------------------

    def set_stretch(self) -> None:
        """
        Handles changes to stretch transform parameters.
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_stretch()")

        self.set_wire(stretch=[self.stretch_spinbox[i].value() for i in range(3)])

    def clear_stretch(self) -> None:
        """
        Clears the stretch values.
        """
        Debug(self, ".clear_stretch()")

        stretch = [1.0, 1.0, 1.0]
        self.set_wire(stretch=stretch)
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
            rotational_symmetry={
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
        self.set_wire(rotational_symmetry=rotational_symmetry)
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
        self.set_wire(points=list(self.gui.model.wire.get_points_base()) + [np.zeros(3)])
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
        self.set_wire(points=points)

    def on_table_row_deleted(self, index: int) -> None:
        """
        Gets called after a row has been deleted from the table.

        @param index: Row index
        """
        Debug(self, ".on_table_row_deleted()")

        # Delete the wire base point at the given index
        self.set_wire(points=np.delete(self.gui.model.wire.get_points_base(), index, axis=0))

    # ------------------------------------------------------------------------------------------------------------------

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()")

        if self.gui.model.wire.is_valid():
            self.sliced_total_label.setText(str(len(self.gui.model.wire.get_points_sliced())))
        else:
            self.sliced_total_label.setText("N/A")
