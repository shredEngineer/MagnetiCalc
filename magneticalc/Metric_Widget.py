""" Metric_Widget module. """

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
from si_prefix import si_format
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from magneticalc.IconLabel import IconLabel
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.Metric import Metric
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Theme import Theme


class Metric_Widget(Groupbox):
    """ Metric_Widget class. """

    # Formatting settings
    ValuePrecision = 1

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Metric")

        self.gui = gui

        # Initially load metric from configuration
        self.set_metric(recalculate=False, update_labels=False, invalidate_self=False)

        # --------------------------------------------------------------------------------------------------------------

        self.addWidget(IconLabel("fa.tint", "Color"))
        color_metric_combobox = QComboBox()
        for i, preset in enumerate(Metric.Presets):
            color_metric_combobox.addItem(preset["id"])
            if preset["id"] == self.gui.model.metric.get_color_preset()["id"]:
                color_metric_combobox.setCurrentIndex(i)
        color_metric_combobox.currentIndexChanged.connect(
            lambda: self.set_metric(color_preset=Metric.get_by_id(color_metric_combobox.currentText()))
        )
        self.addWidget(color_metric_combobox)

        self.color_metric_limits_layout = QHBoxLayout()
        # noinspection PyArgumentList
        self.color_metric_limits_widget = QWidget()
        self.color_metric_limits_widget.setLayout(self.color_metric_limits_layout)
        self.color_metric_min_label = QLabel("N/A")
        self.color_metric_max_label = QLabel("N/A")
        color_metric_dots_icon = QLabel()
        color_metric_dots_icon.setPixmap(qta.icon("mdi.dots-horizontal").pixmap(QSize(16, 16)))
        self.color_metric_min_label.setStyleSheet("background: none;")
        self.color_metric_max_label.setStyleSheet("background: none;")
        color_metric_dots_icon.setStyleSheet("background: none;")
        self.color_metric_limits_layout.addWidget(self.color_metric_min_label, alignment=Qt.AlignVCenter)
        self.color_metric_limits_layout.addWidget(color_metric_dots_icon, alignment=Qt.AlignVCenter | Qt.AlignCenter)
        self.color_metric_limits_layout.addWidget(
            self.color_metric_max_label,
            alignment=Qt.AlignVCenter | Qt.AlignRight
        )
        self.addWidget(self.color_metric_limits_widget)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("mdi.blur", "Alpha"))
        alpha_metric_combobox = QComboBox()
        for i, preset in enumerate(Metric.Presets):
            alpha_metric_combobox.addItem(preset["id"])
            if preset["id"] == self.gui.model.metric.get_alpha_preset()["id"]:
                alpha_metric_combobox.setCurrentIndex(i)
        alpha_metric_combobox.currentIndexChanged.connect(
            lambda: self.set_metric(alpha_preset=Metric.get_by_id(alpha_metric_combobox.currentText()))
        )
        self.addWidget(alpha_metric_combobox)

        self.alpha_metric_limits_layout = QHBoxLayout()
        # noinspection PyArgumentList
        self.alpha_metric_limits_widget = QWidget()
        self.alpha_metric_limits_widget.setLayout(self.alpha_metric_limits_layout)
        self.alpha_metric_min_label = QLabel("N/A")
        self.alpha_metric_max_label = QLabel("N/A")
        alpha_metric_dots_icon = QLabel()
        alpha_metric_dots_icon.setPixmap(qta.icon("mdi.dots-horizontal").pixmap(QSize(16, 16)))
        self.alpha_metric_min_label.setStyleSheet("background: none;")
        self.alpha_metric_max_label.setStyleSheet("background: none;")
        alpha_metric_dots_icon.setStyleSheet("background: none;")
        self.alpha_metric_limits_layout.addWidget(self.alpha_metric_min_label, alignment=Qt.AlignVCenter)
        self.alpha_metric_limits_layout.addWidget(alpha_metric_dots_icon, alignment=Qt.AlignVCenter | Qt.AlignCenter)
        self.alpha_metric_limits_layout.addWidget(
            self.alpha_metric_max_label,
            alignment=Qt.AlignVCenter | Qt.AlignRight
        )
        self.addWidget(self.alpha_metric_limits_widget)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        parameters_label = IconLabel("fa.flask", "Parameters")
        self.addWidget(parameters_label)

        energy_layout = QHBoxLayout()
        energy_label_left = QLabel("Energy:")
        energy_label_left.setStyleSheet("font-style: italic;")
        self.energy_label = QLabel("N/A")
        self.energy_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.energy_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        energy_layout.addWidget(energy_label_left, alignment=Qt.AlignVCenter)
        energy_layout.addWidget(self.energy_label, alignment=Qt.AlignVCenter)
        self.addLayout(energy_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self_inductance_layout = QHBoxLayout()
        self_inductance_label_left = QLabel("Self-inductance:")
        self_inductance_label_left.setStyleSheet("font-style: italic;")
        self.self_inductance_label = QLabel("N/A")
        self.self_inductance_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.self_inductance_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self_inductance_layout.addWidget(self_inductance_label_left, alignment=Qt.AlignVCenter)
        self_inductance_layout.addWidget(self.self_inductance_label, alignment=Qt.AlignVCenter)
        self.addLayout(self_inductance_layout)

    # ------------------------------------------------------------------------------------------------------------------

    def set_metric(
            self,
            color_preset=None,
            alpha_preset=None,
            recalculate=True,
            update_labels=True,
            invalidate_self=True
    ):
        """
        Sets the metric. This will overwrite the currently set metric in the model.
        Any parameter may be left set to None in order to load its default value.

        @param color_preset: Color metric preset (parameters, see Metric module)
        @param alpha_preset: Alpha metric preset (parameters, see Metric module)
        @param recalculate: Enable to trigger final re-calculation (boolean)
        @param update_labels: Enable to update metric labels
        @param invalidate_self: Enable to invalidate the old metric before setting a new one
        """
        with ModelAccess(self.gui, recalculate):

            # Note: Not using self.gui.config.write_read_str here because we're translating between strings and presets

            if color_preset is None:
                color_preset = Metric.get_by_id(self.gui.config.get_str("color_metric"))
            else:
                self.gui.config.set_str("color_metric", color_preset["id"])

            if alpha_preset is None:
                alpha_preset = Metric.get_by_id(self.gui.config.get_str("alpha_metric"))
            else:
                self.gui.config.set_str("alpha_metric", alpha_preset["id"])

            self.gui.model.set_metric(
                Metric(color_preset, alpha_preset),
                invalidate_self=invalidate_self
            )

            if update_labels:
                self.update_labels()

    # ------------------------------------------------------------------------------------------------------------------

    Cool_Gradient_CSS = """
        background: qlineargradient(
            x1:0 y1:0, x2:1 y2:0,
            stop:0 #00fffe,
            stop:1 #ff22f9
        );
    """

    HSV_Gradient_CSS = """
        background: qlineargradient(
            x1:0 y1:0, x2:1 y2:0,
            stop:0.00 #ff0000,
            stop:0.08 #ff8000,
            stop:0.17 #ffff00,
            stop:0.25 #80ff00,
            stop:0.33 #00ff00,
            stop:0.42 #00ff80,
            stop:0.50 #00ffff,
            stop:0.58 #0080ff,
            stop:0.67 #0000ff,
            stop:0.75 #8000ff,
            stop:0.83 #ff00ff,
            stop:0.92 #ff0080,
            stop:1.00 #ff0000
        );
    """

    def update_labels(self):
        """
        Updates the metric limit labels.
        """
        if self.gui.model.metric.is_valid():

            limits = self.gui.model.metric.get_limits()

            field_units = self.gui.model.field.get_units()

            if self.gui.model.metric.get_color_preset()["is_angle"]:
                color_label_min = "N/A"
                color_label_max = "N/A"
                self.color_metric_limits_widget.setStyleSheet(self.HSV_Gradient_CSS)
                self.color_metric_min_label.setStyleSheet("background: none; color: #ffffff;")
                self.color_metric_max_label.setStyleSheet("background: none; color: #ffffff;")
            else:
                color_label_min = si_format(limits["color_min"], precision=self.ValuePrecision) + field_units
                color_label_max = si_format(limits["color_max"], precision=self.ValuePrecision) + field_units
                self.color_metric_limits_widget.setStyleSheet(self.Cool_Gradient_CSS)
                self.color_metric_min_label.setStyleSheet("background: none; color: #000000; font-weight: bold;")
                self.color_metric_max_label.setStyleSheet("background: none; color: #ffffff; font-weight: bold;")

            if self.gui.model.metric.get_alpha_preset()["is_angle"]:
                alpha_label_min = "N/A"
                alpha_label_max = "N/A"
                self.alpha_metric_limits_widget.setStyleSheet(self.HSV_Gradient_CSS)
                self.alpha_metric_min_label.setStyleSheet("background: none; color: #ffffff;")
                self.alpha_metric_max_label.setStyleSheet("background: none; color: #ffffff;")
            else:
                alpha_label_min = si_format(limits["alpha_min"], precision=self.ValuePrecision) + field_units
                alpha_label_max = si_format(limits["alpha_max"], precision=self.ValuePrecision) + field_units
                self.alpha_metric_limits_widget.setStyleSheet(self.Cool_Gradient_CSS)
                self.alpha_metric_min_label.setStyleSheet("background: none; color: #000000; font-weight: bold;")
                self.alpha_metric_max_label.setStyleSheet("background: none; color: #ffffff; font-weight: bold;")

            self.color_metric_min_label.setText(color_label_min)
            self.color_metric_max_label.setText(color_label_max)
            self.alpha_metric_min_label.setText(alpha_label_min)
            self.alpha_metric_max_label.setText(alpha_label_max)

            if self.gui.model.field.get_type() == 1:

                # Field is B-Field (flux density)
                self.energy_label.setText(
                    si_format(self.gui.model.metric.get_energy(), precision=self.ValuePrecision) + "J"
                )
                self.self_inductance_label.setText(
                    si_format(self.gui.model.metric.get_self_inductance(), precision=self.ValuePrecision) + "H"
                )
                self.energy_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")
                self.self_inductance_label.setStyleSheet(f"color: {Theme.PrimaryColor}; font-weight: bold;")
            else:

                # Field is A-Field (vector potential)
                self.energy_label.setText("N/A")
                self.self_inductance_label.setText("N/A")
                self.energy_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
                self.self_inductance_label.setStyleSheet(f"color: {Theme.PrimaryColor};")

        else:

            self.color_metric_min_label.setText("N/A")
            self.color_metric_max_label.setText("N/A")
            self.color_metric_limits_widget.setStyleSheet("")
            self.color_metric_min_label.setStyleSheet("background: none; color: #000000;")
            self.color_metric_max_label.setStyleSheet("background: none; color: #000000;")

            self.alpha_metric_min_label.setText("N/A")
            self.alpha_metric_max_label.setText("N/A")
            self.alpha_metric_limits_widget.setStyleSheet("")
            self.alpha_metric_min_label.setStyleSheet("background: none; color: #000000;")
            self.alpha_metric_max_label.setStyleSheet("background: none; color: #000000;")

            self.energy_label.setText("N/A")
            self.self_inductance_label.setText("N/A")
            self.energy_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
            self.self_inductance_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
