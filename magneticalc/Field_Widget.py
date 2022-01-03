""" Field_Widget module. """

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
from typing import Optional
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QButtonGroup, QRadioButton, QDoubleSpinBox, QLabel, QCheckBox
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.Debug import Debug
from magneticalc.Field import Field
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.Metric import Metric
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Field_Widget(QGroupBox2):
    """ Field_Widget class. """

    # Spinbox limits
    DistanceLimitMinimum = 0.0001
    DistanceLimitMaximum = 1
    DistanceLimitStep = 0.0001
    DistanceLimitPrecision = 4

    def __init__(self, gui: GUI) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Field")
        Debug(self, ": Init")
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addLayout(QIconLabel("Type", "mdi.tune-variant"))

        field_type_layout_left = QVBoxLayout()
        field_type_layout_right = QVBoxLayout()

        field_type_a_radiobutton = QRadioButton(" A-Field (Vector Potential)")
        field_type_a_radiobutton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        field_type_layout_left.addWidget(field_type_a_radiobutton, alignment=Qt.AlignVCenter)
        self.field_type_a_checkbox = QCheckBox(" Cached")
        self.field_type_a_checkbox.setEnabled(False)
        field_type_layout_right.addWidget(self.field_type_a_checkbox, alignment=Qt.AlignVCenter | Qt.AlignRight)

        field_type_b_radiobutton = QRadioButton(" B-Field (Flux Density)")
        field_type_b_radiobutton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        field_type_layout_left.addWidget(field_type_b_radiobutton, alignment=Qt.AlignVCenter)
        self.field_type_b_checkbox = QCheckBox(" Cached")
        self.field_type_b_checkbox.setEnabled(False)
        field_type_layout_right.addWidget(self.field_type_b_checkbox, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.field_type_group = QButtonGroup()
        self.field_type_group.addButton(field_type_a_radiobutton)
        self.field_type_group.addButton(field_type_b_radiobutton)

        field_type_layout = QHBoxLayout()
        field_type_layout.addLayout(field_type_layout_left)
        field_type_layout.addLayout(field_type_layout_right)
        self.addLayout(field_type_layout)

        for i, button in enumerate(self.field_type_group.buttons()):
            button.toggled.connect(partial(self.on_field_type_changed, i))

        total_calculations_layout = QHBoxLayout()
        total_calculations_left = QLabel("Total calculations:")
        total_calculations_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.total_calculations_label = QLabel("N/A")
        self.total_calculations_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.total_calculations_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_calculations_layout.addWidget(total_calculations_left, alignment=Qt.AlignVCenter)
        total_calculations_layout.addWidget(self.total_calculations_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_calculations_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Distance Limit", "mdi.ruler"))
        self.distance_limit_spinbox = QDoubleSpinBox(self.gui)
        self.distance_limit_spinbox.setLocale(self.gui.locale)
        self.distance_limit_spinbox.setDecimals(self.DistanceLimitPrecision)
        self.distance_limit_spinbox.setMinimum(self.DistanceLimitMinimum)
        self.distance_limit_spinbox.setMaximum(self.DistanceLimitMaximum)
        self.distance_limit_spinbox.setSingleStep(self.DistanceLimitStep)
        # noinspection PyUnresolvedReferences
        self.distance_limit_spinbox.valueChanged.connect(
            lambda: self.set_field(distance_limit=self.distance_limit_spinbox.value())
        )
        distance_limit_layout = QHBoxLayout()
        distance_limit_layout.addWidget(self.distance_limit_spinbox, alignment=Qt.AlignVCenter)
        distance_limit_units_label = QLabel("cm")
        distance_limit_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        distance_limit_layout.addWidget(distance_limit_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(distance_limit_layout)

        total_skipped_calculations_layout = QHBoxLayout()
        total_skipped_calculations_left = QLabel("Total skipped calculations:")
        total_skipped_calculations_left.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")
        self.total_skipped_calculations_label = QLabel("N/A")
        self.total_skipped_calculations_label.setStyleSheet(f"color: {Theme.MainColor};")
        self.total_skipped_calculations_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_skipped_calculations_layout.addWidget(total_skipped_calculations_left, alignment=Qt.AlignVCenter)
        total_skipped_calculations_layout.addWidget(self.total_skipped_calculations_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_skipped_calculations_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self) -> None:
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

    def on_field_type_changed(self, field_type: bool, checked: bool) -> None:
        """
        Gets called when the field type changed.

        @param field_type: Field type
        @param checked: Boolean
        """
        if self.signalsBlocked():
            return

        if not checked:
            return

        self.set_field(field_type=field_type, allow_cache=True)

    # ------------------------------------------------------------------------------------------------------------------

    def set_field(
            self,
            field_type: Optional[int] = None,
            distance_limit: Optional[float] = None,
            recalculate: bool = True,
            invalidate_self: bool = True,
            allow_cache: bool = False
    ) -> None:
        """
        Sets the field. This will replace the currently set field in the model.

        Parameters may be left set to None in order to load their default value.

        @param field_type: Field type
        @param distance_limit: Distance limit
        @param recalculate: Enable to trigger final re-calculation
        @param invalidate_self: Enable to invalidate the old field before setting a new one
        @param allow_cache: Enable to select a field from the cache if it is available (based on the field type)
        """
        if self.signalsBlocked():
            return

        Debug(self, ".set_field()")

        with ModelAccess(self.gui, recalculate):

            if allow_cache:
                field = self.gui.model.get_valid_field(field_type)
            else:
                field = None

            if field is not None:
                Debug(self, ".set_field(): Using cached field")
            else:
                backend_type = self.gui.config.get_int("backend_type")
                field_type = self.gui.config.set_get_int("field_type", field_type)
                distance_limit = self.gui.config.set_get_float("field_distance_limit", distance_limit)
                field = Field(backend_type, field_type, distance_limit, Metric.LengthScale)

            self.gui.model.set_field(
                field=field,
                invalidate_self=invalidate_self and not allow_cache,
            )

    # ------------------------------------------------------------------------------------------------------------------

    def update(self) -> None:
        """
        Updates this widget.
        """
        Debug(self, ".update()")

        self.update_labels()
        self.update_controls()

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        if self.gui.model.field.is_valid():
            self.total_calculations_label.setText(str(self.gui.model.field.get_total_calculations()))
            self.total_skipped_calculations_label.setText(str(self.gui.model.field.get_total_skipped_calculations()))
        else:
            self.total_calculations_label.setText("N/A")
            self.total_skipped_calculations_label.setText("N/A")

    def update_controls(self) -> None:
        """
        Updates the controls.
        """
        a_field_available = self.gui.model.get_valid_field(A_FIELD) is not None
        b_field_available = self.gui.model.get_valid_field(B_FIELD) is not None

        self.field_type_a_checkbox.setChecked(a_field_available)
        self.field_type_b_checkbox.setChecked(b_field_available)
