""" Parameters_Widget module. """

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
import numpy as np
from si_prefix import si_format
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QLabel2 import QLabel2
from magneticalc.Debug import Debug
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.Parameters import Parameters
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Parameters_Widget(QGroupBox2):
    """ Parameters_Widget class. """

    # Formatting settings
    ValuePrecision = 1

    def __init__(self, gui: GUI) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Parameters")
        Debug(self, ": Init")
        self.gui = gui

        # Assign the "Parameters" container class
        self.gui.model.set_parameters(Parameters(), invalidate_self=False)

        results_layout = QHBoxLayout()
        results_left = QVBoxLayout()
        results_middle = QVBoxLayout()
        results_right = QVBoxLayout()
        results_layout.addLayout(results_left)
        results_layout.addLayout(results_middle)
        results_layout.addLayout(results_right)
        self.addLayout(results_layout)

        results_left.addWidget(QLabel2("Wire length:"))
        self.wire_length_value_label = QLabel2("", color=Theme.MainColor, align_right=True)
        results_middle.addWidget(self.wire_length_value_label)
        self.wire_length_units_label = QLabel2("N/A", color=Theme.MainColor, expand=False)
        results_right.addWidget(self.wire_length_units_label)

        results_left.addWidget(QLabel2("Magnetic Dipole Moment:"))
        self.magnetic_dipole_moment_value_label = QLabel2("", color=Theme.MainColor, align_right=True)
        results_middle.addWidget(self.magnetic_dipole_moment_value_label)
        self.magnetic_dipole_moment_units_label = QLabel2("N/A", color=Theme.MainColor, expand=False)
        results_right.addWidget(self.magnetic_dipole_moment_units_label)

        results_left.addWidget(QLabel2("Energy:"))
        self.energy_value_label = QLabel2("", color=Theme.MainColor, align_right=True)
        results_middle.addWidget(self.energy_value_label)
        self.energy_units_label = QLabel2("N/A", color=Theme.MainColor, expand=False)
        results_right.addWidget(self.energy_units_label)

        results_left.addWidget(QLabel2("Self-inductance:"))
        self.self_inductance_value_label = QLabel2("", color=Theme.MainColor, align_right=True)
        results_middle.addWidget(self.self_inductance_value_label)
        self.self_inductance_units_label = QLabel2("N/A", color=Theme.MainColor, expand=False)
        results_right.addWidget(self.self_inductance_units_label)

    # ------------------------------------------------------------------------------------------------------------------

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()")

        if self.gui.model.parameters.is_valid():

            self.wire_length_value_label.set(
                f"{self.gui.model.wire.get_length():.2f}", color=Theme.MainColor, bold=True
            )
            self.wire_length_units_label.set("cm", color=Theme.MainColor, bold=True)

            if self.gui.model.field.get_type() == A_FIELD:

                self.energy_value_label.set("", color=Theme.MainColor)
                self.energy_units_label.set("N/A", color=Theme.MainColor)

                self.self_inductance_value_label.set("", color=Theme.MainColor)
                self.self_inductance_units_label.set("N/A", color=Theme.MainColor)

                self.magnetic_dipole_moment_value_label.set("", color=Theme.MainColor)
                self.magnetic_dipole_moment_units_label.set("N/A", color=Theme.MainColor)

            elif self.gui.model.field.get_type() == B_FIELD:

                energy_value = self.gui.model.parameters.get_energy()
                if np.isnan(energy_value):
                    energy_value = "NaN NaN"
                else:
                    energy_value = si_format(
                        energy_value,
                        precision=self.ValuePrecision,
                        exp_format_str="{value}e{expof10} "
                    ) + "J"
                self.energy_value_label.set(energy_value.split(" ")[0], color=Theme.MainColor, bold=True)
                self.energy_units_label.set(energy_value.split(" ")[1], color=Theme.MainColor, bold=True)

                self_inductance_value = self.gui.model.parameters.get_self_inductance()
                if np.isnan(self_inductance_value):
                    self_inductance_value = "NaN NaN"
                else:
                    self_inductance_value = si_format(
                        self_inductance_value,
                        precision=self.ValuePrecision,
                        exp_format_str="{value}e{expof10} "
                    ) + "H"
                self.self_inductance_value_label.set(
                    self_inductance_value.split(" ")[0], color=Theme.MainColor, bold=True
                )
                self.self_inductance_units_label.set(
                    self_inductance_value.split(" ")[1], color=Theme.MainColor, bold=True)

                magnetic_dipole_moment_value = self.gui.model.parameters.get_magnetic_dipole_moment()
                if np.isnan(magnetic_dipole_moment_value):
                    magnetic_dipole_moment_value = "NaN NaN"
                else:
                    magnetic_dipole_moment_value = si_format(
                        magnetic_dipole_moment_value,
                        precision=self.ValuePrecision,
                        exp_format_str="{value}e{expof10} "
                    ) + "A·m²"
                self.magnetic_dipole_moment_value_label.set(
                    magnetic_dipole_moment_value.split(" ")[0], color=Theme.MainColor, bold=True
                )
                self.magnetic_dipole_moment_units_label.set(
                    magnetic_dipole_moment_value.split(" ")[1], color=Theme.MainColor, bold=True
                )

        else:

            self.wire_length_value_label.set("", color=Theme.MainColor)
            self.wire_length_units_label.set("N/A", color=Theme.MainColor)

            self.energy_value_label.set("", color=Theme.MainColor)
            self.energy_units_label.set("N/A", color=Theme.MainColor)

            self.self_inductance_value_label.set("", color=Theme.MainColor)
            self.self_inductance_units_label.set("N/A", color=Theme.MainColor)

            self.magnetic_dipole_moment_value_label.set("", color=Theme.MainColor)
            self.magnetic_dipole_moment_units_label.set("N/A", color=Theme.MainColor)
