""" Constraint_Editor module. """

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
from typing import List, Dict
from PyQt5.Qt import QShowEvent
from PyQt5.QtWidgets import QSizePolicy
from magneticalc.Constraint import Constraint
from magneticalc.Debug import Debug
from magneticalc.Comparison_Types import comparison_type_to_name
from magneticalc.Config_Group import Config_Collection
from magneticalc.Norm_Types import norm_type_to_name
from magneticalc.QtWidgets2.QDialog2 import QDialog2
from magneticalc.QtWidgets2.QIconLabel import QIconLabel
from magneticalc.QtWidgets2.QPushButton2 import QPushButton2
from magneticalc.QTableWidget2 import QTableWidget2
from magneticalc.QtWidgets2.QTextBrowser2 import QTextBrowser2
from magneticalc.Theme import Theme


class Constraint_Editor(QDialog2):
    """ Constraint_Editor class. """

    # Constraint types
    Constraint_Types = {
        "norm"          : "str",
        "comparison"    : "str",
        "min"           : "float",
        "max"           : "float",
        "permeability"  : "float"
    }

    # Constraint options
    Constraint_Options = [
        [norm_type_to_name(norm_type) for norm_type in Constraint.Norm_Types_Supported],
        [comparison_type_to_name(comparison_type) for comparison_type in Constraint.Comparison_Types_Supported],
        None,
        None,
        None
    ]

    # HTML content
    HTML = f"""
        Lengths in <b>cm</b>. &nbsp; Angles in <b>degrees</b>.<br><br>

        <b style="color: {Theme.MainColor};">Experimental Feature</b><br><br>

        By default, all sampling volume points have relative permeability µ<sub>r</sub> = 1.<br>
        A constraint assigns some other µ<sub>r</sub> to some region of the sampling volume.<br>
        Constraints of identical permeability are effectively intersected (logical AND).<br>
        In case of ambiguous constraints, the ones with maximum permeability take precedence.<br>
        Setting the permeability of some region to zero locally disables the field calculation.
    """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Prepares the constraint editor, but doesn't fully initialize it yet.

        @param gui: GUI
        """
        QDialog2.__init__(self, title="Constraint Editor", width=700)
        Debug(self, ": Init", init=True)
        self.gui = gui

        self._constraint_collection = Config_Collection(
            gui=gui,
            prefix="constraint_",
            types=self.Constraint_Types,
            first_without_suffix=False
        )

        table_icon_label = QIconLabel("Constraints", "mdi.playlist-edit", color=Theme.DarkColor)
        table_add_button = QPushButton2("Add constraint", "fa.plus", self.on_table_row_added)
        table_icon_label.addWidget(table_add_button)
        self.addLayout(table_icon_label)

        self.table = QTableWidget2(
            self.gui,
            _cell_edited_callback_=self.on_table_cell_edited,
            _row_deleted_callback_=self.on_table_row_deleted
        )
        self.table.set_horizontal_header(["Norm", "Comparison", "Min.", "Max.", "µ (relative)"])
        self.table.set_vertical_prefix("constraint_")
        self.table.set_horizontal_types(self.Constraint_Types)
        self.table.set_horizontal_options(self.Constraint_Options)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(self.table)

        self.text_browser = QTextBrowser2(html=self.HTML)
        self.addWidget(self.text_browser)

        self.addButtons({
            "OK": ("fa.check", self.accept)
        })

        self._changed = False

    def showEvent(self, event: QShowEvent) -> None:
        """
        Gets called when the dialog is opened.

        @param event: QShowEvent
        """
        Debug(self, ".showEvent()")
        self.text_browser.fit_to_contents()
        self.table.setFocus()

    @property
    def changed(self) -> bool:
        """
        Returns the "changed" state.
        """
        return self._changed

    @changed.setter
    def changed(self, changed: bool) -> None:
        """
        Sets the "changed" state.
        This updates the window title.
        """
        self._changed = changed
        self.setWindowTitle("Constraint Editor" + (" *" if changed else ""))

    def reload(self) -> None:
        """
        Reloads the constraint editor.
        """
        Debug(self, ".reload()", refresh=True)
        self.update_table()
        self.changed = False

    def update_table(self) -> None:
        """
        Populates the table.
        """
        self.table.clear_rows()
        self.table.set_vertical_header([str(i + 1) for i in range(self.get_count())])
        self.table.set_contents(self.get_constraints())
        self.table.select_last_row(focus=False)

    # ------------------------------------------------------------------------------------------------------------------

    def get_count(self) -> int:
        """
        Gets the number of constraints.

        @return: Number of constraints
        """
        return self._constraint_collection.get_count()

    def get_constraints(self) -> List[Dict]:
        """
        Gets the list of constraints.

        @return: List of constraints
        """
        return self._constraint_collection.get_all_groups()

    # ------------------------------------------------------------------------------------------------------------------

    def on_table_row_added(self) -> None:
        """
        Gets called after a row has been added to the table.
        """
        self._constraint_collection.add_group(values={
            "norm"          : norm_type_to_name(Constraint.Norm_Types_Supported[0]),
            "comparison"    : comparison_type_to_name(Constraint.Comparison_Types_Supported[0]),
            "min"           : "0.0000",
            "max"           : "1.0000",
            "permeability"  : "1.0000"
        })

        self.update_table()
        self.table.select_last_row()
        self.changed = True

    def on_table_cell_edited(self, value: str, row: int, column: int):
        """
        Gets called after a table cell has been edited.

        @param value: Cell value
        @param row: Row index
        @param column: Column index
        """
        self._constraint_collection.set(group_index=row, key=list(self.Constraint_Types.keys())[column], value=value)
        self.changed = True

    def on_table_row_deleted(self, row: int) -> None:
        """
        Gets called after a row has been deleted from the table.

        @param row: Row index
        """
        self._constraint_collection.del_group(row)
        self.update_table()
        self.changed = True
