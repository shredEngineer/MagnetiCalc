""" Constraint_Editor module. """

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

import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QSizePolicy
from magneticalc.Constraint import Constraint
from magneticalc.Debug import Debug
from magneticalc.IconLabel import IconLabel
from magneticalc.Table import Table
from magneticalc.Theme import Theme


class Constraint_Editor(QDialog):
    """ Constraint_Editor class. """

    # Window dimensions
    Width = 800

    # Description dimensions
    DescriptionHeight = 210

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
        Constraint.Norm_ID_List,
        Constraint.Comparison_ID_List,
        None,
        None,
        None
    ]

    def __init__(self, gui):
        """
        Prepares the constraint editor, but doesn't fully initialize it yet

        @param gui: GUI
        """
        QDialog.__init__(self)

        self.gui = gui

        self._constraints = []

        self._changed = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        table_icon_label = IconLabel("mdi.playlist-edit", "Constraints")
        table_add_button = QPushButton()
        table_add_button.setIcon(qta.icon("fa.plus"))
        table_add_button.clicked.connect(self.on_table_row_added)
        table_icon_label.addWidget(table_add_button)
        layout.addWidget(table_icon_label, alignment=Qt.AlignTop)

        self.table = Table(
            self.gui,
            cell_edited_callback=self.on_table_cell_edited,
            row_deleted_callback=self.on_table_row_deleted
        )
        self.table.setMinimumWidth(self.Width)
        self.table.set_horizontal_header(["Norm", "Comparison", "Min.", "Max.", "µ (relative)"])
        self.table.set_vertical_prefix("constraint_")
        self.table.set_horizontal_types(self.Constraint_Types)
        self.table.set_horizontal_options(self.Constraint_Options)
        layout.addWidget(self.table)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # HTML description
        html = f"""
            Lengths in <b>cm</b>. &nbsp; Angles in <b>degrees</b>.<br><br><br>

            <b style="color: {Theme.PrimaryColor};">Experimental Feature</b><br><br>

            By default, all sampling volume points have relative permeability µ<sub>r</sub> = 1.<br>
            A constraint assigns some other µ<sub>r</sub> to some region of the sampling volume.<br>
            Constraints of identical permeability are effectively intersected (logical AND).<br>
            In case of ambiguous constraints, the ones with maximum permeability take precedence.<br>
            Setting the permeability of some region to zero locally disables the field calculation.<br>
        """

        text_browser = QTextBrowser()
        text_browser.setMinimumWidth(self.Width)
        text_browser.setMinimumHeight(self.DescriptionHeight)
        text_browser.setMaximumHeight(self.DescriptionHeight)
        text_browser.setStyleSheet("""
            background: palette(window);
            border: none;
            line-height: 20px;
        """)
        text_browser.setOpenExternalLinks(True)
        text_browser.insertHtml(html)
        text_browser.setFocusPolicy(Qt.NoFocus)
        cursor = text_browser.textCursor()
        cursor.setPosition(0)
        text_browser.setTextCursor(cursor)
        layout.addWidget(text_browser, alignment=Qt.AlignBottom)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        button_box = QHBoxLayout()
        ok_button = QPushButton(qta.icon("fa.check"), "OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button, alignment=Qt.AlignBottom)
        layout.addLayout(button_box)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # This will be called by the SamplingVolume_Widget:
        # self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the constraint editor.
        """
        Debug(self, ".reinitialize()")

        # Initially load the constraints
        self.reload_constraints()
        self.update_table()

        self.clear_changed()

    # ------------------------------------------------------------------------------------------------------------------

    def show(self):
        """
        Shows this dialog.
        """
        self.table.setFocus()
        self.exec()

    def get_changed(self) -> bool:
        """
        Returns the "changed" state of the current session.
        """
        return self._changed

    def clear_changed(self):
        """
        Clears the "changed" state of the current session.
        """
        self._changed = False
        self.update_title()

    def update_title(self):
        """
        Updates the window title.
        """
        self.setWindowTitle(
            "Constraint Editor" +
            (" *" if self.get_changed() else "")
        )

    # ------------------------------------------------------------------------------------------------------------------

    def reload_constraints(self):
        """
        Re-loads the list of constraints.
        """
        self._constraints = []

        for i in range(self.gui.config.get_int("constraint_count")):
            self._constraints.append(self.gui.config.set_get_dict(
                prefix=f"constraint_",
                suffix=f"_{i}",
                types=self.Constraint_Types,
                values=None
            ))

    def get_constraints(self):
        """
        Returns the list of constraints.

        @param: List of constraints
        """
        return self._constraints

    # ------------------------------------------------------------------------------------------------------------------

    def update_table(self):
        """
        Populates the table.
        """
        self.table.clear_rows()
        self.table.set_vertical_header([str(i + 1) for i in range(len(self.get_constraints()))])
        self.table.set_contents(self.get_constraints())
        self.table.select_last_row(focus=False)

    def on_table_row_added(self):
        """
        Gets called after a row has been added to the table.
        """
        count = self.gui.config.get_int("constraint_count") + 1
        self.gui.config.set_int("constraint_count", count)

        self.gui.config.set_get_dict(
            prefix=f"constraint_",
            suffix=f"_{count - 1}",
            types=self.Constraint_Types,
            values={
                "norm"          : Constraint.Norm_ID_List[0],
                "comparison"    : Constraint.Comparison_ID_List[0],
                "min"           : "0.0000",
                "max"           : "1.0000",
                "permeability"  : "1.0000"
            },
        )

        self.reload_constraints()
        self.update_table()
        self.table.select_last_row()

        self._changed = True
        self.update_title()

    def on_table_cell_edited(self, value, row, column):
        """
        Gets called after a table cell has been edited.

        @param value: Cell value
        @param row: Row
        @param column: Column
        """
        key = list(self.Constraint_Types.keys())[column]
        _type = self.Constraint_Types.get(key)
        self.gui.config.set_generic(f"constraint_{key}_{row}", _type, value)
        self.reload_constraints()

        self._changed = True
        self.update_title()

    def on_table_row_deleted(self, index):
        """
        Gets called after a row has been deleted from the table.

        @param index: Row index
        """
        count = self.gui.config.get_int("constraint_count")

        assert count > 0
        assert index < count

        # Remove all constraints from configuration
        for i in range(count):
            for key in self.Constraint_Types.keys():
                self.gui.config.remove_key(f"constraint_{key}_{i}")

        # Remove selected constraint from internal list
        del self._constraints[index]

        # Add all remaining constraints to configuration again (regenerate keys)
        for i, constraint in enumerate(self.get_constraints()):
            self.gui.config.set_get_dict(
                prefix=f"constraint_",
                suffix=f"_{i}",
                types=self.Constraint_Types,
                values=constraint
            )

        self.gui.config.set_int("constraint_count", count - 1)

        self.update_table()

        self._changed = True
        self.update_title()
