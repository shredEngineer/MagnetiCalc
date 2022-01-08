""" QTableView2 module. """

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
from typing import Any, Optional, List, Dict, Callable
from functools import partial
from PyQt5 import QtCore
from PyQt5.Qt import QFocusEvent
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QAbstractTableModel, QVariant
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QComboBox, QSizePolicy
from magneticalc.QtWidgets2.QPushButton2 import QPushButton2
from magneticalc.Debug import Debug
from magneticalc.Format import Format
from magneticalc.Theme import Theme


class TableModel(QAbstractTableModel):
    """ TableModel class. """

    def __init__(
            self,
            parent: QTableView,
            data: List[List],
            row_keys: List[str],
            col_keys: List[str],
            col_is_widget: Optional[List[bool]] = None
    ) -> None:
        """
        Initializes a table model.

        @param parent: QTableView
        @param data: Data (2D)
        @param row_keys: List of vertical header strings
        @param col_keys: List of horizontal header strings
        @param col_is_widget: Indicates columns contains only widgets instead of only data (may be None for data-only)
        """
        QAbstractTableModel.__init__(self, parent=parent)
        self._data = data
        self._row_keys = row_keys
        self._col_keys = col_keys
        self._col_is_widget = col_is_widget

    def is_widget(self, index: QtCore.QModelIndex) -> bool:
        """
        Checks if the cell is a widget button.

        @param index: Cell index
        @return: True if the cell is a widget, False otherwise
        """
        return False if self._col_is_widget is None else self._col_is_widget[index.column()]

    def rowCount(self, parent: QtCore.QModelIndex = None):
        """
        Gets the number of rows.

        @return: Number of rows
        """
        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = None):
        """
        Gets the number of columns.
        Note: Enabling allow_delete adds an extra column for the row delete buttons.

        @return: Number of columns
        """
        return len(self._data[0]) if self.rowCount() > 0 else 0

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """
        Sets a cell value.

        @param index: Cell index
        @param value: Cell value
        @param role: Data role
        @return: True if successful, False otherwise
        """
        if role == Qt.EditRole:
            if not self.is_widget(index):
                self._data[index.row()][index.column()] = value
                self.dataChanged.emit(index, index)  # type: ignore
                return True
        return False

    def data(self, index: QtCore.QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        """
        Gets a cell value.

        @param index: Cell index
        @param role: Data role
        @return: Cell value
        """
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if not self.is_widget(index):
                return self._data[index.row()][index.column()]
        return QVariant()

    def flags(self, index: QtCore.QModelIndex) -> int:
        """
        Gets the flags for a cell.

        @param index: Cell index
        @return: Cell flags
        """
        if self.is_widget(index):
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> QVariant:
        """
        Sets the header data.

        @param section: Row or column
        @param orientation: Orientation
        @param role: Data role
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._col_keys[section])
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(self._row_keys[section])
        return QVariant()


class QTableView2(QTableView):
    """ QTableView2 class. """

    def __init__(
            self,
            gui: GUI,  # type: ignore
            col_keys: List[str],
            col_types: Optional[Dict] = None,
            col_options: Optional[List] = None,
            row_allow_delete: bool = True,
            row_count_minimum: int = 0,
            row_prefix: str = "",
            on_cell_edited: Optional[Callable] = None,
            on_selection_changed: Optional[Callable] = None,
            on_row_deleted: Optional[Callable] = None
    ) -> None:
        """
        Initializes a table.

        @param gui: GUI
        @param col_keys: List of horizontal header strings
        @param col_types: Per-column cell types used for binding cells to configuration.
                          Ordered dictionary of key-value pairs (column key : column type) or None to disable binding.
                          Note: Currently, *only the keys* are used for binding cells to project configuration;
                          the cell options actually determine the cell type, i.e. numerical or combobox.
        @param col_options: Per-column cell options. This determines the cell type, i.e. numerical or combobox.
                            List of options for every column; items may be set to None to use numerical cells.
        @param row_allow_delete: Enable to add an extra column for row delete buttons
        @param row_count_minimum: Minimum number of rows (no further rows can be deleted)
        @param row_prefix: Per-row prefix used for binding cells to configuration
                           (key = prefix + column key + "_" + row index)
        @param on_cell_edited: Set this to make cells editable
        @param on_selection_changed: Used to inform the GUI that another row was selected
        @param on_row_deleted: Set this to make rows deletable
        """
        QTableView.__init__(self)
        Debug(self, ": Init", init=True)
        self.gui = gui

        self._allow_delete = row_allow_delete
        self._row_count_minimum = row_count_minimum
        self._row_prefix = row_prefix
        self._col_keys = col_keys
        self._col_types = col_types
        self._col_options = col_options
        self._on_cell_edited = on_cell_edited
        self._on_selection_changed = on_selection_changed
        self._on_row_deleted = on_row_deleted

        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_style(border_color="black", border_width=1)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

    def set_style(self, border_color: str, border_width: int) -> None:
        """
        Sets this widget's style.

        @param border_color: Border color
        @param border_width: Border width
        """
        self.setStyleSheet(f"""
            QTableView {{
                border: {border_width}px solid {border_color};
                border-radius: 5px;
                padding: 1px;
                margin: {2 - border_width}px;
            }}

            QTableCornerButton::section {{
                border-width: 1px;
                border-style: solid;
                border-color: white silver silver white;
            }}

            QTableView::item {{
                padding: 2;
            }}
        """)

    # ------------------------------------------------------------------------------------------------------------------

    def set_data(
            self,
            data: List[List[str]],
            row_keys: List[str]
    ) -> None:
        """
        Sets the table contents.

        @param data: Data (2D)
        @param row_keys: List of vertical header strings
        """
        Debug(self, ".set_data()")

        if self.model() is not None:
            # Disconnect previously set up callbacks
            if self._on_cell_edited is not None:
                self.model().dataChanged.disconnect(self.on_data_changed)  # type: ignore
            if self._on_selection_changed is not None:
                self.selectionModel().selectionChanged.disconnect(self.on_selection_changed)  # type: ignore

        # Initialize cells that are bound to the project configuration
        if self._col_types is not None:
            for row, row_data in enumerate(data):
                for col, col_data in enumerate(data):
                    key = list(self._col_types.keys())[col]
                    data[row][col] = self.gui.project.get_str(self._row_prefix + key + "_" + str(row))

        # Indicate if a column contains only widgets (only data otherwise)
        if self._col_options is not None:
            col_is_widget = [col_options is not None for col_options in self._col_options] + \
                ([True] if self._allow_delete else [])
        else:
            col_is_widget = None

        # Initialize the table model
        # Note: If enabled, this adds an empty column for row delete buttons
        self.setModel(
            TableModel(
                parent=self,
                data=[col_data + ([""] if self._allow_delete else []) for col_data in data],
                row_keys=row_keys,
                col_keys=self._col_keys + ([""] if self._allow_delete else []),
                col_is_widget=col_is_widget
            )
        )

        # Connect callbacks
        if self._on_cell_edited is not None:
            self.model().dataChanged.connect(self.on_data_changed)  # type: ignore
        if self._on_selection_changed is not None:
            self.selectionModel().selectionChanged.connect(self.on_selection_changed)  # type: ignore

        # Set column style
        for col in range(self.model().columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

        # Set row style
        for row in range(self.model().rowCount()):
            self.verticalHeader().setSectionResizeMode(row, QHeaderView.ResizeToContents)
        self.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                padding: 0 3px;
            }
        """)

        # Add row delete buttons if desired
        if self._allow_delete:
            for row in range(self.model().rowCount()):
                delete_button = QPushButton2("", "fa.minus", css="border: none; background: palette(window);")
                if self.model().rowCount() > self._row_count_minimum:
                    delete_button.clicked.connect(  # type: ignore
                        partial(self.on_row_deleted, row)
                    )
                else:
                    delete_button.setEnabled(False)
                self.setIndexWidget(self.model().index(row, self.model().columnCount() - 1), delete_button)

        # Add combo boxes if desired
        if self._col_options is not None:
            for row, row_data in enumerate(data):
                for col, col_data in enumerate(row_data):
                    if self._col_options[col] is not None:
                        combobox = QComboBox()

                        for i, text in enumerate(self._col_options[col]):
                            combobox.addItem(text)

                            # Cell is bound to project configuration:
                            if self._col_types is not None:
                                key = list(self._col_types.keys())[col]
                                if text == self.gui.project.get_str(self._row_prefix + key + "_" + str(row)):
                                    combobox.setCurrentIndex(i)

                        combobox.currentIndexChanged.connect(  # type: ignore
                            partial(self.on_combobox_cell_edited, combobox, row, col)
                        )

                        self.setIndexWidget(self.model().index(row, col), combobox)

    # ------------------------------------------------------------------------------------------------------------------

    def on_data_changed(self, top_left_index: QtCore.QModelIndex, _bottom_right_index: QtCore.QModelIndex) -> None:
        """
        Gets called when the data in a selection changed.
        Note: Always assuming only a single cell is selected.

        @param top_left_index: Model index of the top left selection bounds
        @param _bottom_right_index: Model index of the bottom right selection bounds
        """
        row, col = top_left_index.row(), top_left_index.column()
        Debug(self, f".on_cell_changed({row}, {col})")

        data = str(self.model().data(top_left_index))
        try:
            value = float(data.replace(",", "."))
        except ValueError:
            value = 0.0
        value = Format.float_to_str(value)

        if self._on_cell_edited is not None:
            self._on_cell_edited(value, row, col)

    def on_combobox_cell_edited(self, combobox: QComboBox, row: int, column: int) -> None:
        """
        Gets called when a combobox cell has been edited.

        @param combobox: QCombobox
        @param row: Row index
        @param column: Column index
        """
        Debug(self, ".on_combobox_cell_edited()")

        if self._on_cell_edited is not None:
            self._on_cell_edited(combobox.currentText(), row, column)

    def on_row_deleted(self, row: int) -> None:
        """
        Gets called when a row was deleted.

        @param row: Row
        """
        Debug(self, f".on_row_deleted({row})")

        if self._on_row_deleted is not None:
            self._on_row_deleted(row)

        self.select_last_row()

    # ------------------------------------------------------------------------------------------------------------------

    def select_cell(self, row: Optional[int] = None, col: Optional[int] = None) -> None:
        """
        Selects a cell.
        Any parameter may be left set to None in order to load its value from the selection model.

        @param row: Row
        @param col: Column
        """
        index = self.selectionModel().currentIndex()
        if row is None:
            row = row or index.row()
        if col is None:
            col = col or index.column()
        if row == -1 or col == -1:
            Debug(self, ".select_cell(): Skipped for missing selection", warning=True)
            return
        Debug(self, f".select_cell({row}, {col})")
        self.selectionModel().setCurrentIndex(self.model().index(row, col), QItemSelectionModel.SelectCurrent)
        self.scrollTo(index)

    def select_last_row(self, focus: bool = True) -> None:
        """
        Selects the last row.

        @param focus: Enable to focus the table, disable to explicitly clear the visual selection
        """
        if self.model().rowCount() == 0:
            Debug(self, ".select_last_row(): Skipped for empty table", warning=True)
            return

        Debug(self, ".select_last_row()")

        self.blockSignals(True)

        self.select_cell(self.model().rowCount() - 1, 0)

        if focus:
            if not self.hasFocus():
                self.setFocus()
        else:
            self.clearSelection()

        self.blockSignals(False)

    def get_selected_row(self) -> Optional[int]:
        """
        Returns the currently selected row index.

        @return: Index of currently selected row (None if none selected)
        """
        if self.selectionModel().hasSelection():
            return self.selectionModel().currentIndex().row()
        else:
            return None

    def on_selection_changed(self, _selected: QItemSelection, _deselected: QItemSelection) -> None:
        """
        Gets called when the selection changed.

        @param _selected: Currently selected QItemSelection
        @param _deselected: Currently deselected QItemSelection
        """
        if self.signalsBlocked():
            return

        Debug(self, ".on_selection_changed()")

        if self._on_selection_changed is not None:
            self._on_selection_changed()

    def focusInEvent(self, _event: QFocusEvent) -> None:
        """
        Gets called when the table gained focus.
        This highlights the border and selects the last-selected cell (if any).

        @param _event: QFocusEvent
        """
        Debug(self, ".focusInEvent()")

        if self.model().rowCount() > 0:
            self.select_cell()

        self.set_style(border_color=Theme.MainColor, border_width=2)

    def focusOutEvent(self, _event: QFocusEvent) -> None:
        """
        Gets called when the table lost focus, or when a cell is being edited.
        When not editing, this clears the selection, triggering L{on_selection_changed()}.

        @param _event: QFocusEvent
        """
        if self.state() == QAbstractItemView.EditingState:
            Debug(self, ".focusOutEvent(): Ignored in editing mode")
        else:
            self.clearSelection()
            self.set_style(border_color="black", border_width=1)
