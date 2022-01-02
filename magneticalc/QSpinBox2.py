""" QSpinBox2 module. """

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

from typing import Callable
from PyQt5.QtWidgets import QSpinBox


class QSpinBox2(QSpinBox):
    """ QSpinBox2 class. """

    def __init__(
            self,
            minimum: int,
            maximum: int,
            value: int,
            value_changed: Callable
    ) -> None:
        """
        Initializes a spinbox.

        @param minimum: Minimum value
        @param maximum: Maximum value
        @param value: Initial value
        @param value_changed: Value changed callback
        """
        QSpinBox.__init__(self)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        # noinspection PyUnresolvedReferences
        self.valueChanged.connect(value_changed)
