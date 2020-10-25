""" Wire_Widget module. """

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

import numpy as np
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import \
    QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QLabel, QSizePolicy
from magneticalc.IconLabel import IconLabel
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Table import Table
from magneticalc.Wire import Wire


class Wire_Widget(Groupbox):
    """ Wire_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    RotationalSymmetryCountMin = 1
    RotationalSymmetryCountMax = 99
    RotationalSymmetryRadiusMin = 0
    RotationalSymmetryRadiusMax = 99
    RotationalSymmetryRadiusStep = 0.1
    StretchMin = -99
    StretchMax = 99
    StretchStep = 0.1
    SlicerLimitMinimum = 0.01
    SlicerLimitMaximum = 2.0
    SlicerLimitStep = 0.01
    DcMinimum = -999.0
    DcMaximum = 999.0
    DcStep = 0.1

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        self.gui = gui

        Groupbox.__init__(self, "Wire")

        points_icon_label = IconLabel("mdi.vector-square", "Points")
        table_add_button = QPushButton()
        table_add_button.setIcon(qta.icon("fa.plus"))
        points_icon_label.addWidget(table_add_button)
        table_units_label = QLabel("cm")
        table_units_label.setAlignment(Qt.AlignRight)
        table_units_label.setFixedWidth(self.UnitsLabelWidth)
        points_icon_label.addWidget(table_units_label)
        table_add_button.clicked.connect(self.on_table_row_added)
        self.addWidget(points_icon_label)
        self.table = Table(
            cell_edited_callback=self.on_table_cell_edited,
            row_deleted_callback=self.on_table_row_deleted
        )
        self.table.set_horizontal_header(["X", "Y", "Z"])
        self.addWidget(self.table)

        table_total_layout = QHBoxLayout()
        table_total_label_left = QLabel("Total base points:")
        table_total_label_left.setStyleSheet("""
            color: #555555;
            font-style: italic;
        """)
        self.base_total_label = QLabel("")
        self.base_total_label.setStyleSheet("""
            color: #2a7db0;
        """)
        self.base_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table_total_layout.addWidget(table_total_label_left, alignment=Qt.AlignVCenter)
        table_total_layout.addWidget(self.base_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(table_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(HLine())

        stretch_icon_label = IconLabel("mdi.arrow-all", "Stretch")
        stretch_clear_button = QPushButton()
        stretch_clear_button.setIcon(qta.icon("fa.eraser"))
        stretch_clear_button.clicked.connect(self.clear_stretch)
        stretch_icon_label.addWidget(stretch_clear_button)
        stretch_units_label = QLabel("cm")
        stretch_units_label.setAlignment(Qt.AlignRight)
        stretch_units_label.setFixedWidth(self.UnitsLabelWidth)
        stretch_icon_label.addWidget(stretch_units_label)
        self.addWidget(stretch_icon_label)

        self.stretch_spinbox = [None, None, None]
        stretch_label = [None, None, None]
        stretch_layout = QHBoxLayout()
        for i in range(3):
            self.stretch_spinbox[i] = QDoubleSpinBox(self.gui)
            self.stretch_spinbox[i].setMinimum(self.StretchMin)
            self.stretch_spinbox[i].setMaximum(self.StretchMax)
            self.stretch_spinbox[i].setSingleStep(self.StretchStep)
            self.stretch_spinbox[i].setValue(self.gui.config.get_point("wire_stretch")[i])
            self.stretch_spinbox[i].valueChanged.connect(self.set_stretch)
            stretch_label[i] = QLabel(["X", "Y", "Z"][i] + ":")
            stretch_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            stretch_layout.addWidget(stretch_label[i], alignment=Qt.AlignVCenter)
            stretch_layout.addWidget(self.stretch_spinbox[i], alignment=Qt.AlignVCenter)
        self.addLayout(stretch_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(HLine())

        self.addWidget(IconLabel("mdi.rotate-3d-variant", "Rotational Symmetry"))
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
        self.rotational_symmetry_count_spinbox.setValue(self.gui.config.get_float("rotational_symmetry_count"))
        count_label = QLabel("Count:")
        count_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(count_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_count_spinbox,
            alignment=Qt.AlignVCenter
        )
        self.rotational_symmetry_count_spinbox.valueChanged.connect(self.set_rotational_symmetry)
        rotational_symmetric_units_label = QLabel("cm")
        rotational_symmetric_units_label.setAlignment(Qt.AlignRight)
        rotational_symmetric_units_label.setFixedWidth(self.UnitsLabelWidth)
        rotational_symmetry_layout_right.addWidget(rotational_symmetric_units_label, alignment=Qt.AlignVCenter)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_radius_spinbox = QDoubleSpinBox()
        self.rotational_symmetry_radius_spinbox.setMinimum(self.RotationalSymmetryRadiusMin)
        self.rotational_symmetry_radius_spinbox.setMaximum(self.RotationalSymmetryRadiusMax)
        self.rotational_symmetry_radius_spinbox.setSingleStep(self.RotationalSymmetryRadiusStep)
        self.rotational_symmetry_radius_spinbox.setValue(self.gui.config.get_float("rotational_symmetry_radius"))
        radius_label = QLabel("Radius:")
        radius_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(radius_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_radius_spinbox,
            alignment=Qt.AlignVCenter
        )
        self.rotational_symmetry_radius_spinbox.valueChanged.connect(self.set_rotational_symmetry)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.rotational_symmetry_axis_combobox = QComboBox()
        for i, axis in enumerate(["X", "Y", "Z"]):
            self.rotational_symmetry_axis_combobox.addItem(axis)
            if i == self.gui.config.get_int("rotational_symmetry_axis"):
                self.rotational_symmetry_axis_combobox.setCurrentIndex(i)
        axis_label = QLabel("Axis:")
        axis_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rotational_symmetry_layout_left.addWidget(axis_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        rotational_symmetry_layout_middle.addWidget(
            self.rotational_symmetry_axis_combobox,
            alignment=Qt.AlignVCenter
        )
        self.rotational_symmetry_axis_combobox.currentIndexChanged.connect(self.set_rotational_symmetry)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addLayout(rotational_symmetry_layout)

        rotational_symmetry_total_layout = QHBoxLayout()
        rotational_symmetry_total_label_left = QLabel("Total transformed points:")
        rotational_symmetry_total_label_left.setStyleSheet("""
            color: #555555;
            font-style: italic;
        """)
        self.transformed_total_label = QLabel("")
        self.transformed_total_label.setStyleSheet("""
            color: #2a7db0;
        """)
        self.transformed_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rotational_symmetry_total_layout.addWidget(
            rotational_symmetry_total_label_left,
            alignment=Qt.AlignVCenter
        )
        rotational_symmetry_total_layout.addWidget(self.transformed_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(rotational_symmetry_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(HLine())

        self.addWidget(IconLabel("mdi.box-cutter", "Slicer Limit"))
        slicer_limit_spinbox = QDoubleSpinBox()
        slicer_limit_spinbox.setMinimum(self.SlicerLimitMinimum)
        slicer_limit_spinbox.setMaximum(self.SlicerLimitMaximum)
        slicer_limit_spinbox.setSingleStep(self.SlicerLimitStep)
        slicer_limit_spinbox.setValue(self.gui.config.get_float("wire_slicer_limit"))
        slicer_limit_spinbox.valueChanged.connect(
            lambda: self.set_wire(slicer_limit=slicer_limit_spinbox.value())
        )
        slicer_limit_units_label = QLabel("cm")
        slicer_limit_units_label.setAlignment(Qt.AlignRight)
        slicer_limit_units_label.setFixedWidth(self.UnitsLabelWidth)
        slicer_limit_layout = QHBoxLayout()
        slicer_limit_layout.addWidget(slicer_limit_spinbox, alignment=Qt.AlignVCenter)
        slicer_limit_layout.addWidget(slicer_limit_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(slicer_limit_layout)

        sliced_total_layout = QHBoxLayout()
        sliced_total_label_left = QLabel("Total sliced points:")
        sliced_total_label_left.setStyleSheet("""
            color: #555555;
            font-style: italic;
        """)
        self.sliced_total_label = QLabel("")
        self.sliced_total_label.setStyleSheet("""
            color: #2a7db0;
        """)
        self.sliced_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sliced_total_layout.addWidget(sliced_total_label_left, alignment=Qt.AlignVCenter)
        sliced_total_layout.addWidget(self.sliced_total_label, alignment=Qt.AlignVCenter)
        self.addLayout(sliced_total_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(HLine())

        dc_spinbox = QDoubleSpinBox()
        self.addWidget(IconLabel("fa.cog", "Wire Current"))
        dc_spinbox.setMinimum(self.DcMinimum)
        dc_spinbox.setMaximum(self.DcMaximum)
        dc_spinbox.setSingleStep(self.DcStep)
        dc_spinbox.setValue(self.gui.config.get_float("wire_dc"))
        dc_spinbox.valueChanged.connect(lambda: self.set_wire(dc=dc_spinbox.value()))
        dc_layout = QHBoxLayout()
        dc_layout.addWidget(dc_spinbox, alignment=Qt.AlignVCenter)
        dc_unit_label = QLabel("A")
        dc_unit_label.setAlignment(Qt.AlignRight)
        dc_unit_label.setFixedWidth(self.UnitsLabelWidth)
        dc_layout.addWidget(dc_unit_label, alignment=Qt.AlignVCenter)
        self.addLayout(dc_layout)

        # Initially load wire from configuration
        self.set_wire(recalculate=False, readjust_sampling_volume=False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_wire(
            self,
            points=None,
            stretch=None,
            rotational_symmetry=None,
            slicer_limit=None,
            dc=None,
            recalculate=True,
            readjust_sampling_volume=True
    ):
        """
        Sets the wire. This will overwrite the currently set wire in the model.
        Any parameter may be left set to None in order to load its default value.

        @param points: Points (List of 3D points)
        @param stretch: XYZ stretch transform factors (3D point)
        @param rotational_symmetry: Dictionary for rotational symmetry transform
        @param slicer_limit: Slicer limit (float)
        @param dc: DC value (float)
        @param recalculate: Enable to trigger final re-calculation (boolean)
        @param readjust_sampling_volume: Enable to readjust sampling volume
        """
        with ModelAccess(self.gui, recalculate):

            points = self.gui.config.set_get_points("wire_points_base", points)
            stretch = self.gui.config.set_get_point("wire_stretch", stretch)
            slicer_limit = self.gui.config.set_get_float("wire_slicer_limit", slicer_limit)
            dc = self.gui.config.set_get_float("wire_dc", dc)

            # ToDo: Implement some kind of "self.gui.config.set_get_dict" to make this shorter
            if rotational_symmetry is None:
                count = self.gui.config.get_int("rotational_symmetry_count")
                radius = self.gui.config.get_float("rotational_symmetry_radius")
                axis = self.gui.config.get_int("rotational_symmetry_axis")
            else:
                count = self.gui.config.set_get_int("rotational_symmetry_count", rotational_symmetry["count"])
                radius = self.gui.config.set_get_float("rotational_symmetry_radius", rotational_symmetry["radius"])
                axis = self.gui.config.set_get_int("rotational_symmetry_axis", rotational_symmetry["axis"])
            rotational_symmetry = {
                "count": count,
                "radius": radius,
                "axis": axis
            }

            self.gui.model.set_wire(
                Wire(
                    points=points,
                    stretch=stretch,
                    rotational_symmetry=rotational_symmetry,
                    slicer_limit=slicer_limit,
                    dc=dc
                )
            )

            self.update_table()

            self.transformed_total_label.setText(str(len(self.gui.model.wire.get_points_transformed())))

            if readjust_sampling_volume:
                self.gui.sidebar_left.sampling_volume_widget.readjust()

    # ------------------------------------------------------------------------------------------------------------------

    def set_stretch(self):
        """
        Handles changes to stretch transform parameters.
        """
        if self.signalsBlocked():
            return

        self.set_wire(stretch=[self.stretch_spinbox[i].value() for i in range(3)])

    def clear_stretch(self):
        """
        Clears the stretch values.
        """
        self.set_wire(stretch=[1.0, 1.0, 1.0])

        self.blockSignals(True)
        for i in range(3):
            self.stretch_spinbox[i].setValue(1.0)
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_rotational_symmetry(self):
        """
        Handles changes to rotational symmetry transform parameters.
        """
        self.set_wire(
            rotational_symmetry={
                "count": self.rotational_symmetry_count_spinbox.value(),
                "radius": self.rotational_symmetry_radius_spinbox.value(),
                "axis": {"X": 0, "Y": 1, "Z": 2}[self.rotational_symmetry_axis_combobox.currentText()]
            }
        )

    # ------------------------------------------------------------------------------------------------------------------

    def update_table(self):
        """
        Populates the wire base points table.
        """
        self.table.clear_rows()

        self.table.set_vertical_header([str(i + 1) for i in range(len(self.gui.model.wire.get_points_base()))])

        points = [[f"{round(col, 2):+0.02f}" for col in row] for row in self.gui.model.wire.get_points_base()]

        self.table.set_contents(points)

        self.base_total_label.setText(str(len(self.gui.model.wire.get_points_base())))

    def on_table_row_added(self):
        """
        Adds a wire base point after a row has been added to the table.
        """
        self.set_wire(points=[np.array([0, 0, 0])] + list(self.gui.model.wire.get_points_base()))

    def on_table_cell_edited(self, item):
        """
        Gets called after a wire point cell has been edited.

        @param item: QTableWidgetItem
        """
        try:
            value = float(item.text().replace(",", "."))
        except ValueError:
            value = 0.0

        points = self.gui.model.wire.get_points_base()
        points[item.row()][item.column()] = value
        self.set_wire(points=points)

    def on_table_row_deleted(self, index):
        """
        Deletes a wire base point after a row has been deleted from the table.

        @param index: Wire base point index
        """
        self.set_wire(points=np.delete(self.gui.model.wire.get_points_base(), index, axis=0))

    # ------------------------------------------------------------------------------------------------------------------

    def update_sliced_total_label(self):
        """
        Updates the total sliced points label.
        Called from calculation thread after the wire became valid.
        """
        if self.gui.model.wire.is_valid():
            self.sliced_total_label.setText(str(len(self.gui.model.wire.get_points_sliced())))
        else:
            self.sliced_total_label.setText("N/A")
