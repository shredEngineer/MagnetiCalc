""" GUI module. """

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

import time
import atexit
from sty import fg
import qtawesome as qta
from PyQt5.Qt import QCloseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMainWindow, QSplitter, QMessageBox
from magneticalc.QMessageBox2 import QMessageBox2
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
from magneticalc.VisPyCanvas import VisPyCanvas


class GUI(QMainWindow):
    """ GUI class. """

    # Used by L{Debug}
    DebugColor = fg.blue

    # Minimum window size
    MinimumWindowSize = (800, 600)

    # Default configuration filename
    DefaultFilename = "MagnetiCalc-DefaultProject.ini"

    # These signals are fired from the calculation thread
    calculation_status = pyqtSignal(str)
    calculation_exited = pyqtSignal(bool)

    # Used by ModelAccess to invalidate the statusbar
    invalidate_statusbar = pyqtSignal()

    def __init__(self) -> None:
        """
        Initializes the GUI.
        """
        QMainWindow.__init__(self, flags=Qt.Window)
        Debug(self, ": Init", init=True)

        self.user_locale = QLocale(QLocale.English)

        self.setWindowIcon(qta.icon("ei.magnet", color=Theme.MainColor))
        self.setMinimumSize(*self.MinimumWindowSize)
        self.showMaximized()

        self.config = Config()
        self.config.set_changed_callback(self.on_config_changed)
        self.config.set_filename(self.DefaultFilename)
        self.config.load()

        # The calculation thread is started once initially; after that, recalculation is triggered through ModelAccess
        self.calculation_thread = None  # Will be initialized by "recalculate()" but is needed here for ModelAccess
        self.calculation_start_time = time.monotonic()  # Will be overwritten by "recalculate()"

        # Register exit handler (used by Assert_Dialog to exit gracefully)
        atexit.register(self.cleanup)

        # Create the statusbar first, as it connects to the "invalidate_statusbar" signal emitted by ModelAccess
        self.statusbar = Statusbar(self)
        self.invalidate_statusbar.connect(self.statusbar.invalidate)  # type: ignore

        # Create the model next, as the following objects will access it (each widget acts as view *and* controller)
        self.model = Model(self)

        # Create the left and right sidebar
        # Note: These create the wire, sampling volume, field, metric and parameters widgets,
        #       each populating the model from config
        self.sidebar_left = SidebarLeft(self)
        self.sidebar_right = SidebarRight(self)

        # Create the VisPy canvas (our 3D scene)
        self.vispy_canvas = VisPyCanvas(self)
        self.vispy_canvas.native.setFocusPolicy(Qt.NoFocus)  # Don't let VisPy gain control – handle all events in GUI

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
        self.calculation_status.connect(  # type: ignore
            lambda text: self.statusbar.set_text(text)
        )
        self.calculation_exited.connect(  # type: ignore
            lambda success: self.on_calculation_exited(success)
        )

        self.initializing = True

        self.reload()

    # ------------------------------------------------------------------------------------------------------------------

    def reload(self) -> None:
        """
        Reloads the GUI.
        """
        self.sidebar_left.wire_widget.reload()
        self.sidebar_left.sampling_volume_widget.reload()
        self.sidebar_right.field_widget.reload()
        self.sidebar_right.metric_widget.reload()
        self.sidebar_right.parameters_widget.reload()
        self.sidebar_right.perspective_widget.reload()
        self.sidebar_right.display_widget.reload()

        self.menu.reload()
        self.statusbar.reload()

        self.vispy_canvas.load_perspective()

        if self.config.get_bool("auto_calculation"):
            self.recalculate()
        else:
            self.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def redraw(self) -> None:
        """
        Re-draws the scene.
        """
        if self.calculation_thread is not None:
            if self.calculation_thread.isRunning():
                Debug(self, ".redraw(): WARNING: Skipped because calculation is in progress", warning=True)
                return
            else:
                Debug(self, ".redraw(): WARNING: Setting calculation thread to None", warning=True)
                self.calculation_thread = None
        else:
            Debug(self, ".redraw()")

        self.sidebar_right.display_widget.setEnabled(self.model.field.valid)

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
                    f".on_calculation_exited(success={success}): "
                    f"Took {calculation_time:.2f} s",
                    success=success
                )
        else:
            Debug(
                self,
                f".on_calculation_exited(success={success}): "
                f"WARNING: Interrupted after {calculation_time:.2f} s",
                warning=True
            )

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Gets called when the window is closed (programmatically through close() or manually)

        @param event: Close event
        """
        Debug(self, ".closeEvent()")

        closed = self.close_project(cancelable=True)
        if not closed:
            event.ignore()
            return

        self.cleanup()

    def cleanup(self):
        """
        Perform clean-up upon quitting the application.
        """
        Debug(self, ".cleanup()")

        if self.calculation_thread != QThread.currentThread():
            if self.calculation_thread is not None:
                self.interrupt_calculation()
        else:
            Debug(self, ".quit(): Called from calculation thread (assertion failed)")

        print()
        print("Goodbye!")

        # Unregister exit handler (used by Assert_Dialog to exit gracefully)
        atexit.unregister(self.cleanup)

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

    # ------------------------------------------------------------------------------------------------------------------

    def close_project(self, cancelable: bool) -> bool:
        """
        Confirm closing the project.
        Let user choose to cancel closing, or save/discard changes if there is unsaved work.

        @param cancelable: True to make dialog cancelable, False to make dialog non-cancelable
        @return: False if canceled, True if saved/discarded
        """
        if not self.config.get_synced():
            Debug(self, ".close_project(): Project has unsaved changes", warning=True)

            messagebox = QMessageBox2(
                title="Project Changed",
                text="Do you want to save your changes?",
                icon=QMessageBox.Question,
                buttons=QMessageBox.Save | QMessageBox.Discard | (QMessageBox.Cancel if cancelable else 0),
                default_button=QMessageBox.Save
            )
            if not messagebox.user_accepted or messagebox.choice == QMessageBox.Cancel:
                Debug(self, ".close_project(): Canceled")
                return False
            elif messagebox.choice == QMessageBox.Save:
                Debug(self, ".close_project(): Saving changes to project", success=True)
                self.config.save()
            else:
                Debug(self, ".close_project(): Discarding changes to project", warning=True)

        self.config.close()
        Debug(self, ".close_project(): Project closed")
        return True

    def switch_project(self, filename: str) -> None:
        """
        Switches to another project file.
        """
        Debug(self, f".switch_project(): {filename}", warning=True)

        if not self.close_project(cancelable=True):
            Debug(self, ".switch_project(): Canceled")
            return

        with ModelAccess(self, recalculate=False):
            self.model.invalidate(do_all=True)

        self.config.set_filename(filename)
        self.config.load()

        self.reload()
