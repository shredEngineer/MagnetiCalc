""" SamplingVolume_Widget module. """

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
from typing import Optional, List, Tuple
import numpy as np
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QComboBox, QSizePolicy, QWidget
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.Comparison_Types import comparison_type_from_str
from magneticalc.Constraint import Constraint
from magneticalc.Constraint_Editor import Constraint_Editor
from magneticalc.Debug import Debug
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Norm_Types import norm_type_from_str
from magneticalc.OverridePadding_Dialog import OverridePadding_Dialog
from magneticalc.SamplingVolume import SamplingVolume
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class SamplingVolume_Widget(QGroupBox2):
    """ SamplingVolume_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    PaddingMin = -1e+3
    PaddingMax = +1e+3

    # Resolution options
    ResolutionOptionsDict = {
        "256"       : 8,
        "128"       : 7,
        "64"        : 6,
        "32"        : 5,
        "16"        : 4,
        "8"         : 3,
        "4"         : 2,
        "2"         : 1,
        "1"         : 0,
        "1 / 2"     : -1,
        "1 / 4"     : -2,
        "1 / 8"     : -3,
        "1 / 16"    : -4,
        "1 / 32"    : -5,
        "1 / 64"    : -6,
        "1 / 128"   : -7,
        "1 / 256"   : -8,
    }

    def __init__(self, gui: GUI) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Sampling Volume")
        Debug(self, ": Init")
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Insert constraint editor, but don't fully initialize it yet
        self.constraint_editor = Constraint_Editor(self.gui)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        padding_icon_label = QIconLabel("Padding", "mdi.arrow-expand-all")
        padding_override_button = QPushButton(" Override … ")
        # noinspection PyUnresolvedReferences
        padding_override_button.clicked.connect(self.override_padding)
        padding_override_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        padding_icon_label.addWidget(padding_override_button)
        padding_clear_button = QPushButton()
        padding_clear_button.setIcon(qta.icon("fa.eraser"))
        # noinspection PyUnresolvedReferences
        padding_clear_button.clicked.connect(self.clear_padding)
        padding_icon_label.addWidget(padding_clear_button)
        padding_units_label = QLabel("cm")
        padding_units_label.setAlignment(Qt.AlignRight)
        padding_units_label.setFixedWidth(self.UnitsLabelWidth)
        padding_icon_label.addWidget(padding_units_label)
        self.addLayout(padding_icon_label)

        self.padding_widget = QWidget()
        padding_layout = QHBoxLayout()
        padding_label = [None, None, None]
        self.padding_spinbox = [None, None, None]
        for i in range(3):
            self.padding_spinbox[i] = QSpinBox(self.gui)
            self.padding_spinbox[i].setMinimum(self.PaddingMin)
            self.padding_spinbox[i].setMaximum(self.PaddingMax)
            # noinspection PyUnresolvedReferences
            self.padding_spinbox[i].valueChanged.connect(self.update_padding)
            padding_label[i] = QLabel(["X", "Y", "Z"][i] + ":")
            padding_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            padding_layout.addWidget(padding_label[i], alignment=Qt.AlignVCenter)
            padding_layout.addWidget(self.padding_spinbox[i], alignment=Qt.AlignVCenter)
        self.padding_widget.setLayout(padding_layout)
        self.addWidget(self.padding_widget)

        total_extent_layout = QHBoxLayout()
        total_extent_label_left = QLabel("Total extent:")
        total_extent_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.total_extent_label = QLabel("N/A")
        self.total_extent_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.total_extent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_extent_layout.addWidget(total_extent_label_left, alignment=Qt.AlignVCenter)
        total_extent_layout.addWidget(self.total_extent_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_extent_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        constraints_icon_label = QIconLabel("Constraints", "mdi.playlist-edit")
        constraint_shortcut_label = QLabel("⟨F3⟩")
        constraint_shortcut_label.setStyleSheet(f"font-size: 13px; color: {Theme.LiteColor}")
        constraints_icon_label.addWidget(constraint_shortcut_label)

        constraint_edit_button = QPushButton("Edit …")
        # noinspection PyUnresolvedReferences
        constraint_edit_button.clicked.connect(self.open_constraint_editor)
        constraints_icon_label.addWidget(constraint_edit_button)

        self.addLayout(constraints_icon_label)

        total_constraints_layout = QHBoxLayout()
        total_constraints_label_left = QLabel("Total constraints:")
        total_constraints_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.total_constraints_label = QLabel("N/A")
        self.total_constraints_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.total_constraints_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_constraints_layout.addWidget(total_constraints_label_left, alignment=Qt.AlignVCenter)
        total_constraints_layout.addWidget(self.total_constraints_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_constraints_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Resolution", "fa.th"))

        self.resolution_combobox = QComboBox()
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(self.resolution_combobox, alignment=Qt.AlignVCenter)
        self.resolution_units_label = QLabel(" Points / cm")
        self.resolution_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        resolution_layout.addWidget(self.resolution_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(resolution_layout)

        # Populate resolution combobox
        for i, value in enumerate(self.ResolutionOptionsDict):
            self.resolution_combobox.addItem(str(value))
        # noinspection PyUnresolvedReferences
        self.resolution_combobox.currentIndexChanged.connect(
            lambda: self.set_sampling_volume(
                resolution_exponent=self.ResolutionOptionsDict.get(
                    self.resolution_combobox.currentText(),
                    0
                )
            )
        )

        total_points_layout = QHBoxLayout()
        total_points_label_left = QLabel("Total sampling points:")
        total_points_label_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.total_points_label = QLabel("N/A")
        self.total_points_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.total_points_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_points_layout.addWidget(total_points_label_left, alignment=Qt.AlignVCenter)
        total_points_layout.addWidget(self.total_points_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_points_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self) -> None:
        """
        Re-initializes the widget and the constraint editor
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        for i in range(3):
            self.padding_spinbox[i].setValue(self.gui.config.get_point("sampling_volume_padding")[i])

        # Set default resolution if it is not available anymore
        target = self.gui.config.get_int("sampling_volume_resolution_exponent")
        if target not in self.ResolutionOptionsDict.values():
            Debug(self, f": WARNING: Invalid: sampling_volume_resolution_exponent = {target}", warning=True)
            self.gui.config.set_int("sampling_volume_resolution_exponent", 0)

        # Select the resolution
        target = self.gui.config.get_int("sampling_volume_resolution_exponent")
        for i, value in enumerate(self.ResolutionOptionsDict.values()):
            if value == target:
                self.resolution_combobox.setCurrentIndex(i)

        self.blockSignals(False)

        # Re-initialize the constraint editor
        self.constraint_editor.reinitialize()

        # Initially load sampling volume from configuration
        self.set_sampling_volume(recalculate=False, invalidate_self=False)

    # ------------------------------------------------------------------------------------------------------------------

    def update_padding(self) -> None:
        """
        Updates padding.
        """
        if self.signalsBlocked():
            return

        Debug(self, ".update_padding()")

        self.set_sampling_volume(padding=[self.padding_spinbox[i].value() for i in range(3)])

    def clear_padding(self) -> None:
        """
        Clears the padding values.
        """
        Debug(self, ".clear_padding()")

        self.gui.config.set_bool("sampling_volume_override_padding", False)
        self.gui.config.set_points("sampling_volume_bounding_box", [np.zeros(3), np.zeros(3)])

        self.set_sampling_volume(padding=[0, 0, 0])

        self.blockSignals(True)
        for i in range(3):
            self.padding_spinbox[i].setValue(0)
        self.blockSignals(False)

    def override_padding(self) -> None:
        """
        Override padding, setting the bounding box directly.
        """
        Debug(self, ".override_padding()")

        dialog = OverridePadding_Dialog(self.gui)
        dialog.show()

        if not dialog.success:
            return

        # This needlessly also clears the override padding and bounding box config, but that's acceptable.
        self.clear_padding()

        self.set_sampling_volume(
            override_padding=True,
            bounding_box=[
                [dialog.bounds_min_spinbox[i].value() for i in range(3)],
                [dialog.bounds_max_spinbox[i].value() for i in range(3)]
            ]
        )

        self.update_controls()

    # ------------------------------------------------------------------------------------------------------------------

    def set_sampling_volume(
            self,
            resolution_exponent: Optional[int] = None,
            label_resolution_exponent: Optional[int] = None,
            padding: Optional[List] = None,
            override_padding: Optional[bool] = None,
            bounding_box: List[List] = None,
            recalculate: bool = True,
            invalidate_self: bool = True
    ) -> None:
        """
        Sets the sampling volume. This will overwrite the currently set sampling volume in the model.
        Parameters may be left set to None in order to load their default value.

        @param resolution_exponent: Sampling volume resolution exponent
        @param label_resolution_exponent: Sampling volume label resolution exponent
        @param padding: Padding (3D point)
        @param override_padding: Enable to override padding instead, setting the bounding box directly
        @param bounding_box: Bounding box (used in conjunction with override_padding)
        @param recalculate: Enable to trigger final re-calculation
        @param invalidate_self: Enable to invalidate the old sampling volume before setting a new one
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_sampling_volume()")

        with ModelAccess(self.gui, recalculate):

            resolution_exponent = self.gui.config.set_get_int(
                "sampling_volume_resolution_exponent",
                resolution_exponent
            )

            label_resolution_exponent = self.gui.config.set_get_int(
                "sampling_volume_label_resolution_exponent",
                label_resolution_exponent
            )

            resolution = np.power(2.0, resolution_exponent)
            label_resolution = np.power(2.0, label_resolution_exponent)

            self.gui.model.set_sampling_volume(
                SamplingVolume(resolution=resolution, label_resolution=label_resolution),
                invalidate_self=invalidate_self
            )

            self.readjust(padding, override_padding, bounding_box)

            # Load sampling volume constraints from configuration
            for constraint in self.constraint_editor.get_constraints():
                Debug(self, f".set_sampling_volume(): Loading Constraint: {constraint}")
                self.gui.model.sampling_volume.add_constraint(
                    Constraint(
                        norm_type_from_str(constraint["norm"]),
                        comparison_type_from_str(constraint["comparison"]),
                        constraint["min"],
                        constraint["max"],
                        constraint["permeability"]
                    )
                )

            if recalculate:
                # The display widget depends on the sampling volume
                self.gui.sidebar_right.display_widget.update()

    # ------------------------------------------------------------------------------------------------------------------

    def readjust(
            self,
            padding: Optional[List] = None,
            override_padding: Optional[bool] = None,
            bounding_box: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> None:
        """
        Readjusts the sampling volume to the currently set wire bounds and padding.
        This also readjusts the minimum padding bounds in case the wire bounds have shrunk too far.

        Padding may also be overridden instead, setting the bounding box directly.

        Parameters may be left set to None in order to load their default value.

        @param padding: Padding (3D point)
        @param override_padding: Enable to override padding instead, setting the bounding box directly
        @param bounding_box: Bounding box (used in conjunction with override_padding)
        """
        Debug(self, ".readjust()")

        override_padding = self.gui.config.set_get_bool("sampling_volume_override_padding", override_padding)
        bounding_box = self.gui.config.set_get_points("sampling_volume_bounding_box", bounding_box)

        if override_padding:

            self.gui.model.sampling_volume.set_bounds_nearest(*bounding_box)

        else:

            self.gui.model.sampling_volume.set_bounds_nearest(*self.gui.model.wire.get_bounds())

            bounds_min, bounds_max = self.gui.model.sampling_volume.get_bounds()

            # Adjust padding values if they are now outside the new minimum padding bounds
            padding = self.gui.config.set_get_point("sampling_volume_padding", padding)
            padding_adjusted = False
            for i in range(3):
                if bounds_min[i] > self.padding_spinbox[i].value():
                    padding[i] = bounds_min[i]
                    padding_adjusted = True
            if padding_adjusted:
                Debug(self, ".readjust(): Adjusted padding values to new minimum padding bounds")
                self.gui.config.set_point("sampling_volume_padding", padding)

            self.blockSignals(True)
            for i in range(3):
                self.padding_spinbox[i].setMinimum(bounds_min[i])
            self.blockSignals(False)

            self.gui.model.sampling_volume.set_padding_nearest(padding)

    # ------------------------------------------------------------------------------------------------------------------

    def update(self) -> None:
        """
        Updates the widget.
        """
        Debug(self, ".update()")

        self.update_controls()
        self.update_labels()

    def update_controls(self) -> None:
        """
        Updates the controls.
        """
        Debug(self, ".update_controls()")

        override_padding = self.gui.config.get_bool("sampling_volume_override_padding")
        self.padding_widget.setEnabled(not override_padding)

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()")

        if self.gui.model.sampling_volume.is_valid():
            self.total_extent_label.setText(
                " × ".join([f"{extent:.0f}" for extent in self.gui.model.sampling_volume.get_extent()]) + " cm³"
            )
            self.total_points_label.setText(
                str(self.gui.model.sampling_volume.get_points_count())
            )
        else:
            self.total_extent_label.setText("N/A")
            self.total_points_label.setText("N/A")

        self.total_constraints_label.setText(str(self.constraint_editor.get_count()))

    # ------------------------------------------------------------------------------------------------------------------

    def open_constraint_editor(self) -> None:
        """
        Opens the constraint editor.
        Recalculates the sampling volume if the constraints changed.
        """
        Debug(self, ".open_constraint_editor()")

        self.constraint_editor.show()

        if self.constraint_editor.get_changed():

            self.set_sampling_volume()

            self.constraint_editor.clear_changed()
