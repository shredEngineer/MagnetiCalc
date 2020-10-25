""" GUI module. """

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

import os
import time
import atexit
import datetime
import qtawesome as qta
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QFileDialog
from magneticalc.CalculationThread import CalculationThread
from magneticalc.Debug import Debug
from magneticalc.Menu import Menu
from magneticalc.Model import Model
from magneticalc.SidebarLeft import SidebarLeft
from magneticalc.SidebarRight import SidebarRight
from magneticalc.Statusbar import Statusbar
from magneticalc.Version import Version
from magneticalc.VispyCanvas import VispyCanvas


class GUI(QMainWindow):
    """ GUI class. """

    # These signals are fired from the from calculation thread
    calculation_status = pyqtSignal(str)
    calculation_exited = pyqtSignal(bool)

    def __init__(self, config):
        """
        Initializes the GUI.

        @param config: Config
        """
        QMainWindow.__init__(self, flags=Qt.Window)

        Debug(self, ": Init")

        self.config = config

        self.set_window()

        # The calculation thread is started once initially; after that, recalculation is triggered through ModelAccess
        self.calculation_thread = None  # Will be initialized by self.recalculate() but is needed here for ModelAccess
        self.calculation_start_time = None

        # Register exit handler (used by Assert_Dialog to exit gracefully)
        atexit.register(self.quit)

        # Create the model first, as the following objects will access it (each widget acts as view *and* controller)
        self.model = Model(
            # This callback is needed to clear the metric labels after the metric became invalid
            on_metric_invalidated=self.on_metric_invalidated
        )

        # Create the left and right sidebar
        # Note: These create the wire, sampling volume and metric widgets, each populating the model from configuration
        self.sidebar_left = SidebarLeft(self)
        self.sidebar_right = SidebarRight(self)

        # Create the VisPy canvas (our 3D scene) and statusbar
        self.vispy_canvas = VispyCanvas(self)
        self.statusbar = Statusbar(self)

        # Insert left sidebar, VisPy canvas and right sidebar into main layout.
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar_left)
        self.splitter.addWidget(self.vispy_canvas.native)
        self.splitter.addWidget(self.sidebar_right)
        self.setCentralWidget(self.splitter)
        self.splitter.setHandleWidth(8)

        # Insert the menu
        self.menu = Menu(self)

        # Connect the calculation thread communication signals
        self.calculation_status.connect(lambda text: self.statusbar.text(text))
        self.calculation_exited.connect(lambda success: self.on_calculation_exited(success))

        # Kick off the field calculation
        self.recalculate()

    # ------------------------------------------------------------------------------------------------------------------

    def redraw(self):
        """
        Re-draws the scene.
        """
        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                Debug(self, ".redraw(): Skipped because calculation is in progress", color=(0, 0, 255))
                return
            else:
                Debug(self, ".redraw(): WARNING: Setting calculation thread to None", color=(255, 0, 0))
                self.calculation_thread = None

        self.vispy_canvas.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self):
        """
        Re-calculates the model.
        """
        Debug(self, ".recalculate()", color=(0, 128, 0))

        if self.calculation_thread is not None:
            Debug(self, ".recalculate(): WARNING: Killing orphaned calculation thread", color=(255, 0, 0))
            self.interrupt_calculation()

        self.redraw()
        self.statusbar.arm()

        # Create a new calculation thread and kick it off
        self.calculation_thread = CalculationThread(self)
        self.calculation_start_time = time.monotonic()
        self.calculation_thread.start()

    def on_calculation_exited(self, success):
        """
        This is called after calculation thread has exited.

        @param success: Reflects successful calculation
        """
        calculation_time = time.monotonic() - self.calculation_start_time

        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                # Skipping because another thread is now running
                # Note: This happens all the time when calculation is interrupted and restarted through ModelAccess;
                #       we see this because there is no reliable way to revoke the delayed "calculation_exited" signal
                #       after another thread has already been started
                return
            else:
                # This happens when calculation finished and there
                self.calculation_thread = None
                Debug(self, f".on_calculation_exited(): Success (took {calculation_time:.2f} s)", color=(0, 128, 0))
        else:
            Debug(self, f".on_calculation_exited(): Interrupted after {calculation_time:.2f} s", color=(0, 0, 255))

        # Note: For some reason, most of the time we need an additional ("final-final") re-draw here
        self.redraw()

        self.statusbar.disarm(success)

    def interrupt_calculation(self):
        """
        Kills any running calculation.
        """
        if self.calculation_thread is None:
            Debug(self, ".interrupt_calculation: WARNING: No calculation thread to interrupt", color=(255, 0, 0))
            return

        if self.calculation_thread.isRunning():
            Debug(self, ".interrupt_calculation(): Requesting interruption", color=(0, 0, 255))
            self.calculation_thread.requestInterruption()

            if self.calculation_thread.wait(1000):
                Debug(self, ".interrupt_calculation(): Exited gracefully", color=(0, 0, 255))
            else:
                Debug(self, ".interrupt_calculation(): WARNING: Terminating ungracefully", color=(255, 0, 0))
                self.calculation_thread.terminate()
                self.calculation_thread.wait()
        else:
            Debug(self, ".interrupt_calculation: WARNING: Calculation thread should be running", color=(255, 0, 0))

        self.calculation_thread = None

    # ------------------------------------------------------------------------------------------------------------------

    def on_metric_invalidated(self):
        """
        Needed to clear the metric labels after the metric became invalid.
        """
        self.sidebar_right.metric_widget.invalidate_labels()

    # ------------------------------------------------------------------------------------------------------------------

    def set_window(self):
        """
        Sets the basic window properties.
        """

        # Set window title, icon and dimensions
        self.setWindowTitle(Version.String)
        self.setWindowIcon(qta.icon("ei.magnet"))
        self.resize(self.config.get_int("window_width"), self.config.get_int("window_height"))

        # Center window
        fg = self.frameGeometry()
        # noinspection PyArgumentList
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        # noinspection PyArgumentList
        fg.moveCenter(QApplication.desktop().screenGeometry(screen).center())
        self.move(fg.topLeft())

    def quit(self):
        """
        Quits the application.
        """
        if self.calculation_thread != QThread.currentThread():
            Debug(self, ".quit()")
            if self.calculation_thread is not None:
                self.interrupt_calculation()
        else:
            Debug(self, ".quit(): Called from calculation thread (assertion failed)")

        self.config.set_float("azimuth", self.vispy_canvas.view_main.camera.azimuth)
        self.config.set_float("elevation", self.vispy_canvas.view_main.camera.elevation)
        self.config.set_float("scale_factor", self.vispy_canvas.view_main.camera.scale_factor)

        self.config.close()

        print()
        print("Goodbye!")

        # Unregister exit handler (used by Assert_Dialog to exit gracefully)
        atexit.unregister(self.quit)

    def closeEvent(self, _event):
        """
        Handle close event.

        @param _event: Close event
        """
        self.quit()

    def file_save(self):
        """
        Saves the currently displayed scene to PNG file.
        """

        # noinspection PyCallByClass,PyTypeChecker
        filename, _chosen_extension = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_MagnetiCalc"),
            "Portable Network Graphics (*.png)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":
            _file_name, file_extension = os.path.splitext(filename)

            if file_extension.lower() != ".png":
                filename += ".png"

            self.vispy_canvas.save_image(filename)
