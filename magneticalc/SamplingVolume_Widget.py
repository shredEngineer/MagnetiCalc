""" SamplingVolume_Widget module. """

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
from typing import Optional, List, Tuple
import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QSizePolicy
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.QLabel2 import QLabel2
from magneticalc.QPushButton2 import QPushButton2
from magneticalc.QSpinBox2 import QSpinBox2
from magneticalc.Comparison_Types import comparison_type_from_str
from magneticalc.Constraint import Constraint
from magneticalc.Constraint_Editor import Constraint_Editor
from magneticalc.Debug import Debug
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Norm_Types import norm_type_from_str
from magneticalc.OverridePadding_Dialog import OverridePadding_Dialog
from magneticalc.SamplingVolume import SamplingVolume
from magneticalc.Theme import Theme


class SamplingVolume_Widget(QGroupBox2):
    """ SamplingVolume_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    PaddingMin = -1000
    PaddingMax = +1000

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

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Sampling Volume")
        Debug(self, ": Init", init=True)
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Insert constraint editor, but don't fully initialize it yet
        self.constraint_editor = Constraint_Editor(self.gui)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        padding_icon_label = QIconLabel("Padding", "mdi.arrow-expand-all")
        padding_override_button = QPushButton2("  Override …  ", "", self.override_padding)
        padding_icon_label.addWidget(padding_override_button)
        padding_icon_label.addWidget(QPushButton2("", "fa.eraser", self.clear_padding))
        padding_icon_label.addWidget(QLabel2("cm", align_right=True, width=self.UnitsLabelWidth))
        self.addLayout(padding_icon_label)

        self.padding_widget = QWidget()
        padding_layout = QHBoxLayout()
        self.padding_spinbox = []
        for i in range(3):
            padding_spinbox = QSpinBox2(
                minimum=self.PaddingMin,
                maximum=self.PaddingMax,
                value=0,
                value_changed=self.update_padding
            )
            self.padding_spinbox.append(padding_spinbox)
            padding_layout.addWidget(QLabel2(["X", "Y", "Z"][i] + ":", expand=False))
            padding_layout.addWidget(self.padding_spinbox[i])
        self.padding_widget.setLayout(padding_layout)
        self.addWidget(self.padding_widget)

        total_extent_layout = QHBoxLayout()
        self.total_extent_label = QLabel2("N/A", color=Theme.MainColor, align_right=True)
        total_extent_layout.addWidget(QLabel2("Total extent:", italic=True, color=Theme.LiteColor))
        total_extent_layout.addWidget(self.total_extent_label)
        self.addLayout(total_extent_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        constraints_icon_label = QIconLabel("Constraints", "mdi.playlist-edit")
        constraints_icon_label.addWidget(QLabel2("⟨F3⟩", font_size="13px", color=Theme.LiteColor, expand=False))
        constraints_icon_label.addWidget(QPushButton2("Edit …", "", self.open_constraint_editor))
        self.addLayout(constraints_icon_label)

        total_constraints_layout = QHBoxLayout()
        self.total_constraints_label = QLabel2("N/A", color=Theme.MainColor, align_right=True)
        total_constraints_layout.addWidget(QLabel2("Total constraints:", italic=True, color=Theme.LiteColor))
        total_constraints_layout.addWidget(self.total_constraints_label)
        self.addLayout(total_constraints_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Resolution", "fa.th"))

        self.resolution_combobox = QComboBox()
        self.resolution_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(self.resolution_combobox)
        self.resolution_units_label = QLabel2(" Points / cm", expand=False)
        resolution_layout.addWidget(self.resolution_units_label)
        self.addLayout(resolution_layout)

        # Populate resolution combobox
        for i, value in enumerate(self.ResolutionOptionsDict):
            self.resolution_combobox.addItem(str(value))
        self.resolution_combobox.currentIndexChanged.connect(  # type: ignore
            lambda: self.set_sampling_volume(
                _resolution_exponent_=self.ResolutionOptionsDict.get(
                    self.resolution_combobox.currentText(),
                    0
                )
            )
        )

        total_points_layout = QHBoxLayout()
        self.total_points_label = QLabel2("N/A", color=Theme.MainColor, align_right=True)
        total_points_layout.addWidget(QLabel2("Total sampling points:", italic=True, color=Theme.LiteColor))
        total_points_layout.addWidget(self.total_points_label)
        self.addLayout(total_points_layout)

    def reload(self) -> None:
        """
        Reloads the widget.
        """
        Debug(self, ".reload()", refresh=True)

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
        self.constraint_editor.reload()

        # Initially load sampling volume from configuration
        self.set_sampling_volume(recalculate=False, invalidate=False)

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

        if self.gui.model.sampling_volume.valid:
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

    def update_controls(self) -> None:
        """
        Updates the controls.
        """
        Debug(self, ".update_controls()", refresh=True)

        self.padding_widget.setEnabled(not self.gui.config.get_bool("sampling_volume_override_padding"))

        self.indicate_valid(self.gui.model.sampling_volume.valid)

    # ------------------------------------------------------------------------------------------------------------------

    def update_padding(self) -> None:
        """
        Updates padding.
        """
        if self.signalsBlocked():
            return

        Debug(self, ".update_padding()")

        self.set_sampling_volume(_padding_=[self.padding_spinbox[i].value() for i in range(3)])

    def clear_padding(self) -> None:
        """
        Clears the padding values.
        """
        Debug(self, ".clear_padding()")

        self.gui.config.set_bool("sampling_volume_override_padding", False)
        self.gui.config.set_points("sampling_volume_bounding_box", [np.zeros(3), np.zeros(3)])

        self.set_sampling_volume(_padding_=[0, 0, 0])

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
            _override_padding_=True,
            _bounding_box_=(
                np.array([dialog.bounds_min_spinbox[i].value() for i in range(3)]),
                np.array([dialog.bounds_max_spinbox[i].value() for i in range(3)])
            )
        )

        self.update_controls()

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

    # ------------------------------------------------------------------------------------------------------------------

    def set_sampling_volume(
            self,
            _resolution_exponent_: Optional[int] = None,
            _label_resolution_exponent_: Optional[int] = None,
            _padding_: Optional[List] = None,
            _override_padding_: Optional[bool] = None,
            _bounding_box_: Optional[Tuple[np.ndarray, np.ndarray]] = None,
            invalidate: bool = True,
            recalculate: bool = True
    ) -> None:
        """
        Sets the sampling volume. This will overwrite the currently set sampling volume in the model.
        Any underscored parameter may be left set to None in order to load its default value.

        @param _resolution_exponent_: Sampling volume resolution exponent
        @param _label_resolution_exponent_: Sampling volume label resolution exponent
        @param _padding_: Padding (3D point)
        @param _override_padding_: Enable to override padding instead, setting the bounding box directly
        @param _bounding_box_: Bounding box (used in conjunction with override_padding)
        @param invalidate: Enable to invalidate this model hierarchy level
        @param recalculate: Enable to trigger final re-calculation
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_sampling_volume()")

        with ModelAccess(self.gui, recalculate):

            resolution_exponent = self.gui.config.set_get_int(
                "sampling_volume_resolution_exponent",
                _resolution_exponent_
            )

            label_resolution_exponent = self.gui.config.set_get_int(
                "sampling_volume_label_resolution_exponent",
                _label_resolution_exponent_
            )

            resolution = np.power(2.0, resolution_exponent)
            label_resolution = np.power(2.0, label_resolution_exponent)

            self.gui.model.set_sampling_volume(
                invalidate=invalidate,
                resolution=resolution,
                label_resolution=label_resolution
            )

            self.readjust(_padding_=_padding_, _override_padding_=_override_padding_, _bounding_box_=_bounding_box_)

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

                # This forces updating the number of constraints if the sampling volume is already invalidated
                if not self.gui.model.sampling_volume.valid:
                    self.update()

    # ------------------------------------------------------------------------------------------------------------------

    def readjust(
            self,
            _padding_: Optional[List] = None,
            _override_padding_: Optional[bool] = None,
            _bounding_box_: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> None:
        """
        Readjusts the sampling volume to the currently set wire bounds and padding.
        This also readjusts the minimum padding bounds in case the wire bounds have shrunk too far.

        Padding may also be overridden instead, setting the bounding box directly.

        Any underscored parameter may be left set to None in order to load its default value.

        @param _padding_: Padding (3D point)
        @param _override_padding_: Enable to override padding instead, setting the bounding box directly
        @param _bounding_box_: Bounding box (used in conjunction with override_padding)
        """
        Debug(self, ".readjust()")

        override_padding = self.gui.config.set_get_bool("sampling_volume_override_padding", _override_padding_)
        bounding_box = self.gui.config.set_get_points("sampling_volume_bounding_box", _bounding_box_)

        if override_padding:

            self.gui.model.sampling_volume.set_bounds_nearest(*bounding_box)

        else:

            self.gui.model.sampling_volume.set_bounds_nearest(*self.gui.model.wire.get_bounds())

            bounds_min, bounds_max = self.gui.model.sampling_volume.get_bounds()

            padding = self.gui.config.set_get_point("sampling_volume_padding", _padding_)

            # Adjust padding values if they are now outside the new minimum padding bounds
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
