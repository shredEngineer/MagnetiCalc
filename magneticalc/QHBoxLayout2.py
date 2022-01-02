""" QHBoxLayout2 module. """

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

from typing import Union
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLayout


class QHBoxLayout2(QHBoxLayout):
    """ QHBoxLayout2 class. """

    def __init__(
            self,
            *elements: Union[QWidget, QLayout]
    ) -> None:
        """
        Initializes a horizontal layout with multiple elements at once.

        @param elements: Arbitrary arguments of QWidget and QLayout
        """
        QHBoxLayout.__init__(self)
        for element in elements:
            if isinstance(element, QWidget):
                self.addWidget(element, alignment=Qt.AlignVCenter)
            elif isinstance(element, QLayout):
                self.addLayout(element)
