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
from PyQt5.QtCore import Qt
from magneticalc.QtWidgets2.QDialog2 import QDialog2
from magneticalc.QtWidgets2.QIconLabel import QIconLabel
from magneticalc.QtWidgets2.QPushButton2 import QPushButton2
from magneticalc.QtWidgets2.QTextBrowser2 import QTextBrowser2
from magneticalc.Constraint import Constraint
from magneticalc.Comparison_Types import comparison_type_to_name, comparison_name_to_type
from magneticalc.Config_Group import Config_Collection
from magneticalc.Debug import Debug
from magneticalc.Norm_Types import norm_type_to_name, norm_name_to_type
from magneticalc.QTableView2 import QTableView2
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
        Setting the permeability of some region to zero locally disables the field calculation.<br>
        In case of ambiguous constraints, the ones with maximum permeability take precedence.<br><br>

        Constraints of identical permeability are effectively intersected (logical <code>AND</code> behaviour).<br>
        <i>Note:</i> You can achieve a logical <code>OR</code> behaviour using <i>De Morgan's laws</i>.<br>
        (<code>A</code> <b>Not</b> <i>In Range</i>)
        <code>AND</code>
        (<code>B</code> <b>Not</b> <i>In Range</i>) =
        <b>Not</b> (<code>A</code> <i>In Range</i> <code>OR</code> <code>B</code> <i>In Range</i>).<br>
        This result can then be inverted by letting <code>A</code> and <code>B</code> evaluate to µ<sub>r</sub> = 0.
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

        self.table = QTableView2(
            self.gui,
            row_prefix="constraint_",
            col_keys=["Norm", "Comparison", "Min.", "Max.", "µ (relative)"],
            col_types=self.Constraint_Types,
            col_options=self.Constraint_Options,
            on_cell_edited=self.on_table_cell_edited,
            on_row_deleted=self.on_table_row_deleted
        )
        self.addWidget(self.table)

        self.text_browser = QTextBrowser2(html=self.HTML)
        self.addWidget(self.text_browser, alignment=Qt.AlignBottom)

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
        self.table.set_data(
            data=[list(col_data.values()) for col_data in self.rows],
            row_keys=[str(i + 1) for i in range(self.rows_count)]
        )
        self.table.select_last_row(focus=False)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def rows(self) -> List[Dict]:
        """
        Gets the list of rows (constraint groups).

        @return: List of rows (constraint groups).
        """
        return self._constraint_collection.get_all_groups()

    @property
    def rows_count(self) -> int:
        """
        Gets the number of rows (constraint groups).

        @return: Number of rows (constraint groups)
        """
        return self._constraint_collection.get_count()

    def get_constraints(self) -> List[Constraint]:
        """
        Gets the list of constraints.

        @return: List of constraints
        """
        constraints = []
        for row in self.rows:
            Debug(self, f".get_constraints(): {row}")
            constraints.append(
                Constraint(
                    norm_name_to_type(row["norm"]),
                    comparison_name_to_type(row["comparison"]),
                    row["min"],
                    row["max"],
                    row["permeability"]
                )
            )
        return constraints

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
