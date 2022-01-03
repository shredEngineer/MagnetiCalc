""" Metric_Widget module. """

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
import qtawesome as qta
from si_prefix import si_format
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.Debug import Debug
from magneticalc.Metric import Metric
from magneticalc.Metric_Presets import Metric_Presets
from magneticalc.ModelAccess import ModelAccess

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Metric_Widget(QGroupBox2):
    """ Metric_Widget class. """

    # Formatting settings
    ValuePrecision = 1

    def __init__(self, gui: GUI) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Metric")
        Debug(self, ": Init")
        self.gui = gui

        # --------------------------------------------------------------------------------------------------------------

        self.addLayout(QIconLabel("Color", "fa.tint"))
        self.color_metric_combobox = QComboBox()
        for i, preset in enumerate(Metric_Presets.List):
            self.color_metric_combobox.addItem(preset["id"])
        # noinspection PyUnresolvedReferences
        self.color_metric_combobox.currentIndexChanged.connect(
            lambda: self.set_metric(color_preset=Metric_Presets.get_by_id(self.color_metric_combobox.currentText()))
        )
        self.addWidget(self.color_metric_combobox)

        self.color_metric_limits_layout = QHBoxLayout()
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

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Alpha", "mdi.blur"))
        self.alpha_metric_combobox = QComboBox()
        for i, preset in enumerate(Metric_Presets.List):
            # Note: (v1.9)
            # Using angle metric for alpha transparency is discouraged and is not available in the combobox anymore.
            if not preset["is_angle"]:
                self.alpha_metric_combobox.addItem(preset["id"])
        # noinspection PyUnresolvedReferences
        self.alpha_metric_combobox.currentIndexChanged.connect(
            lambda: self.set_metric(alpha_preset=Metric_Presets.get_by_id(self.alpha_metric_combobox.currentText()))
        )
        self.addWidget(self.alpha_metric_combobox)

        self.alpha_metric_limits_layout = QHBoxLayout()
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

        self.reinitialize()

    def reinitialize(self) -> None:
        """
        Re-initializes the widget.
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        for i, preset in enumerate(Metric_Presets.List):
            if preset["id"] == self.gui.config.get_str("color_metric"):
                self.color_metric_combobox.setCurrentIndex(i)

        for i, preset in enumerate(Metric_Presets.List):
            if preset["id"] == self.gui.config.get_str("alpha_metric"):
                self.alpha_metric_combobox.setCurrentIndex(i)

        self.blockSignals(False)

        # Initially load metric from configuration
        self.set_metric(recalculate=False, update_labels=False, invalidate_self=False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_metric(
            self,
            color_preset=None,
            alpha_preset=None,
            recalculate: bool = True,
            update_labels: bool = True,
            invalidate_self: bool = True
    ) -> None:
        """
        Sets the metric. This will overwrite the currently set metric in the model.
        Any parameter may be left set to None in order to load its default value.

        @param color_preset: Color metric preset (parameters, see Metric module)
        @param alpha_preset: Alpha metric preset (parameters, see Metric module)
        @param recalculate: Enable to trigger final re-calculation
        @param update_labels: Enable to update metric labels
        @param invalidate_self: Enable to invalidate the old metric before setting a new one
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_metric()")

        with ModelAccess(self.gui, recalculate):

            # Note: Not using self.gui.config.write_read_str here because we're translating between strings and presets

            if color_preset is None:
                color_preset = Metric_Presets.get_by_id(self.gui.config.get_str("color_metric"))
            else:
                self.gui.config.set_str("color_metric", color_preset["id"])

            if alpha_preset is None:
                alpha_preset = Metric_Presets.get_by_id(self.gui.config.get_str("alpha_metric"))
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

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()")

        if self.gui.model.metric.is_valid():

            limits = self.gui.model.metric.get_limits()

            show_gauss = self.gui.config.get_bool("show_gauss")
            field_units, field_factor = self.gui.model.field.get_units(show_gauss=show_gauss)

            if self.gui.model.metric.get_color_preset()["is_angle"]:
                color_label_min = "0°"
                color_label_max = "360°"
                self.color_metric_limits_widget.setStyleSheet(self.HSV_Gradient_CSS)
                self.color_metric_min_label.setStyleSheet("background: none; color: #ffffff;")
                self.color_metric_max_label.setStyleSheet("background: none; color: #ffffff;")
            else:
                color_log_prefix, color_log_suffix = ("log(", ")") \
                    if self.gui.model.metric.get_color_preset()["is_log"] else ("", "")

                if np.isnan(limits["color_min"]):
                    color_label_min = "NaN"
                else:
                    color_label_min = color_log_prefix +\
                        si_format(
                            limits["color_min"] * field_factor,
                            precision=self.ValuePrecision,
                            exp_format_str="{value}e{expof10} "
                        ) +\
                        field_units +\
                        color_log_suffix
                if np.isnan(limits["color_max"]):
                    color_label_max = "NaN"
                else:
                    color_label_max = color_log_prefix +\
                        si_format(
                            limits["color_max"] * field_factor,
                            precision=self.ValuePrecision,
                            exp_format_str="{value}e{expof10} "
                        ) +\
                        field_units + \
                        color_log_suffix
                self.color_metric_limits_widget.setStyleSheet(self.Cool_Gradient_CSS)
                self.color_metric_min_label.setStyleSheet("background: none; color: #000000; font-weight: bold;")
                self.color_metric_max_label.setStyleSheet("background: none; color: #ffffff; font-weight: bold;")

            if self.gui.model.metric.get_alpha_preset()["is_angle"]:
                # Note: (v1.9)
                # Using angle metric for alpha transparency is discouraged and is not available in the combobox anymore.
                alpha_label_min = "0°"
                alpha_label_max = "360°"
                self.alpha_metric_limits_widget.setStyleSheet(self.HSV_Gradient_CSS)
                self.alpha_metric_min_label.setStyleSheet("background: none; color: #ffffff;")
                self.alpha_metric_max_label.setStyleSheet("background: none; color: #ffffff;")
            else:
                alpha_log_prefix, alpha_log_suffix = ("log(", ")") \
                    if self.gui.model.metric.get_alpha_preset()["is_log"] else ("", "")

                if np.isnan(limits["alpha_min"]):
                    alpha_label_min = "NaN"
                else:
                    alpha_label_min = alpha_log_prefix +\
                        si_format(
                            limits["alpha_min"] * field_factor,
                            precision=self.ValuePrecision,
                            exp_format_str="{value}e{expof10} "
                        ) +\
                        field_units +\
                        alpha_log_suffix
                if np.isnan(limits["alpha_max"]):
                    alpha_label_max = "NaN"
                else:
                    alpha_label_max = alpha_log_prefix +\
                        si_format(
                            limits["alpha_max"] * field_factor,
                            precision=self.ValuePrecision,
                            exp_format_str="{value}e{expof10} "
                        ) +\
                        field_units + \
                        alpha_log_suffix
                self.alpha_metric_limits_widget.setStyleSheet(self.Cool_Gradient_CSS)
                self.alpha_metric_min_label.setStyleSheet("background: none; color: #000000; font-weight: bold;")
                self.alpha_metric_max_label.setStyleSheet("background: none; color: #ffffff; font-weight: bold;")

            self.color_metric_min_label.setText(color_label_min)
            self.color_metric_max_label.setText(color_label_max)
            self.alpha_metric_min_label.setText(alpha_label_min)
            self.alpha_metric_max_label.setText(alpha_label_max)

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
