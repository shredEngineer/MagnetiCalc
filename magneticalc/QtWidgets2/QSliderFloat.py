""" QSliderFloat module. """

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider


class QSliderFloat(QSlider):
    """ QSliderFloat class. """

    def __init__(
            self,
            orientation: Qt.Orientation,
            minimum: float,
            maximum: float,
            step: float
    ) -> None:
        """
        Initializes a slider supporting float values.

        @param orientation: Orientation
        @param step: Step value
        @param minimum: Minimum value
        @param maximum: Maximum value
        """
        QSlider.__init__(self, orientation)
        self._step = step
        self.setMinimum(round(minimum / self._step))
        self.setMaximum(round(maximum / self._step))
        self.setSingleStep(1)

    def setValue(self, value: float) -> None:
        """
        Sets the slider value.

        @param value: Slider value
        """
        super().setValue(round(value / self._step))

    def get_value(self) -> float:
        """
        Returns the slider value.

        @return: Slider value
        """
        return super().value() * self._step
