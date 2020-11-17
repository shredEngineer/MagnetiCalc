""" Field_Widget module. """

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

from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QButtonGroup, QRadioButton, QDoubleSpinBox, QLabel, QSizePolicy
from magneticalc.Debug import Debug
from magneticalc.Field import Field
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.IconLabel import IconLabel
from magneticalc.Metric import Metric
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Theme import Theme


class Field_Widget(Groupbox):
    """ Field_Widget class. """

    # Spinbox limits
    DistanceLimitMinimum = 0.0001
    DistanceLimitMaximum = 1
    DistanceLimitStep = 0.0001
    DistanceLimitPrecision = 4

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Field")

        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(IconLabel("mdi.tune-variant", "Type"))
        self.field_type_group = QButtonGroup()
        field_type_a_radiobutton = QRadioButton(" A-Field (Vector Potential)")
        field_type_b_radiobutton = QRadioButton(" B-Field (Flux Density)")
        self.field_type_group.addButton(field_type_a_radiobutton)
        self.field_type_group.addButton(field_type_b_radiobutton)
        self.addWidget(field_type_a_radiobutton)
        self.addWidget(field_type_b_radiobutton)
        for i, button in enumerate(self.field_type_group.buttons()):
            button.toggled.connect(partial(self.on_field_type_changed, i))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("mdi.ruler", "Distance Limit"))
        self.distance_limit_spinbox = QDoubleSpinBox(self.gui)
        self.distance_limit_spinbox.setLocale(self.gui.locale)
        self.distance_limit_spinbox.setDecimals(self.DistanceLimitPrecision)
        self.distance_limit_spinbox.setMinimum(self.DistanceLimitMinimum)
        self.distance_limit_spinbox.setMaximum(self.DistanceLimitMaximum)
        self.distance_limit_spinbox.setSingleStep(self.DistanceLimitStep)
        self.distance_limit_spinbox.valueChanged.connect(
            lambda: self.set_field(distance_limit=self.distance_limit_spinbox.value())
        )
        distance_limit_layout = QHBoxLayout()
        distance_limit_layout.addWidget(self.distance_limit_spinbox, alignment=Qt.AlignVCenter)
        distance_limit_units_label = QLabel("cm")
        distance_limit_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        distance_limit_layout.addWidget(distance_limit_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(distance_limit_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        total_limited_points_layout = QHBoxLayout()
        total_limited_points_left = QLabel("Total limited points:")
        total_limited_points_left.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")
        self.total_limited_points_label = QLabel("N/A")
        self.total_limited_points_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.total_limited_points_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_limited_points_layout.addWidget(total_limited_points_left, alignment=Qt.AlignVCenter)
        total_limited_points_layout.addWidget(self.total_limited_points_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_limited_points_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the widget.
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        for i, button in enumerate(self.field_type_group.buttons()):
            button.setChecked(i == self.gui.config.get_int("field_type"))

        self.distance_limit_spinbox.setValue(self.gui.config.get_float("field_distance_limit"))

        self.blockSignals(False)

        # Initially load field from configuration
        self.set_field(recalculate=False, invalidate_self=False)

    # ------------------------------------------------------------------------------------------------------------------

    def on_field_type_changed(self, _type: bool, checked: bool):
        """
        Gets called when the field type changed.

        @param _type: Field type (0: A-field; 1: B-field)
        @param checked: Boolean
        """
        if self.signalsBlocked():
            return

        if checked:
            self.set_field(_type=_type)

    # ------------------------------------------------------------------------------------------------------------------

    def set_field(
            self,
            _type: int = None,
            distance_limit: float = None,
            recalculate: bool = True,
            invalidate_self: bool = True
    ):
        """
        Sets the field. This will overwrite the currently set field in the model.
        Parameters may be left set to None in order to load their default value.

        @param _type: Field type (0: A-field; 1: B-field)
        @param distance_limit: Distance limit
        @param recalculate: Enable to trigger final re-calculation
        @param invalidate_self: Enable to invalidate the old field before setting a new one
        """
        if self.signalsBlocked():
            return

        with ModelAccess(self.gui, recalculate):

            backend = self.gui.config.get_int("backend")
            _type = self.gui.config.set_get_int("field_type", _type)
            distance_limit = self.gui.config.set_get_float("field_distance_limit", distance_limit)

            self.gui.model.set_field(
                Field(backend, _type, distance_limit, Metric.LengthScale),
                invalidate_self=invalidate_self
            )

    # ------------------------------------------------------------------------------------------------------------------

    def update_labels(self):
        """
        Updates the labels.
        """
        if self.gui.model.field.is_valid():
            self.total_limited_points_label.setText(str(self.gui.model.field.get_total_limited()))
        else:
            self.total_limited_points_label.setText("N/A")
