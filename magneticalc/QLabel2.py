""" QLabel2 module. """

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

from typing import Optional, Union, Tuple
from PyQt5.Qt import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy


class QLabel2(QLabel):
    """ QLabel2 class. """

    def __init__(
            self,
            text: str,
            expand: bool = True,
            align_right: bool = False,
            **kwargs,
    ) -> None:
        """
        Initializes a QLabel.

        Please see L{set()} for supported arguments.

        @param text: Text
        @param expand: Enable to expand
        @param align_right: Enable to align right
        """
        QLabel.__init__(self)

        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        else:
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        if align_right:
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self.setAlignment(Qt.AlignVCenter)

        self.set(text, **kwargs)

    def set(
            self,
            text: str,
            font: Optional[QFont] = None,
            bold: bool = False,
            italic: bool = False,
            color: Union[str, Tuple[int, int, int]] = "black"
    ) -> None:
        """
        Sets the label properties.

        @param text: Text
        @param font: QFont
        @param bold: Enable for bold text
        @param italic: Enable for italic text
        @param color: Text color
        """
        self.setText(text)

        if font:
            self.setFont(font)

        stylesheet_map = {
            "font-weight: bold": bold,
            "font-weight: italic": italic,
            f"color: {color}": color
        }
        self.setStyleSheet(";".join([string for string, condition in stylesheet_map.items() if condition]))
