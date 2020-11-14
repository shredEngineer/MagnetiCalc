""" Parameters_Widget module. """

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
from si_prefix import si_format
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from magneticalc.Groupbox import Groupbox
from magneticalc.Parameters import Parameters
from magneticalc.Theme import Theme


class Parameters_Widget(Groupbox):
    """ Parameters_Widget class. """

    # Formatting settings
    ValuePrecision = 1

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Parameters")

        self.gui = gui

        # Assign the Parameters container class
        self.gui.model.set_parameters(Parameters(), invalidate_self=False)

        # --------------------------------------------------------------------------------------------------------------

        results_layout = QHBoxLayout()
        results_left = QVBoxLayout()
        results_middle = QVBoxLayout()
        results_right = QVBoxLayout()
        results_layout.addLayout(results_left)
        results_layout.addLayout(results_middle)
        results_layout.addLayout(results_right)
        self.addLayout(results_layout)

        # --------------------------------------------------------------------------------------------------------------

        wire_length_label = QLabel("Wire length:")
        wire_length_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_left.addWidget(wire_length_label)

        self.wire_length_value_label = QLabel("")
        self.wire_length_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.wire_length_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.wire_length_value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_middle.addWidget(self.wire_length_value_label, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.wire_length_units_label = QLabel("N/A")
        self.wire_length_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.wire_length_units_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.wire_length_units_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        results_right.addWidget(self.wire_length_units_label, alignment=Qt.AlignVCenter)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        magnetic_dipole_moment_label = QLabel("Magnetic Dipole Moment:")
        magnetic_dipole_moment_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_left.addWidget(magnetic_dipole_moment_label)

        self.magnetic_dipole_moment_value_label = QLabel("")
        self.magnetic_dipole_moment_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.magnetic_dipole_moment_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.magnetic_dipole_moment_value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_middle.addWidget(self.magnetic_dipole_moment_value_label, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.magnetic_dipole_moment_units_label = QLabel("N/A")
        self.magnetic_dipole_moment_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.magnetic_dipole_moment_units_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.magnetic_dipole_moment_units_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        results_right.addWidget(self.magnetic_dipole_moment_units_label, alignment=Qt.AlignVCenter)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        energy_label = QLabel("Energy:")
        energy_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_left.addWidget(energy_label)

        self.energy_value_label = QLabel("")
        self.energy_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.energy_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.energy_value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_middle.addWidget(self.energy_value_label, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.energy_units_label = QLabel("N/A")
        self.energy_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.energy_units_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.energy_units_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        results_right.addWidget(self.energy_units_label, alignment=Qt.AlignVCenter)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self_inductance_label = QLabel("Self-inductance:")
        self_inductance_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_left.addWidget(self_inductance_label)

        self.self_inductance_value_label = QLabel("")
        self.self_inductance_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.self_inductance_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.self_inductance_value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_middle.addWidget(self.self_inductance_value_label, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.self_inductance_units_label = QLabel("N/A")
        self.self_inductance_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.self_inductance_units_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.self_inductance_units_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        results_right.addWidget(self.self_inductance_units_label, alignment=Qt.AlignVCenter)

    # ------------------------------------------------------------------------------------------------------------------

    def update_labels(self):
        """
        Updates the labels.
        """
        if self.gui.model.parameters.is_valid():

            self.wire_length_value_label.setText(f"{self.gui.model.wire.get_length():.2f}")
            self.wire_length_value_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")
            self.wire_length_units_label.setText("cm")
            self.wire_length_units_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")

            if self.gui.model.field.get_type() == 1:

                # Field is B-field (flux density)

                energy_value = self.gui.model.parameters.get_energy()
                if np.isnan(energy_value):
                    energy_value = "NaN "
                else:
                    energy_value = si_format(energy_value, precision=self.ValuePrecision) + "J"
                self.energy_value_label.setText(energy_value.split(" ")[0])
                self.energy_value_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")
                self.energy_units_label.setText(energy_value.split(" ")[1])
                self.energy_units_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")

                self_inductance_value = self.gui.model.parameters.get_self_inductance()
                if np.isnan(self_inductance_value):
                    self_inductance_value = "NaN "
                else:
                    self_inductance_value = si_format(self_inductance_value, precision=self.ValuePrecision) + "H"
                self.self_inductance_value_label.setText(self_inductance_value.split(" ")[0])
                self.self_inductance_value_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")
                self.self_inductance_units_label.setText(self_inductance_value.split(" ")[1])
                self.self_inductance_units_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")

                magnetic_dipole_moment_value = self.gui.model.parameters.get_magnetic_dipole_moment()
                if np.isnan(magnetic_dipole_moment_value):
                    magnetic_dipole_moment_value = "NaN "
                else:
                    magnetic_dipole_moment_value = si_format(
                        magnetic_dipole_moment_value, precision=self.ValuePrecision
                    ) + "Am²"
                self.magnetic_dipole_moment_value_label.setText(magnetic_dipole_moment_value.split(" ")[0])
                self.magnetic_dipole_moment_value_label.setStyleSheet(
                    f"color: {Theme.PrimaryColor}; font-weight: bold;"
                )
                self.magnetic_dipole_moment_units_label.setText(magnetic_dipole_moment_value.split(" ")[1])
                self.magnetic_dipole_moment_units_label.setStyleSheet(
                    f"color: {Theme.PrimaryColor}; font-weight: bold;"
                )

            else:

                # Field is A-field (vector potential)

                self.energy_value_label.setText("")
                self.energy_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
                self.energy_units_label.setText("N/A")
                self.energy_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

                self.self_inductance_value_label.setText("")
                self.self_inductance_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
                self.self_inductance_units_label.setText("N/A")
                self.self_inductance_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

                self.magnetic_dipole_moment_value_label.setText("")
                self.magnetic_dipole_moment_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
                self.magnetic_dipole_moment_units_label.setText("N/A")
                self.magnetic_dipole_moment_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

        else:

            self.wire_length_value_label.setText("")
            self.wire_length_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
            self.wire_length_units_label.setText("N/A")
            self.wire_length_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

            self.energy_value_label.setText("")
            self.energy_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
            self.energy_units_label.setText("N/A")
            self.energy_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

            self.self_inductance_value_label.setText("")
            self.self_inductance_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
            self.self_inductance_units_label.setText("N/A")
            self.self_inductance_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

            self.magnetic_dipole_moment_value_label.setText("")
            self.magnetic_dipole_moment_value_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
            self.magnetic_dipole_moment_units_label.setText("N/A")
            self.magnetic_dipole_moment_units_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
