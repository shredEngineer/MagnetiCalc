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
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox
from magneticalc.QtWidgets2.QDoubleSpinBox2 import QDoubleSpinBox2
from magneticalc.QtWidgets2.QGroupBox2 import QGroupBox2
from magneticalc.QtWidgets2.QHLine import QHLine
from magneticalc.QtWidgets2.QIconLabel import QIconLabel
from magneticalc.QtWidgets2.QLabel2 import QLabel2
from magneticalc.QtWidgets2.QPushButton2 import QPushButton2
from magneticalc.QtWidgets2.QSpinBox2 import QSpinBox2
from magneticalc.QtWidgets2.Theme import Theme
from magneticalc.QTableView2 import QTableView2
from magneticalc.Config_Collection import Config_Collection
from magneticalc.Debug import Debug
from magneticalc.Format import Format


""" Wire collection types. """
Wire_Collection_Types = {
    "points_base"               : "points",
    "stretch"                   : "point",
    "slicer_limit"              : "float",
    "dc"                        : "float",
    "close_loop"                : "bool",
    "rotational_symmetry_count" : "int",
    "rotational_symmetry_radius": "float",
    "rotational_symmetry_axis"  : "int",
    "rotational_symmetry_offset": "float"
}


""" Default stretch setting. """
DefaultStretch = {
    "stretch": [1.0, 1.0, 1.0]
}


