""" QDoubleSpinBox2 module. """

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
from typing import Callable
from PyQt5.QtWidgets import QDoubleSpinBox, QSizePolicy


class QDoubleSpinBox2(QDoubleSpinBox):
    """ QDoubleSpinBox2 class. """

    def __init__(
            self,
            gui: GUI,  # type: ignore
            minimum: float,
            maximum: float,
            step: float,
            precision: int,
            value: int,
            value_changed: Callable
    ) -> None:
        """
        Initializes a floating-point spinbox.

        @param gui: GUI
        @param minimum: Minimum value
        @param maximum: Maximum value
        @param step: Step
        @param precision: Precision
        @param value: Initial value
        @param value_changed: Value changed callback
        """
        QDoubleSpinBox.__init__(self)
        self.setLocale(gui.user_locale)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.setSingleStep(step)
        self.setDecimals(precision)
        self.valueChanged.connect(value_changed)  # type: ignore
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
