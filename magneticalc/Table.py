""" Table module. """

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

from functools import partial
import qtawesome as qta
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QAbstractItemView, QComboBox
from magneticalc.Config import Config
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class Table(QTableWidget):
    """ Table class. """

    # Display settings
    MinimumHeight = 150

    # Used by L{Debug}
    DebugColor = (128, 0, 128)

    def __init__(
            self,
            gui,
            enabled=True,
            cell_edited_callback=None,
            selection_changed_callback=None,
            row_deleted_callback=None,
            minimum_rows: int = 0,
    ):
        """
        Initializes table.

        @param gui: GUI
        @param cell_edited_callback: Set this to make cells editable
        @param selection_changed_callback: Used to inform the GUI that another row was selected
        @param row_deleted_callback: Set this to make rows deletable
        @param minimum_rows: Minimum number of rows (no further rows can be deleted)
        """
        QTableWidget.__init__(self)

        Debug(self, ": Init")

        self.gui = gui

        self._enabled = enabled
        self._cell_edited_callback = cell_edited_callback
        self._selection_changed_callback = selection_changed_callback
        self._row_deleted_callback = row_deleted_callback
        self._minimum_rows = minimum_rows

        self._prefix = None
        self._types = None
        self._options = None

        if self._cell_edited_callback is not None:
            self.itemChanged.connect(self.on_numerical_cell_edited)
            self.cellChanged.connect(self.on_cell_changed)

        if self._selection_changed_callback is not None:
            self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.set_style(border_color="black", border_width=1)
        self.setMinimumHeight(self.MinimumHeight)
        self.setAlternatingRowColors(True)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.setFocusPolicy(Qt.StrongFocus)

    # ------------------------------------------------------------------------------------------------------------------

    def on_cell_changed(self, row: int, column: int):
        """
        Gets called when a cell changed.
        This is only used to correct the strange behaviour after editing a cell.

        @param row: Row
        @param column: Column
        """
        Debug(self, f".on_cell_changed({row}, {column})")

        self.select_cell(row, column)
        self.setFocus()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def on_numerical_cell_edited(self, item):
        """
        Gets called when a numerical cell has been edited.

        @param item: QTableWidgetItem
        """
        Debug(self, f".on_cell_edited()")

        try:
            value = float(item.text().replace(",", "."))
        except ValueError:
            value = 0.0

        value = f"{value:.{Config.FloatPrecision}f}"
        row = item.row()
        column = item.column()

        item.setText(value)

        self._cell_edited_callback(value, row, column)

    def on_combobox_cell_edited(self, combobox, row, column):
        """
        Gets called when a combobox cell has been edited.

        @param combobox: QCombobox
        @param row: Row
        @param column: Column
        """
        Debug(self, f".on_combobox_cell_edited()")

        self._cell_edited_callback(combobox.currentText(), row, column)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def on_selection_changed(self, _selected, _deselected):
        """
        Gets called when the selection changed.

        @param _selected: Currently selected QItemSelection
        @param _deselected: Currently deselected QItemSelection
        """
        if self.signalsBlocked():
            Debug(self, f".on_selection_changed(): Blocked")
            return

        Debug(self, f".on_selection_changed()")
        self._selection_changed_callback()

    def on_row_deleted(self, row: int):
        """
        Gets called when a row was deleted.

        @param row: Row
        """
        Debug(self, f".on_row_deleted({row})")

        self._row_deleted_callback(row)
        self.select_last_row()

    # ------------------------------------------------------------------------------------------------------------------

    def get_selected_row(self):
        """
        Returns the currently selected row index.

        @return: Index of currently selected row (None if none selected)
        """
        if self.selectionModel().hasSelection():
            return self.selectionModel().currentIndex().row()
        else:
            return None

    def is_cell_widget_selected(self):
        """
        Indicates whether a cell widget is selected (as opposed to a cell item).
        """
        row = self.selectionModel().currentIndex().row()
        column = self.selectionModel().currentIndex().column()

        if row == -1 or column == -1:
            return False

        if self._row_deleted_callback is not None:
            if column == self.columnCount() - 1:
                Debug(self, f".is_cell_widget_selected: Ignoring delete button")
                return False

        item = self.item(row, column)
        return item is None

    def select_cell(self, row=None, column=None):
        """
        Selects a cell.
        Any parameter may be left set to None in order to load its value from the selection model.

        @param row: Row
        @param column: Column
        """
        if row is None:
            row = self.selectionModel().currentIndex().row()

        if column is None:
            column = self.selectionModel().currentIndex().column()

        if row == -1 or column == -1:
            Debug(self, f".select_cell({row}, {column}): WARNING: Skipped", color=Theme.WarningColor, force=True)
            return

        item = self.item(row, column)

        if item is None:

            # Select cell widget
            Debug(self, f".select_cell({row}, {column}): Selecting cell widget")
            # widget = self.cellWidget(row, column)

            self.blockSignals(True)
            self.setCurrentCell(row, column)
            self.setFocus()
            self.blockSignals(False)

        else:

            # Select cell item
            Debug(self, f".select_cell({row}, {column}): Selecting cell item")

            item.setSelected(True)
            self.scrollToItem(item, QAbstractItemView.PositionAtCenter)
            self.selectionModel().setCurrentIndex(self.selectedIndexes()[0], QItemSelectionModel.SelectCurrent)

    def select_last_row(self, focus: bool = True):
        """
        Selects the last row.

        @param focus: Enable to focus the table, disable to explicitly clear the visual selection
        """
        if self.rowCount() == 0:
            Debug(self, f".select_last_row(): Skipped for empty table")
            return

        Debug(self, f".select_last_row(): Blocking signals")
        self.blockSignals(True)

        self.select_cell(self.rowCount() - 1, 0)

        if focus:
            if not self.hasFocus():
                self.setFocus()
        else:
            self.clearSelection()

        Debug(self, f".select_last_row(): Unblocking signals")
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_horizontal_header(self, header):
        """
        Sets horizontal header.

        @param header: List of row header strings
        """
        Debug(self, f".set_horizontal_header()")

        if self._row_deleted_callback is not None:
            header.append("")

        self.setColumnCount(len(header))

        for col_index, label in enumerate(header):
            item = QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.setHorizontalHeaderItem(col_index, item)
            self.horizontalHeader().setSectionResizeMode(col_index, QHeaderView.Stretch)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def set_vertical_prefix(self, prefix: str):
        """
        Sets the per-row table prefix.
        Used for mapping cells to configuration; configuration key = prefix + column key + "_" + row index.

        @param prefix: Prefix
        """
        self._prefix = prefix

    def set_horizontal_types(self, types):
        """
        Sets the per-column cell types.
        Used for mapping cells to configuration.

        Note: Currently, *only the keys* are used for mapping cells to configuration;
        the cell options actually determine the cell type, i.e. numerical or combobox.

        @param types: Ordered dictionary of key-value pairs (column key : column type), or None to disable configuration
        """
        self._types = types

    def set_horizontal_options(self, options):
        """
        Sets the per-column cell options.
        This determines if the cell type, i.e. numerical or combobox.

        @param options: List of options for every column; items may be set to None to use numerical cells
        """
        self._options = options

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def set_vertical_header(self, header):
        """
        Sets vertical header.

        @param header: List of column header strings
        """
        Debug(self, f".set_vertical_header()")

        self.setRowCount(len(header))

        for row_index, label in enumerate(header):
            item = QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setVerticalHeaderItem(row_index, item)
            self.verticalHeader().setSectionResizeMode(row_index, QHeaderView.ResizeToContents)

        self.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                padding: 0 3px;
            }
        """)

    # ------------------------------------------------------------------------------------------------------------------

    def clear_rows(self):
        """
        Clears all table rows.
        """
        Debug(self, f".clear_rows()")

        self.setRowCount(0)

    # ------------------------------------------------------------------------------------------------------------------

    def set_contents(self, contents):
        """
        Sets the table contents.

        @param contents: 2D array
        """
        Debug(self, f".set_contents(): Blocking signals")
        self.blockSignals(True)

        # Iterate over rows
        for row_index, row_contents in enumerate(contents):

            # Iterate over columns
            for col_index, col_contents in enumerate(row_contents):

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

                # Determine the configuration and type binding of the cell
                has_config = self._types is not None
                has_options = self._options[col_index] is not None

                if has_options:
                    # Create a combobox
                    combobox = QComboBox()

                    for i, text in enumerate(self._options[col_index]):
                        combobox.addItem(text)
                        if has_config:
                            key = list(self._types.keys())[col_index]
                            if text == self.gui.config.get_str(self._prefix + key + "_" + str(row_index)):
                                combobox.setCurrentIndex(i)

                    combobox.currentIndexChanged.connect(
                        partial(self.on_combobox_cell_edited, combobox, row_index, col_index)
                    )

                    self.setCellWidget(row_index, col_index, combobox)

                else:
                    # Create a numerical cell
                    item = QTableWidgetItem(col_contents)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    # Set the cell flags
                    flags = Qt.NoItemFlags | Qt.ItemIsSelectable
                    if self._enabled:
                        flags |= Qt.ItemIsEnabled
                    if self._cell_edited_callback is not None:
                        flags |= Qt.ItemIsEditable
                    item.setFlags(flags)

                    if has_config:
                        key = list(self._types.keys())[col_index]
                        item.setText(self.gui.config.get_str(self._prefix + key + "_" + str(row_index)))

                    self.setItem(row_index, col_index, item)

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if self._row_deleted_callback is not None:
                # Create a delete button
                delete_button = QPushButton()
                delete_button.setIcon(qta.icon("fa.minus"))
                delete_button.setStyleSheet("""
                    border: none;
                    background: palette(window);
                """)

                if self.rowCount() > self._minimum_rows:
                    # Allow this row to be deleted
                    delete_button.clicked.connect(partial(self.on_row_deleted, row_index))
                else:
                    # Don't allow the any more rows to be deleted
                    delete_button.setEnabled(False)

                # Insert the delete button into the last column
                self.setCellWidget(row_index, self.columnCount() - 1, delete_button)

        Debug(self, f".set_contents(): Unblocking signals")
        self.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def set_style(self, border_color: str, border_width: int):
        """
        Sets this widget's style.

        @param border_color: Border color
        @param border_width: Border width
        """
        self.setStyleSheet(f"""
            QTableWidget {{
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

            QTableWidget::item {{
                padding: 2;
            }}
        """)

    # ------------------------------------------------------------------------------------------------------------------

    def focusInEvent(self, _event):
        """
        Gets called when the table gained focus.
        This highlights the border and selects the last-selected cell (if any).

        @param _event: Event
        """
        Debug(self, f".focusInEvent()")

        if self.rowCount() > 0:
            self.select_cell()

        self.set_style(border_color=Theme.PrimaryColor, border_width=2)

    def focusOutEvent(self, _event):
        """
        Gets called when the table lost focus, or when a cell item is being edited, or when a cell widget is selected.
        When not editing, this clears the selection, triggering L{on_selection_changed}

        @param _event: Event
        """
        if self.state() == QAbstractItemView.EditingState:
            Debug(self, f".focusOutEvent(): Ignored in editing mode")
        elif self.is_cell_widget_selected():
            Debug(self, f".focusOutEvent(): Ignored for cell widget")
        else:
            Debug(self, f".focusOutEvent(): Clearing selection")
            self.clearSelection()
            self.set_style(border_color="black", border_width=1)
