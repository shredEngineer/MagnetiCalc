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

from functools import *
import qtawesome as qta
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Table(QTableWidget):
    """ Table class. """

    def __init__(self, height=None, enabled=True, cell_edited_callback=None, row_deleted_callback=None, minimum_rows=2):
        """
        Initializes table.

        @param height: Sets the exact table height (if not None)
        @param cell_edited_callback: Set this to make cells editable
        @param row_deleted_callback: Set this to make rows deletable
        @param minimum_rows: Minimum number of rows (no further rows can be deleted)
        """
        QTableWidget.__init__(self)

        if height is not None:
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)

        self.enabled = enabled
        self.cell_edited_callback = cell_edited_callback
        self.row_deleted_callback = row_deleted_callback
        self.minimum_rows = minimum_rows

        if self.cell_edited_callback is not None:
            self.itemChanged.connect(self.cell_edited_callback)

        self.setStyleSheet("""
            QTableCornerButton::section {
                border-width: 1px;
                border-style: solid;
                border-color: white silver silver white;
            }

            QTableWidget::item {
                padding: 2;
            }
        """)

    def set_horizontal_header(self, header):
        """
        Sets horizontal header.

        @param header: List of row header strings
        """
        if self.row_deleted_callback is not None:
            header.append("")

        self.setColumnCount(len(header))

        for col_index, label in enumerate(header):
            item = QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.setHorizontalHeaderItem(col_index, item)
            self.horizontalHeader().setSectionResizeMode(col_index, QHeaderView.Stretch)

    def set_vertical_header(self, header):
        """
        Sets vertical header.

        @param header: List of column header strings
        """
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

    def clear_rows(self):
        """ Clears table rows. """
        self.setRowCount(0)

    def set_contents(self, contents):
        """
        Sets table contents.

        @param contents: 2D array
        """
        self.blockSignals(True)

        for row_index, row_contents in enumerate(contents):
            for col_index, col_contents in enumerate(row_contents):

                item = QTableWidgetItem(col_contents)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                flags = Qt.NoItemFlags
                if self.enabled:
                    flags |= Qt.ItemIsEnabled
                if self.cell_edited_callback is not None:
                    flags |= Qt.ItemIsEditable
                item.setFlags(flags)

                self.setItem(row_index, col_index, item)

            if self.row_deleted_callback is not None:
                delete_button = QPushButton()
                delete_button.setIcon(qta.icon("fa.minus"))
                delete_button.setStyleSheet("""
                    border: none;
                    background: palette(window);
                """)

                if self.rowCount() <= self.minimum_rows:
                    delete_button.setEnabled(False)
                else:
                    delete_button.clicked.connect(partial(self.row_deleted_callback, row_index))

                self.setCellWidget(row_index, self.columnCount() - 1, delete_button)

        self.blockSignals(False)
