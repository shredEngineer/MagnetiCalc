""" Theme module. """

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

from PyQt5.Qt import QFont, QSize


class Theme:
    """ Theme class. """

    # Theme colors
    MainColor = "#2c82b8"
    LiteColor = "#555555"
    DarkColor = "#12344a"
    SuccessColor = "#2e7d32"
    FailureColor = "#c62828"
    QuestionColor = "#ff8c00"
    DialogTextColor = "#000000"

    # Default font
    MonoFontFamily = "DejaVu Sans Mono"
    MonoFontSize = 11
    MonoFont = QFont(MonoFontFamily, MonoFontSize)
    MonoFont.setStyleHint(QFont.Monospace)

    IconSizeSmall = QSize(16, 16)
    IconSizeBig = QSize(48, 48)
