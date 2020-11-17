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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton
from magneticalc.Theme import Theme


class Usage_Dialog(QDialog):
    """ Usage_Dialog class. """

    # Window dimensions
    Width = 800
    Height = 610

    # HTML content
    HTML = f"""
        <h3 style="color: {Theme.PrimaryColor};">First Steps</h3>
        <ul>
            <li>Go to <b>Load Wire Preset</b> to select a basic wire shape.</li>
            <li>Customize the wire's base points inside the spreadsheet.</li>
            <li>Apply some transformations to your basic wire; rotate or stretch its shape.</li>
            <li>Reduce the slicer limit to improve the field calculation accuracy.</li>
            <li>Set the electrical current flowing through your wire.</li>
        </ul>

        <ul>
            <li>
                The sampling volume is the grid over which the field is calculated;<br>
                increase its resolution to the desired level to show every detail of the field.
            </li>
            <li>
                By default, the cuboid sampling volume covers the wire completely;<br>
                however, you may symmetrically adjust its bounding box by adding (subtracting) some padding.
            </li>
            <li>
                <i>Experimental Feature:</i>
                Use the constraint editor to create regions of relative permeability µ<sub>r</sub> ≠ 1.
            </li>
        </ul>

        <ul>
            <li>
                Select the type of field to calculate:
                A-field (vector potential) or
                B-field (flux density).
            </li>
            <li>
                Current element center points may be located very close to sampling volume points;<br>
                as this distance approaches zero, the field magnitude approaches infinity (singular behaviour).<br>
                Therefore, some distance limit must be set to cut-off these infinities during calculation.
            </li>
        </ul>

        <ul>
            <li>
                Select a color/alpha metric to adjust the field's hue/transparency individually.<br>
                Because all metrics are normalized, changes in DC current do not affect the field color/alpha;<br>
                however, the displayed metric limits linearly scale with the DC current.
            </li>
        </ul>

        <ul>
            <li>Take a look at the minimum and maximum magnetic flux densities reached in each metric.</li>
            <li>
                For a more accurate coil energy and self-inductance calculation,<br>
                ensure that the sampling volume encloses a large, non-singular portion of the field.
            </li>
        </ul>

        <ul>
            <li>Use the scroll wheel to zoom in and out of the 3D scene.</li>
            <li>Click and drag into the 3D scene to rotate.</li>
            <li>Press SHIFT while dragging to <i>move</i> the entire 3D scene.</li>
            <li>If you like the result, press CTRL+S to save a screenshot!</li>
        </ul>

        All settings (including your wire shape) are stored in the <code>MagnetiCalc.ini</code> file by default.<br>
        Deleting or renaming this file will restore the default settings.

        <h3 style="color: {Theme.PrimaryColor};">What does MagnetiCalc do?</h3>

        MagnetiCalc calculates the static magnetic flux density, vector potential, energy, self-inductance
        and magnetic dipole moment of arbitrary coils.
        Inside a VisPy / OpenGL-accelerated PyQt5 GUI, the magnetic flux density
        (B-field, in units of <i>Tesla</i>)
        or the magnetic vector potential (A-field, in units of <i>Tesla-meter</i>)
        is displayed in interactive 3D, using multiple metrics for highlighting this field's properties.<br><br>

        <i>Experimental feature:</i> To calculate the energy and self-inductance of permeable (i.e. ferromagnetic)
        materials, different core media can be modeled as regions of variable relative permeability;
        however, core saturation is currently not modeled, leading to excessive flux density values.

        <h3 style="color: {Theme.PrimaryColor};">Who needs MagnetiCalc?</h3>

        MagnetiCalc does its job for hobbyists, students, engineers and researchers of magnetic phenomena.
        I designed MagnetiCalc from scratch, because I didn't want to mess around with expensive and/or
        overly complex simulation software whenever I needed to solve a magnetostatic problem.

        <h3 style="color: {Theme.PrimaryColor};">How does it work?</h3>

        The B-field calculation is implemented using the Biot-Savart law [1],
        employing multiprocessing techniques;
        MagnetiCalc uses just-in-time compilation (JIT) and, if available, GPU-acceleration (CUDA)
        to achieve high-performance calculations.
        Additionally, the use of easily constrainable "sampling volumes"
        allows for selective calculation over grids of arbitrary shape and arbitrary relative permeabilities
        <i>(experimental)</i>.<br><br>

        The shape of any wire is modeled as a 3D piecewise linear curve.
        Arbitrary loops of wire are sliced into differential current elements, each of which
        contributes to the total field magnitude at some fixed 3D grid point,
        summing over the positions of all current elements.<br><br>

        At each grid point, the field is displayed using colored arrows and/or dots;
        field color and alpha transparency are individually mapped using one of the various available metrics.<br><br>

        The coil's energy [2] and self-inductance [3]
        are calculated by summing the squared B-field over the entire sampling volume;
        ensure that the sampling volume encloses a large, non-singular portion of the field.<br><br>

        Additionally, the scalar magnetic dipole moment [4] is calculated by summing over all current elements.<br><br>

        [1]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 204, (5.4).<br>
        [2]: Kraus, Electromagnetics, 4th Edition, p. 269, 6-9-1.<br>
        [3]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 252, (5.157).<br>
        [4]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 216, (5.54).<br>

        <br><br><span style="color: {Theme.PrimaryColor};">
            This and more information about MagnetiCalc can be found in the <code>README.md</code> file.
        </span><br>
        """

    def __init__(self):
        """
        Initializes "Usage" dialog.
        """

        QDialog.__init__(self)

        self.setWindowTitle("Usage")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        button_box = QHBoxLayout()
        ok_button = QPushButton(qta.icon("fa.check"), "OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)
        layout.addLayout(button_box)

    # ------------------------------------------------------------------------------------------------------------------

    def show(self):
        """
        Shows this dialog.
        """
        self.exec()
