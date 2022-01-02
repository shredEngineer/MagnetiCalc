""" QButtons module. """

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

from typing import Dict, Tuple, Callable, Union
import qtawesome as qta
from PyQt5.QtWidgets import QHBoxLayout, QPushButton


class QButtons(QHBoxLayout):
    """ QButtons class. """

    def __init__(
            self,
            data: Dict[str, Tuple[str, Callable]]
    ) -> None:
        """
        Initializes a horizontal layout containing multiple buttons.

        @param data: Dictionary {text: (icon, callback)}
        """
        QHBoxLayout.__init__(self)

        self.dictionary: Dict[Union[int, str], QPushButton] = {}

        for n, key_val in enumerate(data.items()):
            text, tup = key_val
            icon, callback = tup

            button = QPushButton(qta.icon(icon), " " + text)
            # noinspection PyUnresolvedReferences
            button.clicked.connect(callback)
            self.addWidget(button)

            self.dictionary[n] = button
            self.dictionary[text] = button
