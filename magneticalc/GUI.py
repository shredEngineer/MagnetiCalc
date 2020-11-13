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
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFileDialog, QDesktopWidget
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.CalculationThread import CalculationThread
from magneticalc.Config import Config
from magneticalc.Debug import Debug
from magneticalc.Menu import Menu
from magneticalc.Model import Model
from magneticalc.SidebarLeft import SidebarLeft
from magneticalc.SidebarRight import SidebarRight
from magneticalc.Statusbar import Statusbar
from magneticalc.Theme import Theme
from magneticalc.Version import Version
from magneticalc.VispyCanvas import VispyCanvas


class GUI(QMainWindow):
    """ GUI class. """

    # Default configuration filename
    DefaultFilename = "MagnetiCalc.ini"

    # These signals are fired from the calculation thread
    calculation_status = pyqtSignal(str)
    calculation_exited = pyqtSignal(bool)

    def __init__(self):
        """
        Initializes the GUI.
        """
        QMainWindow.__init__(self, flags=Qt.Window)

        Debug(self, ": Init")

        self.locale = QLocale(QLocale.English)

        self.set_window()

        self.config = Config()
        self.config.set_changed_callback(self.on_config_changed)
        self.config.set_filename(self.DefaultFilename)
        self.config.load()

        # The calculation thread is started once initially; after that, recalculation is triggered through ModelAccess
        self.calculation_thread = None  # Will be initialized by self.recalculate() but is needed here for ModelAccess
        self.calculation_start_time = None

        # Register exit handler (used by Assert_Dialog to exit gracefully)
        atexit.register(self.quit)

        # Create the model first, as the following objects will access it (each widget acts as view *and* controller)
        self.model = Model(self)

        # Create the left and right sidebar
        # Note: These create the wire, sampling volume, field and metric widgets, each populating the model from config
        self.sidebar_left = SidebarLeft(self)
        self.sidebar_right = SidebarRight(self)

        # Create the VisPy canvas (our 3D scene) and statusbar
        self.vispy_canvas = VispyCanvas(self)
        self.vispy_canvas.native.setFocusPolicy(Qt.NoFocus)  # Don't let VisPy gain control -- handle all events in GUI
        self.statusbar = Statusbar(self)

        # Insert left sidebar, VisPy canvas and right sidebar into main layout.
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar_left)
        self.splitter.addWidget(self.vispy_canvas.native)
        self.splitter.addWidget(self.sidebar_right)
        self.setCentralWidget(self.splitter)
        self.splitter.setHandleWidth(8)

        # Create the menu
        self.menu = Menu(self)

        # Connect the calculation thread communication signals
        self.calculation_status.connect(lambda text: self.statusbar.text(text))
        self.calculation_exited.connect(lambda success: self.on_calculation_exited(success))

        self.initializing = True

        # Kick off the field calculation
        if self.config.get_bool("auto_calculation"):
            self.recalculate()
        else:
            self.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def redraw(self):
        """
        Re-draws the scene.
        """
        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                Debug(
                    self,
                    ".redraw(): Skipped because calculation is in progress",
                    color=Theme.PrimaryColor,
                    force=True
                )
                return
            else:
                Debug(
                    self,
                    ".redraw(): WARNING: Setting calculation thread to None",
                    color=Theme.WarningColor,
                    force=True
                )
                self.calculation_thread = None

        self.sidebar_right.display_widget.set_enabled(self.model.field.is_valid())

        self.vispy_canvas.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self):
        """
        Re-calculates the model.
        """
        Debug(self, ".recalculate()", color=Theme.SuccessColor)

        if self.calculation_thread is not None:
            Debug(
                self,
                ".recalculate(): WARNING: Killing orphaned calculation thread",
                color=Theme.WarningColor,
                force=True
            )
            self.interrupt_calculation()

        if self.initializing:
            self.initializing = False
            self.vispy_canvas.initializing = True

        self.redraw()
        self.statusbar.arm()

        # Create a new calculation thread and kick it off
        self.calculation_thread = CalculationThread(self)
        self.calculation_start_time = time.monotonic()
        self.calculation_thread.start()

    def on_calculation_exited(self, success: bool):
        """
        This is called after calculation thread has exited.

        @param success: True if calculation was successful, False otherwise
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
                # This happens when calculation finished and no other thread was started
                self.calculation_thread = None
                Debug(
                    self,
                    f".on_calculation_exited(): Success (took {calculation_time:.2f} s)",
                    color=Theme.SuccessColor
                )
        else:
            Debug(
                self,
                f".on_calculation_exited(): Interrupted after {calculation_time:.2f} s", color=Theme.PrimaryColor
            )

        # Note: For some reason, most of the time we need an additional ("final-final") re-draw here; VisPy glitch?
        self.redraw()

        self.statusbar.disarm(success)

    def interrupt_calculation(self):
        """
        Kills any running calculation.
        """
        if self.calculation_thread is None:
            Debug(
                self,
                ".interrupt_calculation: WARNING: No calculation thread to interrupt",
                color=Theme.WarningColor,
                force=True
            )
            return

        if self.calculation_thread.isRunning():
            Debug(self, ".interrupt_calculation(): Requesting interruption", color=Theme.PrimaryColor)
            self.calculation_thread.requestInterruption()

            if self.calculation_thread.wait(3000):
                Debug(self, ".interrupt_calculation(): Exited gracefully", color=Theme.PrimaryColor)
            else:
                Assert_Dialog(False, "Failed to terminate calculation thread")
                if self.calculation_thread is not None:
                    if self.calculation_thread.isRunning():
                        Debug(
                            self,
                            ".interrupt_calculation(): WARNING: Terminating ungracefully",
                            color=Theme.WarningColor,
                            force=True
                        )
                        self.calculation_thread.terminate()
                        self.calculation_thread.wait()
        else:
            Debug(
                self,
                ".interrupt_calculation: WARNING: Calculation thread should be running",
                color=Theme.WarningColor,
                force=True
            )

        self.calculation_thread = None

    # ------------------------------------------------------------------------------------------------------------------

    def set_window(self):
        """
        Sets the basic window properties.
        """

        # Set window icon
        self.setWindowIcon(qta.icon("ei.magnet", color=Theme.PrimaryColor))

        # Adjust window dimensions to desktop dimensions
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

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

        self.config.close()

        print()
        print("Goodbye!")

        # Unregister exit handler (used by Assert_Dialog to exit gracefully)
        atexit.unregister(self.quit)

    def closeEvent(self, _event):
        """
        Handles close event.

        @param _event: Close event
        """
        self.quit()

    def keyPressEvent(self, event):
        """
        Handles key press event.

        @param event: Key press event
        """
        if event.key() == Qt.Key_F2:

            # Focus the the wire base points table
            self.sidebar_left.wire_widget.table.setFocus()

        elif event.key() == Qt.Key_F3:

            # Open the the constraint editor
            self.sidebar_left.sampling_volume_widget.open_constraint_editor()

        elif event.key() == Qt.Key_F5:

            # Focus the main window (make sure to un-focus the wire base points table)
            self.setFocus()

            # (Re-)Start calculation
            self.recalculate()

        elif event.key() == Qt.Key_Escape:

            if self.sidebar_left.wire_widget.table.hasFocus():
                # Focus the main window, thus un-focusing the wire base points table
                self.setFocus()
            else:
                # Stop any running calculation
                if self.calculation_thread is not None:
                    if self.calculation_thread.isRunning():
                        # Cancel the running calculation
                        self.interrupt_calculation()

    # ------------------------------------------------------------------------------------------------------------------

    def on_config_changed(self):
        """
        Gets called when the configuration changed.
        """

        # Update the window title
        self.setWindowTitle(
            Version.String +
            " – " +
            self.config.get_filename() +
            ("" if self.config.get_synced() else " *")
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def file_open(self):
        """
        Opens some INI file.
        """

        # Stop any running calculation
        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                # Cancel the running calculation
                self.interrupt_calculation()

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open File",
            filter="MagnetiCalc INI File (*.ini)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":

            self.model.invalidate()

            self.config.close()
            self.config.set_filename(filename)
            self.config.load()

            self.sidebar_left.wire_widget.reinitialize()
            self.sidebar_left.sampling_volume_widget.reinitialize()
            self.sidebar_right.field_widget.reinitialize()
            self.sidebar_right.metric_widget.reinitialize()
            # Parameters_Widget doesn't need reinitialization as it does not access the configuration
            # Perspective_Widget doesn't need reinitialization as it does not access the configuration
            self.sidebar_right.display_widget.reinitialize()

            self.menu.reinitialize()
            self.statusbar.reinitialize()

            if self.config.get_bool("auto_calculation"):
                self.recalculate()
            else:
                self.redraw()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def file_save(self):
        """
        Saves to the currently set INI file.
        """
        self.config.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def file_save_as(self):
        """
        Saves to some INI file.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setWindowTitle("Save As …")
        file_dialog.setNameFilter("MagnetiCalc INI File (*.ini)")
        file_dialog.setOptions(QFileDialog.DontUseNativeDialog)
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                filename = filenames[0]

                _file_name, file_extension = os.path.splitext(filename)

                if file_extension.lower() != ".ini":
                    filename += ".ini"

                self.config.set_filename(filename)
                self.config.save()

    # ------------------------------------------------------------------------------------------------------------------

    def file_save_image(self):
        """
        Saves the currently displayed scene to PNG file.
        """

        filename, _chosen_extension = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Image",
            directory=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_MagnetiCalc"),
            filter="Portable Network Graphics (*.png)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":
            _file_name, file_extension = os.path.splitext(filename)

            if file_extension.lower() != ".png":
                filename += ".png"

            self.vispy_canvas.save_image(filename)
