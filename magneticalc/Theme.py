""" Theme module. """

#  ISC License
#
#  Copyright (c) 2020–2021, Paul Wilhelm <anfrage@paulwilhelm.de>
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

from PyQt5.QtWidgets import QWidget, QStyle


class Theme:
    """ Theme class. """

    # Theme colors
    PrimaryColor = "#2c82b8"
    LightColor = "#555555"
    SuccessColor = "#2e7d32"
    WarningColor = "#c62828"

    @staticmethod
    def get_icon(widget: QWidget, name: str):
        """
        Gets a PyQt5 standard icon by name.

        @param widget: Base QWidget
        @param name: Name
        @return: PyQt5 icon
        """
        return widget.style().standardIcon(getattr(QStyle, name))
