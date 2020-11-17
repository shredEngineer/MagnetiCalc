""" Display_Widget module. """

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel, QSizePolicy, QHBoxLayout
from magneticalc.Debug import Debug
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.IconLabel import IconLabel
from magneticalc.SliderFloat import SliderFloat


class Display_Widget(Groupbox):
    """ Display_Widget class. """

    # Slider limits
    FieldArrowScaleMinimum = 0
    FieldArrowScaleMaximum = 1
    FieldArrowScaleStep = 0.025
    FieldPointScaleMinimum = 0
    FieldPointScaleMaximum = 20
    FieldPointScaleStep = 0.5
    FieldBoostMinimum = 0
    FieldBoostMaximum = 1
    FieldBoostStep = 0.025

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Display")

        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(IconLabel("fa.circle", "Point Scale"))
        self.field_point_scale_slider = SliderFloat(Qt.Horizontal)
        self.field_point_scale_slider.set_range_step(
            self.FieldPointScaleMinimum,
            self.FieldPointScaleMaximum,
            self.FieldPointScaleStep
        )
        self.field_point_scale_slider.valueChanged.connect(
            lambda: self.set_field_point_scale(self.field_point_scale_slider.get_value())
        )
        self.addWidget(self.field_point_scale_slider)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("fa.arrow-right", "Arrow Scale"))
        self.field_arrow_scale_slider = SliderFloat(Qt.Horizontal)
        self.field_arrow_scale_slider.set_range_step(
            self.FieldArrowScaleMinimum,
            self.FieldArrowScaleMaximum,
            self.FieldArrowScaleStep
        )
        self.field_arrow_scale_slider.valueChanged.connect(
            lambda: self.set_field_arrow_scale(self.field_arrow_scale_slider.get_value())
        )
        self.addWidget(self.field_arrow_scale_slider)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("fa.adjust", "Field Boost"))
        self.field_boost_slider = SliderFloat(Qt.Horizontal)
        self.field_boost_slider.set_range_step(
            self.FieldBoostMinimum,
            self.FieldBoostMaximum,
            self.FieldBoostStep
        )
        self.field_boost_slider.valueChanged.connect(
            lambda: self.set_field_boost(self.field_boost_slider.get_value())
        )
        self.addWidget(self.field_boost_slider)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        self.addWidget(IconLabel("fa.tags", "Field Labels"))
        self.display_magnitude_labels_checkbox = QCheckBox(" Display Magnitude (slow)")  # Leading space for alignment
        self.display_magnitude_labels_checkbox.stateChanged.connect(
            lambda: self.set_display_magnitude_labels(self.display_magnitude_labels_checkbox.isChecked())
        )
        self.addWidget(self.display_magnitude_labels_checkbox)

        self.label_resolution_options = None
        self.label_resolution_combobox = QComboBox()
        label_resolution_layout = QHBoxLayout()
        label_resolution_layout.addWidget(self.label_resolution_combobox, alignment=Qt.AlignVCenter)
        self.label_resolution_units_label = QLabel(" Labels / cm")
        self.label_resolution_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        label_resolution_layout.addWidget(self.label_resolution_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(label_resolution_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the widget.
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        self.field_point_scale_slider.setValue(self.gui.config.get_float("field_point_scale"))
        self.field_arrow_scale_slider.setValue(self.gui.config.get_float("field_arrow_scale"))
        self.field_boost_slider.setValue(self.gui.config.get_float("field_boost"))
        self.display_magnitude_labels_checkbox.setChecked(self.gui.config.get_bool("display_magnitude_labels"))

        self.blockSignals(False)

        self.update_label_resolution_combobox()

    # ------------------------------------------------------------------------------------------------------------------

    def set_enabled(self, enabled: bool):
        """
        Enables / disables this widget.

        @param enabled: Enabled state
        """
        self.setEnabled(enabled)

    # ------------------------------------------------------------------------------------------------------------------

    def set_field_arrow_scale(self, value: float):
        """
        Sets field arrow scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_arrow_scale", value)
        self.gui.redraw()

    def set_field_point_scale(self, value: float):
        """
        Sets field point scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_point_scale", value)
        self.gui.redraw()

    def set_field_boost(self, value: float):
        """
        Sets field boost value.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_boost", value)
        self.gui.redraw()

    def set_display_magnitude_labels(self, value: bool):
        """
        Sets "Display Magnitude" value.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_bool("display_magnitude_labels", value)

        self.update_label_resolution_combobox()

        self.gui.redraw()

    def set_label_resolution(self, value: int):
        """
        Sets label density value.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_int("label_resolution", value)

        # The labels generated by the SamplingVolume depend on the label resolution
        self.gui.sidebar_left.sampling_volume_widget.set_sampling_volume()

        self.gui.redraw()

    def update_label_resolution_combobox(self):
        """
        Updates the enabled state and possible values of the label resolution combobox.
        """
        Debug(self, ".update_label_resolution_combobox()")

        any_labels = \
            self.gui.config.get_bool("display_magnitude_labels")

        self.label_resolution_combobox.setEnabled(any_labels)
        self.label_resolution_units_label.setEnabled(any_labels)

        # Possible label resolution values: Integer divisors of sampling volume resolution
        sampling_volume_resolution = self.gui.config.get_int("sampling_volume_resolution")
        self.label_resolution_options = [
            n for n in range(1, sampling_volume_resolution + 1) if sampling_volume_resolution % n == 0
        ]

        self.blockSignals(True)

        # Re-populate label resolution combobox
        self.label_resolution_combobox.clear()
        for i, value in enumerate(self.label_resolution_options):
            self.label_resolution_combobox.addItem(str(value))
        self.label_resolution_combobox.currentIndexChanged.connect(
            lambda: self.set_label_resolution(self.label_resolution_combobox.currentText())
        )

        # Set default label resolution if it is not available anymore
        if self.gui.config.get_int("label_resolution") not in self.label_resolution_options:
            self.gui.config.set_int("label_resolution", 1)

        # Select the label resolution
        for i, value in enumerate(self.label_resolution_options):
            if value == self.gui.config.get_int("label_resolution"):
                self.label_resolution_combobox.setCurrentIndex(i)

        self.blockSignals(False)
