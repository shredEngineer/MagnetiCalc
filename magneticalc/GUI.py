""" GUI module. """

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

import time
import atexit
from typing import Optional
from sty import fg
import qtawesome as qta
from PyQt5.Qt import QCloseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFileDialog, QMessageBox
from magneticalc.QMessageBox2 import QMessageBox2
from magneticalc.QSaveAction import QSaveAction
from magneticalc import API
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.CalculationThread import CalculationThread
from magneticalc.Config import Config
from magneticalc.Debug import Debug
from magneticalc.Menu import Menu
from magneticalc.Model import Model
from magneticalc.ModelAccess import ModelAccess
from magneticalc.SidebarLeft import SidebarLeft
from magneticalc.SidebarRight import SidebarRight
from magneticalc.Statusbar import Statusbar
from magneticalc.Theme import Theme
from magneticalc.Version import Version
from magneticalc.VispyCanvas import VispyCanvas


class GUI(QMainWindow):
    """ GUI class. """

    # Minimum window size
    MinimumWindowSize = (800, 600)

    # Used by L{Debug}
    DebugColor = fg.blue

    # Default configuration filename
    DefaultFilename = "MagnetiCalc-DefaultProject.ini"

    # These signals are fired from the calculation thread
    calculation_status = pyqtSignal(str)
    calculation_exited = pyqtSignal(bool)

    def __init__(self) -> None:
        """
        Initializes the GUI.
        """
        QMainWindow.__init__(self, flags=Qt.Window)
        Debug(self, ": Init")

        self.locale = QLocale(QLocale.English)

        self.setWindowIcon(qta.icon("ei.magnet", color=Theme.MainColor))
        self.setMinimumSize(*self.MinimumWindowSize)
        self.showMaximized()

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
        # noinspection PyUnresolvedReferences
        self.calculation_status.connect(lambda text: self.statusbar.set_text(text))
        # noinspection PyUnresolvedReferences
        self.calculation_exited.connect(lambda success: self.on_calculation_exited(success))

        self.initializing = True

        # Kick off the field calculation
        if self.config.get_bool("auto_calculation"):
            self.recalculate()
        else:
            self.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def redraw(self) -> None:
        """
        Re-draws the scene.
        """
        Debug(self, ".redraw()")

        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                Debug(self, ".redraw(): WARNING: Skipped because calculation is in progress", warning=True)
                return
            else:
                Debug(self, ".redraw(): WARNING: Setting calculation thread to None", warning=True)
                self.calculation_thread = None

        self.sidebar_right.display_widget.set_enabled(self.model.field.is_valid())

        self.vispy_canvas.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self) -> None:
        """
        Re-calculates the model.
        """
        Debug(self, ".recalculate()")

        if self.calculation_thread is not None:
            Debug(self, ".recalculate(): WARNING: Killing orphaned calculation thread", warning=True)
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

    def on_calculation_exited(self, success: bool) -> None:
        """
        This is called after calculation thread has exited.

        @param success: True if calculation was successful, False otherwise
        """
        Debug(self, f".on_calculation_exited(success={success})")

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
                Debug(self, f".on_calculation_exited(): Success (took {calculation_time:.2f} s)", success=True)
        else:
            Debug(
                self, f".on_calculation_exited(): WARNING: Interrupted after {calculation_time:.2f} s", warning=True)

        # Note: For some reason, most of the time we need an additional ("final-final") re-draw here; VisPy glitch?
        self.redraw()

        self.statusbar.disarm(success)

    def interrupt_calculation(self) -> None:
        """
        Kills any running calculation.
        """
        Debug(self, ".interrupt_calculation()")

        if self.calculation_thread is None:
            Debug(self, ".interrupt_calculation(): WARNING: No calculation thread to interrupt", warning=True)
            return

        if self.calculation_thread.isRunning():
            Debug(self, ".interrupt_calculation(): WARNING: Requesting interruption", warning=True)
            self.calculation_thread.requestInterruption()

            if self.calculation_thread.wait(5000):
                Debug(self, ".interrupt_calculation(): Exited gracefully", success=True)
            else:
                Assert_Dialog(False, "Failed to terminate calculation thread")
                if self.calculation_thread is not None:
                    if self.calculation_thread.isRunning():
                        Debug(self, ".interrupt_calculation(): WARNING: Terminating ungracefully", warning=True)
                        self.calculation_thread.terminate()
                        self.calculation_thread.wait()
        else:
            Debug(self, ".interrupt_calculation(): WARNING: Calculation thread should be running", warning=True)

        self.calculation_thread = None

    # ------------------------------------------------------------------------------------------------------------------

    def confirm_saving_unsaved_work(self, cancelable: bool) -> Optional[bool]:
        """
        Confirm saving unsaved work.

        @param cancelable: True to make dialog cancelable, False to make dialog non-cancelable
        @return: None if canceled, True if saving, False if discarding
        """
        Debug(self, f".confirm_saving_unsaved_work(cancelable={cancelable})")

        buttons = QMessageBox.Save | QMessageBox.Discard | (QMessageBox.Cancel if cancelable else 0)
        messagebox = QMessageBox2(
            title="Project Changed",
            text="Do you want to save your changes?",
            icon=QMessageBox.Question,
            buttons=buttons,
            default_button=QMessageBox.Save
        )
        if messagebox.choice == QMessageBox.Save:
            return True
        elif messagebox.choice == QMessageBox.Discard:
            return False
        else:
            return None

    def confirm_close(self) -> None:
        """
        Called by menu "Quit" action.
        Lets user choose to cancel closing or save / discard file if there is unsaved work.
        """
        Debug(self, ".confirm_close()")

        if not self.config.get_synced():
            choice = self.confirm_saving_unsaved_work(cancelable=True)
            if choice is None:
                Debug(self, ".confirm_close(): Canceled")
                return
            elif choice:
                Debug(self, ".confirm_close(): Saving unsaved work")
                self.config.save()
            else:
                Debug(self, ".confirm_close(): Discarding unsaved work")

        self.close()

    def closeEvent(self, _event: QCloseEvent) -> None:
        """
        Handles close event.

        @param _event: Close event
        """
        Debug(self, ".closeEvent()")

        self.quit()

    def quit(self):
        """
        Quits the application.
        """
        Debug(self, ".quit()")

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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press event.

        @param event: Key press event
        """
        if event.key() == Qt.Key_F2:

            # Focus the  wire base points table
            self.sidebar_left.wire_widget.table.setFocus()

        elif event.key() == Qt.Key_F3:

            # Open the constraint editor
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

    def on_config_changed(self) -> None:
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

    def file_open(self) -> None:
        """
        Opens a project from an INI file.
        """
        Debug(self, ".file_open()")

        # Stop any running calculation
        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                # Cancel the running calculation
                self.interrupt_calculation()

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Project",
            filter="MagnetiCalc INI File (*.ini)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":

            with ModelAccess(self, recalculate=False):
                self.model.invalidate()

            if not self.config.get_synced():
                if self.confirm_saving_unsaved_work(cancelable=False):
                    Debug(self, ".file_open(): Saving unsaved work")
                    self.config.save()
                else:
                    Debug(self, ".file_open(): Discarding unsaved work")

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

            self.vispy_canvas.load_perspective()

            if self.config.get_bool("auto_calculation"):
                self.recalculate()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def file_save(self) -> None:
        """
        Saves the project to the currently set INI file.
        """
        Debug(self, ".file_save()")

        self.config.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def file_save_as(self) -> None:
        """
        Saves the project to an INI file.
        """
        Debug(self, ".file_save_as()")

        action = QSaveAction(
            self,
            title="Save Project",
            date=True,
            filename="MagnetiCalc_Project",
            extension=".ini",
            filter="MagnetiCalc INI File (*.ini)"
        )
        if action.filename:
            self.config.set_filename(action.filename)
            self.config.save()

    # ------------------------------------------------------------------------------------------------------------------

    def file_save_image(self) -> None:
        """
        Saves the currently displayed scene to a PNG file.
        """
        Debug(self, ".file_save_image()")

        action = QSaveAction(
            self,
            title="Save Image",
            date=True,
            filename="MagnetiCalc_Screenshot",
            extension=".png",
            filter="PNG (*.png)"
        )
        if action.filename:
            self.vispy_canvas.save_image(action.filename)

    # ------------------------------------------------------------------------------------------------------------------

    def import_wire(self) -> None:
        """
        Imports wire points from a TXT file.
        """
        Debug(self, ".import_wire()")

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self,
            caption="Import Wire",
            filter="Text File (*.txt)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":

            points = API.import_wire(filename)
            self.sidebar_left.wire_widget.set_wire(
                points=points,
                stretch=[1.0, 1.0, 1.0],
                rotational_symmetry={
                    "count": 1,
                    "radius": 0,
                    "axis": 2,
                    "offset": 0
                }
            )

    def export_wire(self) -> None:
        """
        Exports wire points to a TXT file.
        """
        Debug(self, ".export_wire()")

        if not self.model.wire.is_valid():
            Assert_Dialog(False, "Attempting to export invalid wire")
            return

        action = QSaveAction(
            self,
            title="Export Wire",
            date=True,
            filename="MagnetiCalc_Wire",
            extension=".txt",
            filter="Text File (*.txt)"
        )
        if action.filename:
            API.export_wire(action.filename, self.model.wire.get_points_sliced())
