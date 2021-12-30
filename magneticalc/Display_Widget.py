""" Display_Widget module. """

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

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout, QMessageBox
from magneticalc.Debug import Debug
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.IconLabel import IconLabel
from magneticalc.SamplingVolume_Widget import SamplingVolume_Widget
from magneticalc.SliderFloat import SliderFloat
from magneticalc.Theme import Theme
from magneticalc.VispyCanvas import VispyCanvas


class Display_Widget(Groupbox):
    """ Display_Widget class. """

    # Slider limits
    FieldArrowHeadScaleMinimum = 0
    FieldArrowHeadScaleMaximum = 1
    FieldArrowHeadScaleStep = 1 / VispyCanvas.FieldArrowHeadSize
    FieldArrowLineScaleMinimum = 0
    FieldArrowLineScaleMaximum = 1
    FieldArrowLineScaleStep = 1 / 10
    FieldPointScaleMinimum = 0
    FieldPointScaleMaximum = 1
    FieldPointScaleStep = 1 / VispyCanvas.FieldPointSize
    FieldBoostMinimum = 0
    FieldBoostMaximum = 1
    FieldBoostStep = 1 / 20

    # Warn about displaying an excessive number of field labels
    ExcessiveFieldLabelThreshold = 250

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

        field_arrow_scale_layout_left = QVBoxLayout()
        field_arrow_scale_layout_right = QVBoxLayout()

        field_arrow_head_scale_label = QLabel("Head:")
        field_arrow_head_scale_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        field_arrow_scale_layout_left.addWidget(field_arrow_head_scale_label, alignment=Qt.AlignVCenter)
        self.field_arrow_head_scale_slider = SliderFloat(Qt.Horizontal)
        self.field_arrow_head_scale_slider.set_range_step(
            self.FieldArrowHeadScaleMinimum,
            self.FieldArrowHeadScaleMaximum,
            self.FieldArrowHeadScaleStep
        )
        self.field_arrow_head_scale_slider.valueChanged.connect(
            lambda: self.set_field_arrow_head_scale(self.field_arrow_head_scale_slider.get_value())
        )
        field_arrow_scale_layout_right.addWidget(self.field_arrow_head_scale_slider, alignment=Qt.AlignVCenter)

        field_arrow_line_scale_label = QLabel("Line:")
        field_arrow_line_scale_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        field_arrow_scale_layout_left.addWidget(field_arrow_line_scale_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        self.field_arrow_line_scale_slider = SliderFloat(Qt.Horizontal)
        self.field_arrow_line_scale_slider.set_range_step(
            self.FieldArrowLineScaleMinimum,
            self.FieldArrowLineScaleMaximum,
            self.FieldArrowLineScaleStep
        )
        self.field_arrow_line_scale_slider.valueChanged.connect(
            lambda: self.set_field_arrow_line_scale(self.field_arrow_line_scale_slider.get_value())
        )
        field_arrow_scale_layout_right.addWidget(self.field_arrow_line_scale_slider, alignment=Qt.AlignVCenter)

        field_arrow_scale_layout = QHBoxLayout()
        field_arrow_scale_layout.addLayout(field_arrow_scale_layout_left)
        field_arrow_scale_layout.addLayout(field_arrow_scale_layout_right)
        self.addLayout(field_arrow_scale_layout)

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
        self.display_field_magnitude_labels_checkbox = QCheckBox(" Display Magnitude")  # Leading space for alignment
        self.display_field_magnitude_labels_checkbox.toggled.connect(
            lambda: self.set_display_field_magnitude_labels(self.display_field_magnitude_labels_checkbox.isChecked())
        )
        self.addWidget(self.display_field_magnitude_labels_checkbox)

        self.field_label_resolution_combobox = QComboBox()
        self.field_label_resolution_combobox_connection = None
        field_label_resolution_layout = QHBoxLayout()
        field_label_resolution_layout.addWidget(self.field_label_resolution_combobox, alignment=Qt.AlignVCenter)
        field_label_resolution_units_label = QLabel(" Labels / cm")
        field_label_resolution_units_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        field_label_resolution_layout.addWidget(field_label_resolution_units_label, alignment=Qt.AlignVCenter)
        self.addLayout(field_label_resolution_layout)

        total_labels_layout = QHBoxLayout()
        total_labels_left = QLabel("Total labels:")
        total_labels_left.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")
        self.total_labels_label = QLabel("N/A")
        self.total_labels_label.setStyleSheet(f"color: {Theme.PrimaryColor};")
        self.total_labels_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_labels_layout.addWidget(total_labels_left, alignment=Qt.AlignVCenter)
        total_labels_layout.addWidget(self.total_labels_label, alignment=Qt.AlignVCenter)
        self.addLayout(total_labels_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the widget.
        """
        Debug(self, ".reinitialize()")

        self.blockSignals(True)

        self.field_point_scale_slider.setValue(self.gui.config.get_float("field_point_scale"))
        self.field_arrow_head_scale_slider.setValue(self.gui.config.get_float("field_arrow_head_scale"))
        self.field_arrow_line_scale_slider.setValue(self.gui.config.get_float("field_arrow_line_scale"))
        self.field_boost_slider.setValue(self.gui.config.get_float("field_boost"))
        self.display_field_magnitude_labels_checkbox.setChecked(
            self.gui.config.get_bool("display_field_magnitude_labels")
        )

        self.blockSignals(False)

        self.update()

    # ------------------------------------------------------------------------------------------------------------------

    def set_enabled(self, enabled: bool):
        """
        Enables / disables this widget.

        @param enabled: Enabled state
        """
        self.setEnabled(enabled)

    # ------------------------------------------------------------------------------------------------------------------

    def set_field_point_scale(self, value: float):
        """
        Sets field point scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_point_scale", value)
        self.gui.redraw()

    def set_field_arrow_head_scale(self, value: float):
        """
        Sets field arrow head scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_arrow_head_scale", value)
        self.gui.redraw()

    def set_field_arrow_line_scale(self, value: float):
        """
        Sets field arrow line scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_arrow_line_scale", value)
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

    def set_display_field_magnitude_labels(self, value: bool):
        """
        Sets field label "Display Magnitude" value.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_bool("display_field_magnitude_labels", value)

        self.prevent_excessive_field_labels(choice=True)

        self.update()

        self.gui.redraw()

    def set_field_label_resolution(self, value: int):
        """
        Sets field label resolution exponent.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.sidebar_left.sampling_volume_widget.set_sampling_volume(label_resolution_exponent=value)

        # Note: L{prevent_excessive_field_labels(choice=False)} will be called by L{Model.on_sampling_volume_valid()}.

        self.gui.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def update(self):
        """
        Updates this widget.
        """
        Debug(self, ".update()")

        self.update_labels()
        self.update_controls()

    def update_labels(self):
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()")

        if self.gui.model.sampling_volume.is_valid():
            n = self.gui.model.sampling_volume.get_labels_count()
            color = Theme.WarningColor if n > self.ExcessiveFieldLabelThreshold else Theme.LightColor
            self.total_labels_label.setText(str(n))
            self.total_labels_label.setStyleSheet(f"color: {color}; font-style: italic;")
        else:
            self.total_labels_label.setText("N/A")
            self.total_labels_label.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")

    def update_controls(self):
        """
        Updates the field label resolution combobox.
        """
        Debug(self, ".update_controls()")

        # Possible field label resolution values: Less than or equal to sampling volume resolution
        sampling_volume_resolution = self.gui.model.sampling_volume.get_resolution()
        label_resolution_options_dict = {
            key: value for key, value in SamplingVolume_Widget.ResolutionOptionsDict.items()
            if np.power(2.0, value) <= sampling_volume_resolution
        }

        self.blockSignals(True)

        # Re-populate field label resolution combobox
        if self.field_label_resolution_combobox_connection is not None:
            self.field_label_resolution_combobox.currentIndexChanged.disconnect(
                self.field_label_resolution_combobox_connection
            )
        self.field_label_resolution_combobox.clear()
        for i, value in enumerate(label_resolution_options_dict.keys()):
            self.field_label_resolution_combobox.addItem(str(value))

        def connection():
            """ Sets field label resolution. """
            self.set_field_label_resolution(
                label_resolution_options_dict.get(
                    self.field_label_resolution_combobox.currentText(),
                    0
                )
            )
        self.field_label_resolution_combobox_connection = connection
        self.field_label_resolution_combobox.currentIndexChanged.connect(connection)

        # Set default field label resolution if it is not available anymore
        target = self.gui.config.get_int("sampling_volume_label_resolution_exponent")
        if target not in label_resolution_options_dict.values():
            Debug(
                self,
                f": Invalid: sampling_volume_label_resolution_exponent = {target}",
                color=Theme.WarningColor,
                force=True
            )
            self.gui.config.set_int(
                "sampling_volume_label_resolution_exponent",
                next(iter(label_resolution_options_dict.items()))[1]  # First value from combobox
            )

        # Select the field label resolution
        target = self.gui.config.get_int("sampling_volume_label_resolution_exponent")
        for i, value in enumerate(label_resolution_options_dict.values()):
            if value == target:
                self.field_label_resolution_combobox.setCurrentIndex(i)

        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def disable_field_labels(self) -> None:
        """
        Disables field labels.
        """
        Debug(self, ".disable_field_labels()")

        self.gui.config.set_bool("display_field_magnitude_labels", False)

        previous_signals_blocked = self.signalsBlocked()
        self.blockSignals(True)
        self.display_field_magnitude_labels_checkbox.setChecked(False)
        self.blockSignals(previous_signals_blocked)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def prevent_excessive_field_labels(self, choice: bool) -> None:
        """
        Prevents displaying an excessive number of field labels.

        @param choice: True lets the user choose; False disables field labels if there is an excessive number of them
        """
        Debug(self, f".prevent_excessive_field_labels(choice={choice})")

        if not self.gui.config.get_bool("display_field_magnitude_labels"):
            return

        if not self.gui.model.sampling_volume.is_valid():
            return

        if not self.gui.model.sampling_volume.get_labels_count() > self.ExcessiveFieldLabelThreshold:
            return

        if choice:

            messagebox = QMessageBox()
            messagebox.setWindowTitle("Excessive Number Of Field Labels")
            messagebox.setIcon(QMessageBox.Question)
            messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            messagebox.setDefaultButton(QMessageBox.No)
            messagebox.setText(
                "You are about to display an excessive number of field labels. "
                "This will be very slow and cannot be interrupted.\n\n"
                "DO YOU WANT TO DISPLAY FIELD LABELS ANYWAY?\n\n"
                "Choosing 'No' will disable field labels immediately.\n\n"
                "Please consider the following before choosing 'Yes':\n"
                "– Save your work first.\n"
                "– Decrease sampling volume resolution.\n"
                "– Decrease field label resolution."
            )
            if messagebox.exec() == QMessageBox.No:
                self.disable_field_labels()

        else:

            self.disable_field_labels()

            messagebox = QMessageBox()
            messagebox.setWindowTitle("Excessive Number Of Field Labels")
            messagebox.setIcon(QMessageBox.Information)
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.setDefaultButton(QMessageBox.Ok)
            messagebox.setText(
                "Field labels were disabled automatically because\n"
                "an excessive number of field labels was detected.\n\n"
                "You may manually re-enable field labels after all calculations have finished."
            )
            messagebox.exec()
