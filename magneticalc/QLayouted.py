""" QLayouted module. """

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

from typing import Dict, Tuple, Callable, Union, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLayout, QWidget, QPushButton
from magneticalc.QButtons import QButtons


class QLayouted:
    """ QLayouted class. """

    def __init__(self, direction: str = "vertical") -> None:
        """
        Initializes the QLayouted class.
        This adds a layout and several related functions like addWidget() to the parent class.

        @param direction: Sets "vertical" or "horizontal" layout
        """
        self._layout = QVBoxLayout() if direction == "vertical" else QHBoxLayout()

    def install_layout(self, parent: QWidget) -> None:
        """
        Installs this layout in the parent.
        """
        parent.setLayout(self._layout)

    # noinspection PyPep8Naming
    def addWidget(self, widget, alignment: Optional[Union[Qt.Alignment, Qt.AlignmentFlag]] = None) -> None:
        """
        Adds widget.

        @param widget: QWidget
        @param alignment: Alignment
        """
        if alignment:
            self._layout.addWidget(widget, alignment=alignment)
        else:
            self._layout.addWidget(widget)

    # noinspection PyPep8Naming
    def addLayout(self, layout: QLayout) -> None:
        """
        Adds layout.

        @param layout: QLayout
        """
        self._layout.addLayout(layout)

    # noinspection PyPep8Naming
    def addSpacing(self, spacing: float) -> None:
        """
        Adds spacing.

        @param spacing: Spacing value
        """
        self._layout.addSpacing(spacing)

    # noinspection PyPep8Naming
    def addButtons(self, data: Dict[str, Tuple[str, Callable]]) -> Dict[Union[int, str], QPushButton]:
        """
        Adds buttons.

        @param data: Dictionary {text: (icon, callback)}
        @return: Dictionary {text: QPushButton}
        """
        buttons = QButtons(data)
        self.addLayout(buttons)
        return buttons.dictionary
