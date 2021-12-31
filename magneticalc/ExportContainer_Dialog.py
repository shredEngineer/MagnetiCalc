""" ExportContainer_Dialog module. """

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

import os
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QFileDialog
from magneticalc.API import API
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.QtWidgets2 import QLabel2, QHBoxLayout2, QPushButton2
from magneticalc.Theme import Theme


class ExportContainer_Dialog:
    """ ExportContainer_Dialog class. """

    # Window dimensions
    Width = 500

    def __init__(self, gui) -> None:
        """
        Prepares the 'Export Container' dialog.

        @param gui: GUI
        """
        self.gui = gui

        self.dialog = QDialog()
        self.dialog.setWindowTitle("Export Container")

        layout = QVBoxLayout()
        self.dialog.setMinimumWidth(self.Width)
        self.dialog.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        layout.addWidget(QLabel2("Please select items for export", bold=True, color=Theme.PrimaryColor))
        layout.addSpacing(8)
        layout.addWidget(
            QLabel2(
                "Fields must have been calculated before they can be exported.",
                italic=True, color=Theme.LightColor
            )
        )

        layout.addSpacing(16)

        wire_points_available = self.gui.model.wire.is_valid()
        wire_current_available = self.gui.model.wire.is_valid()

        a_field_available = self.gui.model.get_valid_field(A_FIELD) is not None
        b_field_available = self.gui.model.get_valid_field(B_FIELD) is not None

        calculate_hint = " (not calculated)"

        wire_points_hint = "" if wire_points_available else calculate_hint
        wire_current_hint = "" if wire_current_available else calculate_hint
        a_field_hint = "" if a_field_available else calculate_hint
        b_field_hint = "" if b_field_available else calculate_hint

        self.wire_points_checkbox = QCheckBox(" Wire Points" + wire_points_hint)  # Leading space for alignment
        self.wire_current_checkbox = QCheckBox(" Wire Current" + wire_current_hint)  # Leading space for alignment
        self.a_field_checkbox = QCheckBox(" A-Field" + a_field_hint)  # Leading space for alignment
        self.b_field_checkbox = QCheckBox(" B-Field" + b_field_hint)  # Leading space for alignment

        self.wire_points_checkbox.setEnabled(wire_points_available)
        self.wire_current_checkbox.setEnabled(wire_current_available)
        self.a_field_checkbox.setEnabled(a_field_available)
        self.b_field_checkbox.setEnabled(b_field_available)

        self.wire_points_checkbox.setChecked(wire_points_available)
        self.wire_current_checkbox.setChecked(wire_current_available)
        self.a_field_checkbox.setChecked(a_field_available)
        self.b_field_checkbox.setChecked(b_field_available)

        layout.addWidget(self.a_field_checkbox)
        layout.addWidget(self.b_field_checkbox)
        layout.addWidget(self.wire_points_checkbox)
        layout.addWidget(self.wire_current_checkbox)

        layout.addSpacing(16)

        cancel_button = QPushButton2(self.dialog, "SP_DialogCancelButton", " Cancel", self.reject)
        save_button = QPushButton2(self.dialog, "SP_DialogSaveButton", " Save Container …", self.accept)
        layout.addLayout(
            QHBoxLayout2(
                cancel_button,
                save_button
            )
        )
        save_button.setFocus()

    # ------------------------------------------------------------------------------------------------------------------

    def show(self) -> None:
        """
        Shows this dialog.
        """
        if self.dialog.exec() == 1:
            self.export()

    def reject(self) -> None:
        """
        User chose to abort.
        """
        self.dialog.reject()

    def accept(self) -> None:
        """
        User chose to resume.
        """
        self.dialog.accept()

    # ------------------------------------------------------------------------------------------------------------------

    def export(self) -> None:
        """
        Exports wire points, current and fields to some HDF5 container file.
        """
        export_a_field = self.a_field_checkbox.isChecked()
        export_b_field = self.b_field_checkbox.isChecked()
        export_wire_points = self.wire_points_checkbox.isChecked()
        export_wire_current = self.wire_current_checkbox.isChecked()

        export_types_map = {
            "A": export_a_field,
            "B": export_b_field,
            "Wire": export_wire_points,
            "Current": export_wire_current
        }
        export_types_str = "-".join([string for string, condition in export_types_map.items() if condition])

        filename, _chosen_extension = QFileDialog.getSaveFileName(
            parent=self.gui,
            caption="Export Container",
            directory=datetime.now().strftime("%Y-%m-%d_%H-%M-%S_MagnetiCalc_Export_" + export_types_str),
            filter="HDF5 Container (*.hdf5)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":
            _file_name, file_extension = os.path.splitext(filename)

            if file_extension.lower() != ".hdf5":
                filename += ".hdf5"

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            container_dictionary = {}

            fields = {}
            if export_a_field or export_b_field:
                sampling_volume_components = self.gui.model.sampling_volume.get_points().T
                fields.update(dict(zip(["x", "y", "z"], sampling_volume_components)))
            if export_a_field:
                a_field_components = self.gui.model.get_valid_field(A_FIELD).get_vectors().T
                fields.update(dict(zip(["A_x", "A_y", "A_z"], a_field_components)))
            if export_b_field:
                b_field_components = self.gui.model.get_valid_field(B_FIELD).get_vectors().T
                fields.update(dict(zip(["B_x", "B_y", "B_z"], b_field_components)))
            if export_a_field or export_b_field:
                container_dictionary.update({"fields": fields})

            if export_wire_points:
                wire_points_components = self.gui.model.wire.get_points_sliced().T
                wire_points = dict(zip(["x", "y", "z"], wire_points_components))
                container_dictionary.update({"wire_points": wire_points})

            if export_wire_current:
                wire_current = self.gui.model.wire.get_dc()
                container_dictionary.update({"wire_current": wire_current})

            API.export_hdf5(filename, container_dictionary)
