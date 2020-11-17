""" SamplingVolume_Widget module. """

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

import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QSizePolicy
from magneticalc.Constraint import Constraint
from magneticalc.Constraint_Editor import Constraint_Editor
from magneticalc.Debug import Debug
from magneticalc.IconLabel import IconLabel
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.ModelAccess import ModelAccess
from magneticalc.SamplingVolume import SamplingVolume
from magneticalc.Theme import Theme


class SamplingVolume_Widget(Groupbox):
    """ SamplingVolume_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    PaddingMin = -99
    PaddingMax = 99
    ResolutionMinimum = 1
    ResolutionMaximum = 100

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Sampling Volume")

        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Insert constraint editor, but don't fully initialize it yet
        self.constraint_editor = Constraint_Editor(self.gui)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        padding_icon_label = IconLabel("mdi.arrow-expand-all", "Padding")
        padding_clear_button = QPushButton()
        padding_clear_button.setIcon(qta.icon("fa.eraser"))
        padding_clear_button.clicked.connect(self.clear_padding)
        padding_icon_label.addWidget(padding_clear_button)
        padding_units_label = QLabel("cm")
        padding_units_label.setAlignment(Qt.AlignRight)
        padding_units_label.setFixedWidth(self.UnitsLabelWidth)
        padding_icon_label.addWidget(padding_units_label)
        self.addWidget(padding_icon_label)

        padding_layout = QHBoxLayout()
        padding_label = [None, None, None]
        self.padding_spinbox = [None, None, None]
        for i in range(3):
            self.padding_spinbox[i] = QSpinBox(self.gui)
            self.padding_spinbox[i].setMinimum(self.PaddingMin)
            self.padding_spinbox[i].setMaximum(self.PaddingMax)
            self.padding_spinbox[i].valueChanged.connect(self.update_padding)
            padding_label[i] = QLabel(["X", "Y", "Z"][i] + ":")
            padding_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            padding_layout.addWidget(padding_label[i], alignment=Qt.AlignVCenter)
            padding_layout.addWidget(self.padding_spinbox[i], alignment=Qt.AlignVCenter)
        self.addLayout(padding_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        constraints_icon_label = IconLabel("mdi.playlist-edit", "Constraints")
        constraint_shortcut_label = QLabel("⟨F3⟩")
        constraint_shortcut_label.setStyleSheet(f"font-size: 13px; color: {Theme.LightColor}")
        constraints_icon_label.addWidget(constraint_shortcut_label)

        constraint_edit_button = QPushButton()
        constraint_edit_button.setText("Edit …")
        constraint_edit_button.clicked.connect(self.open_constraint_editor)
        constraints_icon_label.addWidget(constraint_edit_button)

        self.addWidget(constraints_icon_label)

        total_constraints_layout = QHBoxLayout()
        total_constraints_label_left = QLabel("Total constraints:")
        total_constraints_label_left.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")
        self.total_constraints_label = QLabel("N/A")
        self.total_constraints_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.total_constraints_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_constraints_layout.addWidget(total_constraints_label_left, alignment=Qt.AlignVCenter)
        total_constraints_layout.addWidget(self.total_constraints_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_constraints_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("fa.th", "Resolution"))
        self.resolution_spinbox = QSpinBox(self.gui)
        self.resolution_spinbox.setMinimum(self.ResolutionMinimum)
        self.resolution_spinbox.setMaximum(self.ResolutionMaximum)
        self.resolution_spinbox.valueChanged.connect(
            lambda: self.set_sampling_volume(resolution=self.resolution_spinbox.value())
        )
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(self.resolution_spinbox, alignment=Qt.AlignVCenter)
        points_units_label = QLabel("Points / cm")
        points_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        resolution_layout.addWidget(points_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(resolution_layout)

        total_points_layout = QHBoxLayout()
        total_points_label_left = QLabel("Total sampling points:")
        total_points_label_left.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")
        self.total_points_label = QLabel("N/A")
        self.total_points_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.total_points_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_points_layout.addWidget(total_points_label_left, alignment=Qt.AlignVCenter)
        total_points_layout.addWidget(self.total_points_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_points_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the widget and the constraint editor
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        for i in range(3):
            self.padding_spinbox[i].setValue(self.gui.config.get_point("sampling_volume_padding")[i])

        self.resolution_spinbox.setValue(self.gui.config.get_int("sampling_volume_resolution"))

        self.blockSignals(False)

        # Re-initialize the constraint editor
        self.constraint_editor.reinitialize()

        # Initially load sampling volume from configuration
        self.set_sampling_volume(recalculate=False, invalidate_self=False)

    # ------------------------------------------------------------------------------------------------------------------

    def update_padding(self):
        """
        Updates padding.
        """
        if self.signalsBlocked():
            return

        self.set_sampling_volume(padding=[self.padding_spinbox[i].value() for i in range(3)])

    def clear_padding(self):
        """
        Clears the padding values.
        """
        self.set_sampling_volume(padding=[0, 0, 0])

        self.blockSignals(True)
        for i in range(3):
            self.padding_spinbox[i].setValue(0)
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_sampling_volume(
            self,
            padding=None,
            resolution: int = None,
            recalculate: bool = True,
            invalidate_self: bool = True
    ):
        """
        Sets the sampling volume. This will overwrite the currently set sampling volume in the model.
        Parameters may be left set to None in order to load their default value.

        @param resolution: Sampling volume _resolution
        @param padding: Padding (3D point)
        @param recalculate: Enable to trigger final re-calculation
        @param invalidate_self: Enable to invalidate the old sampling volume before setting a new one
        """
        if self.signalsBlocked():
            return

        with ModelAccess(self.gui, recalculate):

            resolution = self.gui.config.set_get_int("sampling_volume_resolution", resolution)

            self.gui.model.set_sampling_volume(SamplingVolume(resolution), invalidate_self=invalidate_self)

            self.readjust(padding)

            # Load sampling volume constraints from configuration
            for i, constraint in enumerate(self.constraint_editor.get_constraints()):

                constraint = self.gui.config.set_get_dict(
                    prefix=f"constraint_",
                    suffix=f"_{i}",
                    types=self.constraint_editor.Constraint_Types,
                    values=None
                )

                self.gui.model.sampling_volume.add_constraint(
                    Constraint(
                        constraint["norm"],
                        constraint["comparison"],
                        constraint["min"],
                        constraint["max"],
                        constraint["permeability"]
                    )
                )

            if recalculate:
                # The label resolution depends on the sampling volume resolution
                self.gui.sidebar_right.display_widget.update_label_resolution_combobox()

    # ------------------------------------------------------------------------------------------------------------------

    def readjust(self, padding=None):
        """
        Readjusts the sampling volume to the currently set wire bounds and padding.
        The parameter may be left set to None in order to load its default value.
        This also readjusts the minimum padding bounds in case the wire bounds have shrunk too far.

        @param padding: Padding (3D point), may be None to be read from configuration
        """
        Debug(self, ".readjust()")

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

    def update_labels(self):
        """
        Updates the labels.
        """
        if self.gui.model.sampling_volume.is_valid():
            self.total_points_label.setText(str(len(self.gui.model.sampling_volume.get_points())))
        else:
            self.total_points_label.setText("N/A")

        self.total_constraints_label.setText(str(len(self.constraint_editor.get_constraints())))

    # ------------------------------------------------------------------------------------------------------------------

    def open_constraint_editor(self):
        """
        Opens the constraint editor.
        Recalculates the sampling volume if the constraints changed.
        """

        self.constraint_editor.show()

        if self.constraint_editor.get_changed():

            self.set_sampling_volume()

            self.constraint_editor.clear_changed()
