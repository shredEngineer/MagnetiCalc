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

from __future__ import annotations
from PyQt5.QtWidgets import QCheckBox
from magneticalc.QLabel2 import QLabel2
from magneticalc.QDialog2 import QDialog2
from magneticalc.QSaveAction import QSaveAction
from magneticalc.API import API
from magneticalc.Debug import Debug
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class ExportContainer_Dialog(QDialog2):
    """ ExportContainer_Dialog class. """

    def __init__(self, gui: GUI) -> None:
        """
        Prepares the 'Export Container' dialog.

        @param gui: GUI
        """
        QDialog2.__init__(self, title="Export Container", width=500)
        Debug(self, ": Init")
        self.gui = gui

        self.addWidget(QLabel2("Please select items for export", bold=True, color=Theme.MainColor))
        self.addSpacing(8)
        self.addWidget(QLabel2(
            "Fields must have been calculated before they can be exported.", italic=True, color=Theme.LiteColor
        ))
        self.addSpacing(16)

        wire_points_available = self.gui.model.wire.is_valid()
        wire_current_available = self.gui.model.wire.is_valid()

        a_field_available = self.gui.model.get_valid_field(A_FIELD) is not None
        b_field_available = self.gui.model.get_valid_field(B_FIELD) is not None

        calculate_hint = " (not calculated)"

        wire_points_hint = "" if wire_points_available else calculate_hint
        wire_current_hint = "" if wire_current_available else calculate_hint
        a_field_hint = "" if a_field_available else calculate_hint
        b_field_hint = "" if b_field_available else calculate_hint

        self.wire_points_checkbox = QCheckBox(" Wire Points" + wire_points_hint)
        self.wire_current_checkbox = QCheckBox(" Wire Current" + wire_current_hint)
        self.a_field_checkbox = QCheckBox(" A-Field" + a_field_hint)
        self.b_field_checkbox = QCheckBox(" B-Field" + b_field_hint)

        self.wire_points_checkbox.setEnabled(wire_points_available)
        self.wire_current_checkbox.setEnabled(wire_current_available)
        self.a_field_checkbox.setEnabled(a_field_available)
        self.b_field_checkbox.setEnabled(b_field_available)

        self.wire_points_checkbox.setChecked(wire_points_available)
        self.wire_current_checkbox.setChecked(wire_current_available)
        self.a_field_checkbox.setChecked(a_field_available)
        self.b_field_checkbox.setChecked(b_field_available)

        self.addWidget(self.a_field_checkbox)
        self.addWidget(self.b_field_checkbox)
        self.addWidget(self.wire_points_checkbox)
        self.addWidget(self.wire_current_checkbox)

        self.addSpacing(16)

        buttons = self.addButtons({
            "Cancel": ("fa.close", self.reject),
            "Save Container …": ("fa.save", self.export)
        })
        buttons[1].setFocus()

    def export(self) -> None:
        """
        Exports wire points, current and fields to some HDF5 container file.
        """
        Debug(self, ".export()")

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

        action = QSaveAction(
            self.gui,
            title="Export Container",
            date=True,
            filename="MagnetiCalc_Export" + (("_" + export_types_str) if export_types_str else ""),
            extension=".hdf5",
            filter="HDF5 Container (*.hdf5)"
        )
        if action.filename:

            container_dictionary = {}

            fields = {}
            if export_a_field or export_b_field:
                sampling_volume_components = self.gui.model.sampling_volume.get_points().T
                fields.update(dict(zip(["nx", "ny", "nz"], self.gui.model.sampling_volume.dimension)))
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

            API.export_hdf5(action.filename, container_dictionary)

            self.accept()

        else:

            self.reject()
