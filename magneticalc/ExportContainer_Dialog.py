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
import h5py
import datetime
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, QFileDialog
from magneticalc.Field_Types import A_FIELD, B_FIELD
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

        title_label = QLabel("Please select items for export")
        title_label.setStyleSheet(f"font-weight: bold; color: {Theme.PrimaryColor}")
        layout.addWidget(title_label)

        layout.addSpacing(8)

        hint_label = QLabel("Fields must have been calculated before they can be exported.")
        hint_label.setStyleSheet(f"font-style: italic; color: {Theme.LightColor}")
        layout.addWidget(hint_label)

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

        button_box = QHBoxLayout()

        cancel_button = QPushButton(
            Theme.get_icon(self.dialog, "SP_DialogCancelButton"),
            " Cancel"  # Leading space for alignment
        )
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(cancel_button, alignment=Qt.AlignBottom)

        save_button = QPushButton(
            Theme.get_icon(self.dialog, "SP_DialogSaveButton"),
            " Save Container …"  # Leading space for alignment
        )
        save_button.clicked.connect(self.accept)
        button_box.addWidget(save_button, alignment=Qt.AlignBottom)

        layout.addLayout(button_box)

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

        export_types = []

        if export_a_field:
            export_types.append("A")
        if export_b_field:
            export_types.append("B")
        if export_wire_points:
            export_types.append("Wire")
        if export_wire_current:
            export_types.append("Current")

        export_types_str = "-".join(export_types)

        filename, _chosen_extension = QFileDialog.getSaveFileName(
            parent=self.gui,
            caption="Export Container",
            directory=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_MagnetiCalc_Export_" + export_types_str),
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
                fields.update({
                    "x": np.array(sorted(list(set(sampling_volume_components[0])))),
                    "y": np.array(sorted(list(set(sampling_volume_components[1])))),
                    "z": np.array(sorted(list(set(sampling_volume_components[2]))))
                })

            if export_a_field:
                a_field_components = self.gui.model.get_valid_field(A_FIELD).get_vectors().T
                fields.update({
                    "A_x": np.rehsape(a_field_components[0],(len(fields['x']),len(fields['y']),len(fields['z']))),
                    "A_y": np.reshape(a_field_components[1],(len(fields['x']),len(fields['y']),len(fields['z']))),
                    "A_z": np.reshape(a_field_components[2],(len(fields['x']),len(fields['y']),len(fields['z'])))
                })

            if export_b_field:
                b_field_components = self.gui.model.get_valid_field(B_FIELD).get_vectors().T
                fields.update({
                    "B_x": np.reshape(b_field_components[0],(len(fields['x']),len(fields['y']),len(fields['z']))),
                    "B_y": np.reshape(b_field_components[1],(len(fields['x']),len(fields['y']),len(fields['z']))),
                    "B_z": np.reshape(b_field_components[2],(len(fields['x']),len(fields['y']),len(fields['z'])))
                })

            if export_a_field or export_b_field:
                container_dictionary.update({"fields": fields})

            if export_wire_points:
                wire_points_components = self.gui.model.wire.get_points_sliced().T
                wire_points = {
                    "x": wire_points_components[0],
                    "y": wire_points_components[1],
                    "z": wire_points_components[2]
                }
                container_dictionary.update({"wire_points": wire_points})

            if export_wire_current:
                wire_current = self.gui.model.wire.get_dc()
                container_dictionary.update({"wire_current": wire_current})

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            def dict_to_hdf5_group(hdf5_group, dictionary) -> None:
                """
                Recursively transforms a dictionary into a HDF5 group (in-place).

                @param hdf5_group: HDF5 group
                @param dictionary: Dictionary
                """
                for key in dictionary.keys():
                    if isinstance(dictionary[key], dict):
                        group = hdf5_group.create_group(key)
                        dict_to_hdf5_group(group, dictionary[key])
                    else:
                        hdf5_group[key] = dictionary[key]
                return

            hdf5_group = h5py.File(filename, "w")
            dict_to_hdf5_group(hdf5_group, container_dictionary)
            hdf5_group.close()
