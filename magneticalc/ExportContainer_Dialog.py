""" ExportContainer_Dialog module. """

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
from PyQt5.QtWidgets import QCheckBox
from magneticalc.QtWidgets2.QLabel2 import QLabel2
from magneticalc.QtWidgets2.QDialog2 import QDialog2
from magneticalc.QtWidgets2.QSaveAction import QSaveAction
from magneticalc.API import API
from magneticalc.Debug import Debug
from magneticalc.Field_Types import Field_Types_Names_Map, Field_Types_Abbreviations_Map, field_name_to_type
from magneticalc.Theme import Theme


class ExportContainer_Dialog(QDialog2):
    """ ExportContainer_Dialog class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Initializes the dialog.

        @param gui: GUI
        """
        QDialog2.__init__(self, title="Export Container", width=500)
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.addWidget(QLabel2("Please select items for export", bold=True, color=Theme.MainColor))
        self.addSpacing(8)
        self.addWidget(QLabel2(
            "Fields must have been calculated before they can be exported.", italic=True, color=Theme.LiteColor
        ))
        self.addSpacing(16)

        self.Export_Names_Available_Map = {
            "Wire Points"   : self.gui.model.wire.valid,
            "Wire Current"  : self.gui.model.wire.valid
        }
        self.Export_Names_Available_Map.update({
            field_name: self.gui.model.get_valid_field(field_type) is not None
            for field_type, field_name in Field_Types_Names_Map.items()
        })

        self.checkboxes = {}
        for i, item in enumerate(self.Export_Names_Available_Map.items()):
            item_name, item_available = item
            self.checkboxes[item_name] = QCheckBox(" " + item_name + ("" if item_available else " (not calculated)"))
            self.checkboxes[item_name].setEnabled(item_available)
            self.checkboxes[item_name].setChecked(item_available)
            self.addWidget(self.checkboxes[item_name])

        self.addSpacing(16)

        buttons = self.addButtons({
            "Cancel"            : ("fa.close", self.reject),
            "Save Container …"  : ("fa.save", self.export)
        })
        buttons[1].setFocus()

    def export(self) -> None:
        """
        Exports wire points, current and fields to some HDF5 container file.
        """
        Debug(self, ".export()")

        Export_Names_Selection_Map = {
            item_name: self.checkboxes[item_name].isChecked()
            for item_name, item_available in self.Export_Names_Available_Map.items()
        }

        Export_Names_Abbreviations_Map = {
            "Wire Current"  :   "Current",
            "Wire Points"   :   "Wire"
        }
        Export_Names_Abbreviations_Map.update({
            field_name: Field_Types_Abbreviations_Map[field_type]
            for field_type, field_name in Field_Types_Names_Map.items()
        })
        export_abbreviations_str = "-".join([
            Export_Names_Abbreviations_Map[item_name]
            for item_name, item_selected in Export_Names_Selection_Map.items() if item_selected
        ])

        action = QSaveAction(
            self.gui,
            title="Export Container",
            date=True,
            filename="MagnetiCalc_Export" + (("_" + export_abbreviations_str) if export_abbreviations_str else ""),
            extension=".hdf5",
            _filter="HDF5 Container (*.hdf5)"
        )
        if not action.filename:
            self.reject()
            return

        container = {}
        fields = {}

        for item_name, item_selected in Export_Names_Selection_Map.items():

            if not item_selected:
                continue

            if item_name == "Wire Points":
                wire_points_components = self.gui.model.wire.get_points_sliced().T
                wire_points = dict(zip(["x", "y", "z"], wire_points_components))
                container.update({"wire_points": wire_points})

            elif item_name == "Wire Current":
                wire_current = self.gui.model.wire.get_dc()
                container.update({"wire_current": wire_current})

            else:
                field_type = field_name_to_type(item_name)
                field_components = self.gui.model.get_valid_field(field_type).get_vectors().T
                field_abbreviation = Field_Types_Abbreviations_Map[field_type]
                fields.update(dict(zip(
                    [field_abbreviation + "_x", field_abbreviation + "_y", field_abbreviation + "_z"],
                    field_components
                )))

        if fields != {}:
            fields.update(dict(zip(["nx", "ny", "nz"], self.gui.model.sampling_volume.dimension)))
            fields.update(dict(zip(["x", "y", "z"], self.gui.model.sampling_volume.get_points().T)))
            container.update({"fields": fields})

        API.export_hdf5(action.filename, container)

        self.accept()
