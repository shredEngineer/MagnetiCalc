""" Display_Widget module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QVBoxLayout, QMessageBox, QSizePolicy
from magneticalc.QMessageBox2 import QMessageBox2
from magneticalc.Debug import Debug
from magneticalc.QGroupBox2 import QGroupBox2
from magneticalc.QHLine import QHLine
from magneticalc.QIconLabel import QIconLabel
from magneticalc.QLabel2 import QLabel2
from magneticalc.SamplingVolume_Widget import SamplingVolume_Widget
from magneticalc.QSliderFloat import QSliderFloat
from magneticalc.Theme import Theme
from magneticalc.VisPyCanvas import VisPyCanvas


class Display_Widget(QGroupBox2):
    """ Display_Widget class. """

    # Slider limits
    FieldArrowHeadScaleMin = 0
    FieldArrowHeadScaleMax = 1
    FieldArrowHeadScaleStep = 1 / VisPyCanvas.FieldArrowHeadSize
    FieldArrowLineScaleMin = 0
    FieldArrowLineScaleMax = 1
    FieldArrowLineScaleStep = 1 / 10
    FieldPointScaleMin = 0
    FieldPointScaleMax = 1
    FieldPointScaleStep = 1 / VisPyCanvas.FieldPointSize
    FieldBoostMin = 0
    FieldBoostMax = 1
    FieldBoostStep = 1 / 20

    # Warn about displaying an excessive number of field labels
    ExcessiveFieldLabelsThreshold = 250

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Populates the widget.

        @param gui: GUI
        """
        QGroupBox2.__init__(self, "Display")
        Debug(self, ": Init", init=True)
        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addLayout(QIconLabel("Point Scale", "fa.circle"))
        self.field_point_scale_slider = QSliderFloat(
            orientation=Qt.Horizontal,
            minimum=self.FieldPointScaleMin,
            maximum=self.FieldPointScaleMax,
            step=self.FieldPointScaleStep
        )
        self.field_point_scale_slider.valueChanged.connect(  # type: ignore
            lambda: self.set_field_point_scale(self.field_point_scale_slider.get_value())
        )
        self.addWidget(self.field_point_scale_slider)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Arrow Scale", "fa.arrow-right"))

        field_arrow_scale_layout_left = QVBoxLayout()
        field_arrow_scale_layout_right = QVBoxLayout()

        field_arrow_scale_layout_left.addWidget(QLabel2("Head:", expand=False))
        self.field_arrow_head_scale_slider = QSliderFloat(
            orientation=Qt.Horizontal,
            minimum=self.FieldArrowHeadScaleMin,
            maximum=self.FieldArrowHeadScaleMax,
            step=self.FieldArrowHeadScaleStep
        )
        self.field_arrow_head_scale_slider.valueChanged.connect(  # type: ignore
            lambda: self.set_field_arrow_head_scale(self.field_arrow_head_scale_slider.get_value())
        )
        field_arrow_scale_layout_right.addWidget(self.field_arrow_head_scale_slider)

        field_arrow_scale_layout_left.addWidget(QLabel2("Line:", expand=False))
        self.field_arrow_line_scale_slider = QSliderFloat(
            orientation=Qt.Horizontal,
            minimum=self.FieldArrowLineScaleMin,
            maximum=self.FieldArrowLineScaleMax,
            step=self.FieldArrowLineScaleStep
        )
        self.field_arrow_line_scale_slider.valueChanged.connect(  # type: ignore
            lambda: self.set_field_arrow_line_scale(self.field_arrow_line_scale_slider.get_value())
        )
        field_arrow_scale_layout_right.addWidget(self.field_arrow_line_scale_slider)

        field_arrow_scale_layout = QHBoxLayout()
        field_arrow_scale_layout.addLayout(field_arrow_scale_layout_left)
        field_arrow_scale_layout.addLayout(field_arrow_scale_layout_right)
        self.addLayout(field_arrow_scale_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Field Boost", "fa.adjust"))
        self.field_boost_slider = QSliderFloat(
            orientation=Qt.Horizontal,
            minimum=self.FieldBoostMin,
            maximum=self.FieldBoostMax,
            step=self.FieldBoostStep
        )
        self.field_boost_slider.valueChanged.connect(  # type: ignore
            lambda: self.set_field_boost(self.field_boost_slider.get_value())
        )
        self.addWidget(self.field_boost_slider)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(QHLine())

        self.addLayout(QIconLabel("Field Labels", "fa.tags"))
        self.display_field_magnitude_labels_checkbox = QCheckBox(" Display Magnitude")
        self.display_field_magnitude_labels_checkbox.toggled.connect(  # type: ignore
            lambda: self.set_display_field_magnitude_labels(self.display_field_magnitude_labels_checkbox.isChecked())
        )
        self.addWidget(self.display_field_magnitude_labels_checkbox)

        self.field_label_resolution_combobox = QComboBox()
        self.field_label_resolution_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.field_label_resolution_combobox_connection = None
        field_label_resolution_layout = QHBoxLayout()
        field_label_resolution_layout.addWidget(self.field_label_resolution_combobox)
        field_label_resolution_layout.addWidget(QLabel2(" Labels / cm", expand=False))
        self.addLayout(field_label_resolution_layout)

        total_labels_layout = QHBoxLayout()
        self.total_labels_label = QLabel2("N/A", color=Theme.MainColor, align_right=True)
        total_labels_layout.addWidget(QLabel2("Total labels:", italic=True, color=Theme.LiteColor))
        total_labels_layout.addWidget(self.total_labels_label)
        self.addLayout(total_labels_layout)

    def reload(self) -> None:
        """
        Reloads the widget.
        """
        Debug(self, ".reload()", refresh=True)

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

    def update(self) -> None:
        """
        Updates this widget.
        """
        Debug(self, ".update()", refresh=True)

        self.update_labels()
        self.update_controls()

    def update_labels(self) -> None:
        """
        Updates the labels.
        """
        Debug(self, ".update_labels()", refresh=True)

        if self.gui.model.sampling_volume.valid:
            n = self.gui.model.sampling_volume.get_labels_count()
            color = Theme.FailureColor if n > self.ExcessiveFieldLabelsThreshold else Theme.MainColor
            self.total_labels_label.setText(str(n))
            self.total_labels_label.setStyleSheet(f"color: {color}; font-style: italic;")
        else:
            self.total_labels_label.setText("N/A")
            self.total_labels_label.setStyleSheet(f"color: {Theme.LiteColor}; font-style: italic;")

    def update_controls(self) -> None:
        """
        Updates the field label resolution combobox.
        """
        Debug(self, ".update_controls()", refresh=True)

        # Possible field label resolution values: Less than or equal to sampling volume resolution
        sampling_volume_resolution = self.gui.model.sampling_volume.get_resolution()
        label_resolution_options_dict = {
            key: value for key, value in SamplingVolume_Widget.ResolutionOptionsDict.items()
            if np.power(2.0, value) <= sampling_volume_resolution
        }

        self.blockSignals(True)

        # Re-populate field label resolution combobox
        if self.field_label_resolution_combobox_connection is not None:
            self.field_label_resolution_combobox.currentIndexChanged.disconnect(  # type: ignore
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
        self.field_label_resolution_combobox.currentIndexChanged.connect(connection)  # type: ignore

        # Set default field label resolution if it is not available anymore
        target = self.gui.config.get_int("sampling_volume_label_resolution_exponent")
        if target not in label_resolution_options_dict.values():
            Debug(self, f": WARNING: Invalid: sampling_volume_label_resolution_exponent = {target}", warning=True)
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

    def set_field_point_scale(self, value: float) -> None:
        """
        Sets field point scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_point_scale", value)
        self.gui.redraw()

    def set_field_arrow_head_scale(self, value: float) -> None:
        """
        Sets field arrow head scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_arrow_head_scale", value)
        self.gui.redraw()

    def set_field_arrow_line_scale(self, value: float) -> None:
        """
        Sets field arrow line scale.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_arrow_line_scale", value)
        self.gui.redraw()

    def set_field_boost(self, value: float) -> None:
        """
        Sets field boost value.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.config.set_float("field_boost", value)
        self.gui.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def set_display_field_magnitude_labels(self, value: bool) -> None:
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

    def set_field_label_resolution(self, value: int) -> None:
        """
        Sets field label resolution exponent.

        @param value: Value
        """
        if self.signalsBlocked():
            return

        self.gui.sidebar_left.sampling_volume_widget.set_sampling_volume(_label_resolution_exponent_=value)

        # Note: "prevent_excessive_field_labels()" will be called by "Model.on_sampling_volume_valid()".

        self.gui.redraw()

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

    def prevent_excessive_field_labels(self, choice: bool) -> None:
        """
        Prevents displaying an excessive number of field labels.

        @param choice: True lets the user choose; False disables field labels if there is an excessive number of them
        """
        Debug(self, f".prevent_excessive_field_labels(choice={choice})")

        if not self.gui.config.get_bool("display_field_magnitude_labels"):
            return

        if not self.gui.model.sampling_volume.valid:
            return

        if not self.gui.model.sampling_volume.get_labels_count() > self.ExcessiveFieldLabelsThreshold:
            return

        if choice:
            text = (
                "You are about to display an excessive number of field labels.\n"
                "This will be very slow and cannot be interrupted.\n\n"

                "DO YOU WANT TO DISPLAY FIELD LABELS ANYWAY?\n"
                "Choosing 'No' will disable field labels immediately.\n\n"

                "Please consider the following before choosing 'Yes':\n"
                "– Save your work first.\n"
                "– Decrease sampling volume resolution.\n"
                "– Decrease field label resolution."
            )
            messagebox = QMessageBox2(
                title="Excessive Number Of Field Labels",
                text=text,
                icon=QMessageBox.Question,
                buttons=QMessageBox.Yes | QMessageBox.No,
                default_button=QMessageBox.No
            )
            if not messagebox.user_accepted or messagebox.choice == QMessageBox.No:
                self.disable_field_labels()

        else:

            self.disable_field_labels()

            text = (
                "Field labels were disabled automatically because\n"
                "an excessive number of field labels was detected.\n\n"

                "You may manually re-enable field labels\n"
                "after all calculations have finished."
            )
            QMessageBox2(
                title="Excessive Number Of Field Labels",
                text=text,
                icon=QMessageBox.Information,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
