""" CheckForUpdates_Dialog module. """

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

import re
from urllib.request import urlopen
from PyQt5.Qt import QFont, QSize
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from magneticalc.QtWidgets2 import QPushButton2, QLabel2
from magneticalc.Debug import Debug
from magneticalc.IconLabel import IconLabel
from magneticalc.Theme import Theme
from magneticalc.Version import __VERSION__, __VERSION__URL__


class CheckForUpdates_Dialog(QDialog):
    """ CheckForUpdates_Dialog class. """

    # Window dimensions
    Width = 500

    def __init__(self) -> None:
        """
        Prepares the 'Check for Updates' dialog.
        """
        QDialog.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Check for Updates")
        self.setMinimumWidth(self.Width)

        update_hint = False

        try:
            version_py = urlopen(__VERSION__URL__, timeout=2).read().decode("utf-8")
        except:
            icon, string, color = "fa.exclamation-circle", f"Network Error", Theme.WarningColor
        else:

            pattern = re.compile(r'__VERSION__ = "v(\d+)\.(\d+)\.(\d+)"')
            try:
                version = "v" + ".".join(pattern.search(version_py).groups())
            except:
                icon, string, color = "fa.exclamation-circle", f"Invalid Format", Theme.WarningColor
            else:

                if version > __VERSION__:
                    icon, string, color = "fa.info-circle", f"Newer version available: {version}", Theme.SuccessColor
                    update_hint = True
                elif version == __VERSION__:
                    icon, string, color = "fa.check-circle", f"Up-to-date: {version}", Theme.PrimaryColor
                else:
                    icon, string, color = "fa.exclamation-circle", f"Ahead of Release {version}", Theme.WarningColor

        Debug(self, f": Check for Updates ({__VERSION__URL__}): {string}", color=color, force=True)
        icon_label = IconLabel(icon, string, color, color, font=QFont("DejaVu Sans Mono", 14), size=QSize(32, 32))
        layout.addWidget(icon_label)

        if update_hint:
            layout.addSpacing(8)
            layout.addWidget(QLabel2("Please update now:", italic=True))
            layout.addSpacing(8)
            cmd = QTextEdit("python3 -m pip install magneticalc --upgrade")
            cmd.setFont(QFont("DejaVu Sans Mono", 12))
            cmd.setMaximumHeight(64)
            cmd.setReadOnly(True)
            layout.addWidget(cmd)

        layout.addSpacing(8)
        layout.addWidget(QPushButton2(self, "SP_DialogCloseButton", " Close", self.accept))

    # ------------------------------------------------------------------------------------------------------------------

    def show(self) -> None:
        """
        Shows this dialog.
        """
        self.exec()