""" Default rotational symmetry setting. """
DefaultRotationalSymmetry = {
    "rotational_symmetry_count" : 1,
    "rotational_symmetry_radius": 0,
    "rotational_symmetry_axis"  : 2,
    "rotational_symmetry_offset": 0
}


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
    RotationalSymmetryCountMax = 1000
    RotationalSymmetryRadiusMin = 0
    RotationalSymmetryRadiusMax = 1000
    RotationalSymmetryRadiusStep = 0.1
    RotationalSymmetryRadiusPrecision = 2
    RotationalSymmetryOffsetMin = -360
    RotationalSymmetryOffsetMax = 360
    RotationalSymmetryOffsetStep = 1
    RotationalSymmetryOffsetPrecision = 2
    SlicerLimitMin = 0.001
    SlicerLimitMax = 2.0
    SlicerLimitStep = 0.001
    SlicerLimitPrecision = 3
    DcMin = -1e4
    DcMax = +1e4
    DcStep = 0.1
    DcPrecision = 3

    def on_changed(self) -> None:
        """
        Gets called when some value was changed.
        The controls are bound to configuration.
        We just have to tell the model about it!
        """
        self.gui.interrupt_calculation()
        self.gui.model.set_wire(**self.group)
        if self.gui.project.get_bool("auto_calculation"):
            self.gui.recalculate()

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Wire", color=Theme.DarkColor)
        Debug(self, ": Init", init=True)
        self.gui = gui
        self.wire = gui.model.wire
        self.config_collection = Config_Collection(gui=gui, prefix="wire_", types=Wire_Collection_Types)
        self.group = self.config_collection.get_group(1, on_changed=self.on_changed)

        # --------------------------------------------------------------------------------------------------------------

        table_icon_label = QIconLabel("Points", "mdi.vector-square", color=Theme.DarkColor, expand=False)
        table_icon_label.addWidget(QLabel2("⟨F2⟩, ⟨ESC⟩", font_size="13px", color=Theme.LiteColor, expand=False))
        table_icon_label.addStretch()
        table_icon_label.addWidget(QPushButton2("", "fa.plus", self.on_table_row_added))
        table_icon_label.addWidget(QLabel2("cm", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(table_icon_label)
        self.table = QTableView2(
            self.gui,
            row_count_minimum=2,
            col_keys=["X", "Y", "Z"],
            on_cell_edited=self.on_table_cell_edited,
            on_selection_changed=self.gui.redraw,
            on_row_deleted=self.on_table_row_deleted
        )
        self.addWidget(self.table)

        table_total_layout = QHBoxLayout()
        self.table_total_label = QLabel2("", color=Theme.MainColor, align_right=True)
        table_total_layout.addWidget(QLabel2("Total base points:", italic=True, color=Theme.LiteColor))
        table_total_layout.addWidget(self.table_total_label)
        self.addLayout(table_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        stretch_icon_label = QIconLabel("Stretch", "mdi.arrow-all", color=Theme.DarkColor)
        stretch_icon_label.addWidget(
            QPushButton2("", "fa.eraser", lambda: self.group.set({"stretch": DefaultStretch}))
        )
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
                value_changed=lambda: self.group.set({"stretch": [self.stretch_spinbox[j].value() for j in range(3)]})
            )
            self.stretch_spinbox.append(stretch_spinbox)
            stretch_layout.addWidget(QLabel2(["X", "Y", "Z"][i] + ":", expand=False))
            stretch_layout.addWidget(stretch_spinbox)
        self.addLayout(stretch_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        rotational_symmetry_icon_label = QIconLabel(
            "Rotational Symmetry", "mdi.rotate-3d-variant", color=Theme.DarkColor
        )
        rotational_symmetry_icon_label.addWidget(
            QPushButton2("", "fa.eraser", lambda: self.group.set(DefaultRotationalSymmetry))
        )
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
            value_changed=lambda: self.group.set({
                "rotational_symmetry_count": self.rotational_symmetry_count_spinbox.value()
            })

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
            value_changed=lambda: self.group.set({
                "rotational_symmetry_radius": self.rotational_symmetry_radius_spinbox.value()
            })
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
            lambda: self.group.set({
                "rotational_symmetry_axis":
                {"X": 0, "Y": 1, "Z": 2}[self.rotational_symmetry_axis_combobox.currentText()]
            })
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_offset_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.RotationalSymmetryOffsetMin,
            maximum=self.RotationalSymmetryOffsetMax,
            step=self.RotationalSymmetryOffsetStep,
            precision=self.RotationalSymmetryOffsetPrecision,
            value=0,
            value_changed=lambda: self.group.set({
                "rotational_symmetry_offset": self.rotational_symmetry_offset_spinbox.value()
            })

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
            lambda: self.group.set({"close_loop": self.close_loop_checkbox.isChecked()})
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
                lambda: self.group.set({"points": self.wire.points_transformed})
            )
        )

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Slicer Limit", "mdi.box-cutter", color=Theme.DarkColor))
        self.slicer_limit_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.SlicerLimitMin,
            maximum=self.SlicerLimitMax,
            step=self.SlicerLimitStep,
            precision=self.SlicerLimitPrecision,
            value=0,
            value_changed=lambda: self.group.set({"slicer_limit": self.slicer_limit_spinbox.value()})
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

        self.addLayout(QIconLabel("Wire Current", "fa.cog", color=Theme.DarkColor))
        self.dc_spinbox = QDoubleSpinBox2(
            gui=self.gui,
            minimum=self.DcMin,
            maximum=self.DcMax,
            step=self.DcStep,
            precision=self.DcPrecision,
            value=0,
            value_changed=lambda: self.group.set({"dc": self.dc_spinbox.value()})
        )
        dc_layout = QHBoxLayout()
        dc_layout.addWidget(self.dc_spinbox)
        dc_layout.addWidget(QLabel2("A", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(dc_layout)

    def reload(self) -> None:
        """
        Reloads the widget.
        This populates all widgets with their proper values.
        """
        Debug(self, ".reload(): WARNING: Reloading", refresh=True, warning=True)

        self.gui.model.set_wire(**self.group)

        self.group.blockSignals(True)
        [self.stretch_spinbox[i].setValue(self.group["stretch"][i]) for i in range(3)]
        self.rotational_symmetry_count_spinbox.setValue(self.group["rotational_symmetry_count"])
        self.rotational_symmetry_radius_spinbox.setValue(self.group["rotational_symmetry_radius"])
        self.rotational_symmetry_axis_combobox.setCurrentIndex(self.group["rotational_symmetry_axis"])
        self.rotational_symmetry_offset_spinbox.setValue(self.group["rotational_symmetry_offset"])
        self.close_loop_checkbox.setChecked(self.group["close_loop"])
        self.slicer_limit_spinbox.setValue(self.group["slicer_limit"])
        self.dc_spinbox.setValue(self.group["dc"])
        self.group.blockSignals(False)

        self.refresh()

    def refresh(self) -> None:
        """
        Updates the widget.
        """
        Debug(self, ".refresh(): WARNING: Update", refresh=True, warning=True)

        self.set_color(Theme.MainColor if self.wire.valid else Theme.FailureColor)

        if self.wire.valid:
            self.sliced_total_label.setText(str(len(self.wire.points_sliced)))
        else:
            self.sliced_total_label.setText("N/A")

        self.table.set_data(
            data=[[Format.float_to_str(col) for col in row] for row in self.wire.points_base],
            row_keys=[str(i + 1) for i in range(len(self.wire.points_base))]
        )
        self.table.select_last_row(focus=False)

        self.table_total_label.setText(str(len(self.wire.points_base)))

        self.transformed_total_label.setText(str(len(self.wire.points_transformed)))

        if hasattr(self.gui.sidebar_left, "sampling_volume_widget"):
            self.gui.sidebar_left.sampling_volume_widget.readjust()

    # ------------------------------------------------------------------------------------------------------------------

    def on_table_row_added(self) -> None:
        """
        Gets called after a row has been added to the table.
        """
        Debug(self, ".on_table_row_added()")

        # Add a new base point (0, 0, 0) to the wire
        self.group.set({"points_base": list(self.wire.points_base) + [np.zeros(3)]})
        self.table.select_last_row()

    def on_table_cell_edited(self, value: float, row: int, column: int) -> None:
        """
        Gets called after a table cell has been edited.

        @param value: Cell value
        @param row: Row index
        @param column: Column index
        """
        points = self.wire.points_base
        points[row][column] = value
        self.group.set({"points_base": points})

    def on_table_row_deleted(self, index: int) -> None:
        """
        Gets called after a row has been deleted from the table.

        @param index: Row index
        """
        Debug(self, ".on_table_row_deleted()")

        # Delete the wire base point at the given index
        self.group.set({"points_base": np.delete(self.wire.points_base, index, axis=0)})
