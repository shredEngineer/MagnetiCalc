""" Usage_Dialog module. """

#  ISC License
#
#  Copyright (c) 2020, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

import qtawesome as qta
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Usage_Dialog(QDialog):
    """ Usage_Dialog class. """

    # Window dimensions
    Width = 800
    Height = 590

    # HTML content
    HTML = f"""
        <h3 style="color: #2a7db0;">First Steps</h3>
        <ul>
            <li>Go to <b>Load Wire Preset</b> to select a basic wire shape.</li>
            <li>Customize the wire's base points inside the spreadsheet.</li>
            <li>Apply some transformations to your basic wire; rotate or stretch its shape.</li>
            <li>Reduce the slicer limit to improve the B-field calculation accuracy.</li>
            <li>Set a DC current flowing through your wire.</li> 
        </ul>

        <ul>
            <li>
                The sampling volume is the grid over which the B-field is calculated;<br>
                increase its resolution to the desired level to show every detail of the field.
            </li>
            <li>
                By default, the cuboid sampling volume covers the wire completely;<br>
                however, you may symmetrically adjust its bounding box by adding (subtracting) some padding. 
            </li>
        </ul>

        <ul>
            <li>
                Select a color/alpha metric to adjust the field's hue/transparency individually.<br>
                Because all metrics are normalized, changes in DC current do not affect the field hue/transparency;
                however, the displayed metric limits linearly scale with the DC current. 
            </li> 
        </ul>

        <ul>
            <li>Take a look at the minimum and maximum magnetic flux densities reached in each metric.</li>
        </ul>

        <ul>
            <li>Use the scroll wheel to zoom in and out of the 3D scene.</li>
            <li>Click and drag into the 3D scene to rotate.</li>
            <li>Press SHIFT while dragging to <i>move</i> the entire 3D scene.</li>
            <li>If you like the result, press CTRL+S to save a screenshot!
        </ul>

        All settings (including your wire shape) are stored in the <code>MagnetiCalc.ini</code> file.<br>
        Deleting or renaming this file will restore the default settings.

        <h3 style="color: #2a7db0;">What does MagnetiCalc do?</h3>
        
        MagnetiCalc calculates the magnetic field of arbitrary air coils, examples included.<br>
        Inside this VisPy-accelerated PyQt5 GUI, the static magnetic flux density (B-field due to a DC current)<br>
        is displayed in interactive 3D, using multiple metrics for highlighting this field's properties.<br>
        All parameters and presets can interactively be changed inside the GUI.
        
        <h3 style="color: #2a7db0;">Who needs MagnetiCalc?</h3>
        
        MagnetiCalc does its job for hobbyists, students, engineers and researchers of magnetic phenomena.<br>
        I designed MagnetiCalc from scratch, because I didn't want to mess around with expensive and/or<br>
        overly complex simulation software whenever I needed to solve a magnetostatic problem.
        
        <h3 style="color: #2a7db0;">How does it work?</h3>
        
        The field calculation is implemented using the Biot-Savart law <span style="color: #2a7db0;">[1]</span>,
        employing multiprocessing techniques.<br>
        The use of easily constrainable "sampling volumes" allows for selective calculation over arbitrary shapes.<br>
        <br>
        The shape of any wire is modeled as a 3D piecewise linear curve.<br>
        Arbitrary loops of wire are sliced into differential current elements,<br>
        each of which contributes to the total magnetic flux density B at some fixed 3D grid point.<br>
        <br>
        At each grid point, the field is displayed using colored arrows and/or dots;<br>
        field color and alpha transparency are individually mapped using one of the various available metrics.<br>
        <br>
        <span style="color: #2a7db0;">[1]</span>: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 204, (5.4).<br>
        <br>
        <br>
        <span style="color: #2a7db0;">
            This and more information about MagnetiCalc can be found in the <code>README.md</code> file.
        </span>
        <br>
        """

    def __init__(self):
        """
        Displays "Usage" dialog.
        """

        # noinspection PyArgumentList
        QDialog.__init__(self)

        self.setWindowTitle("Usage")

        layout = QVBoxLayout()
        self.setLayout(layout)

        text_browser = QTextBrowser()
        text_browser.setMinimumWidth(self.Width)
        text_browser.setMinimumHeight(self.Height)
        text_browser.setStyleSheet("""
            background: palette(window);
            border: none;
            line-height: 20px;
        """)
        text_browser.setOpenExternalLinks(True)
        text_browser.insertHtml(Usage_Dialog.HTML)
        text_browser.setFocusPolicy(Qt.NoFocus)
        cursor = text_browser.textCursor()
        cursor.setPosition(0)
        text_browser.setTextCursor(cursor)
        layout.addWidget(text_browser)

        button_box = QHBoxLayout()
        ok_button = QPushButton(qta.icon("fa.check"), "OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)
        layout.addLayout(button_box)

    def show(self):
        """ Shows this dialog. """
        self.exec()
