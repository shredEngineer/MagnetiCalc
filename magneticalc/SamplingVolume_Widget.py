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
from magneticalc.Debug import Debug
from magneticalc.IconLabel import IconLabel
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.ModelAccess import ModelAccess
from magneticalc.SamplingVolume import SamplingVolume


class SamplingVolume_Widget(Groupbox):
    """ SamplingVolume_Widget class. """

    # Display settings
    UnitsLabelWidth = 26

    # Spinbox limits
    PaddingMin = -99
    PaddingMax = 99
    ResolutionMinimum = 1
    ResolutionMaximum = 50

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Sampling Volume")

        self.gui = gui

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
            self.padding_spinbox[i].setValue(self.gui.config.get_point("sampling_volume_padding")[i])
            self.padding_spinbox[i].valueChanged.connect(self.update_padding)
            padding_label[i] = QLabel(["X", "Y", "Z"][i] + ":")
            padding_label[i].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            padding_layout.addWidget(padding_label[i], alignment=Qt.AlignVCenter)
            padding_layout.addWidget(self.padding_spinbox[i], alignment=Qt.AlignVCenter)
        self.addLayout(padding_layout)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(HLine())

        self.addWidget(IconLabel("fa.th", "Resolution"))
        resolution_spinbox = QSpinBox(self.gui)
        resolution_spinbox.setMinimum(self.ResolutionMinimum)
        resolution_spinbox.setMaximum(self.ResolutionMaximum)
        resolution_spinbox.setValue(self.gui.config.get_int("sampling_volume_resolution"))
        resolution_spinbox.valueChanged.connect(
            lambda: self.set_sampling_volume(resolution=resolution_spinbox.value())
        )
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(resolution_spinbox, alignment=Qt.AlignVCenter)
        points_units_label = QLabel("Points / cm")
        points_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        resolution_layout.addWidget(points_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(resolution_layout)

        total_layout = QHBoxLayout()
        total_label_left = QLabel("Total constrained points:")
        total_label_left.setStyleSheet("""
            color: #555555;
            font-style: italic;
        """)
        self.total_label = QLabel("")
        self.total_label.setStyleSheet("""
            color: #2a7db0;
        """)
        self.total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_layout.addWidget(total_label_left, alignment=Qt.AlignVCenter)
        total_layout.addWidget(self.total_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_layout)

        # ToDo: Add a table to add, edit and remove sampling volume constraints

        # Initially load sampling volume from configuration
        self.set_sampling_volume(recalculate=False)

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
            resolution=None,
            recalculate=True
    ):
        """
        Sets the sampling volume. This will overwrite the currently set sampling volume in the model.
        Parameters may be left set to None in order to load their default value.

        @param resolution: Sampling volume _resolution
        @param padding: Padding (3D point)
        @param recalculate: Enable to trigger final re-calculation (boolean)
        """
        with ModelAccess(self.gui, recalculate):

            resolution = self.gui.config.set_get_int("sampling_volume_resolution", resolution)

            self.gui.model.set_sampling_volume(SamplingVolume(resolution))

            self.readjust(padding)

            # ToDo: Add support for sampling volume constraints, e.g.:
            # self.gui.model.sampling_volume.add_constraint(lambda p: -1.5 <= p["z"] <= 1.5)
            # self.gui.model.sampling_volume.add_constraint(lambda p: 2 <= p["radius_xy"] <= 4.5)
            # self.gui.model.sampling_volume.add_constraint(lambda p: p["y"] == 0)
            # self.gui.model.sampling_volume.add_constraint(lambda p: p["radius"] <= 3)

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

        self.gui.model.sampling_volume.set_padding(*padding)

    # ------------------------------------------------------------------------------------------------------------------

    def update_total_label(self):
        """
        Updates the total sampling volume points label.
        Called from calculation thread after the sampling volume became valid.
        """
        if self.gui.model.sampling_volume.is_valid():
            self.total_label.setText(str(len(self.gui.model.sampling_volume.get_points())))
        else:
            self.total_label.setText("N/A")
