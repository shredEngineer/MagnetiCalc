""" Project module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm <anfrage@paulwilhelm.de>
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

from __future__ import annotations
from typing import Dict
from PyQt5.QtWidgets import QMessageBox
from magneticalc.QMessageBox2 import QMessageBox2
from magneticalc.Backend_Types import BACKEND_TYPE_CUDA
from magneticalc.Backend_Types import Backend_Types_Available, Backend_Type_Default, backend_type_safe
from magneticalc.Config import Config
from magneticalc.Debug import Debug
from magneticalc.Field_Types import FIELD_TYPE_B, field_type_safe
from magneticalc.Format import Format
from magneticalc.ModelAccess import ModelAccess
from magneticalc.Perspective_Presets import Perspective_Presets
from magneticalc.Version import Version
from magneticalc.Wire_Presets import Wire_Presets


class Project(Config):
    """ Project class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        """
        Initializes the project class.

        @param gui: GUI
        """
        Config.__init__(self)
        Debug(self, ": Init", init=True)
        self.gui = gui

    def open(self, filename: str) -> None:
        """
        Opens a project.

        @param filename: Project filename
        """
        Debug(self, ".open()")
        self.load_file(filename=filename, default_config=Project.get_default())
        self.validate()

    def close(self) -> bool:
        """
        Attempts to close the project, but lets user choose to cancel closing, or save/discard changes if there are any.

        @return: False if canceled, True if saved/discarded
        """
        if not self.synced:
            Debug(self, ".close(): Project has unsaved changes", warning=True)

            messagebox = QMessageBox2(
                title="Project Changed",
                text="Do you want to save your changes?",
                icon=QMessageBox.Question,
                buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                default_button=QMessageBox.Save
            )
            if not messagebox.user_accepted or messagebox.choice == QMessageBox.Cancel:
                Debug(self, ".close(): Canceled")
                return False
            elif messagebox.choice == QMessageBox.Save:
                Debug(self, ".close(): Saving changes to project", success=True)
                self.save_file()
            else:
                Debug(self, ".close(): Discarding changes to project", warning=True)

        self.on_closing()

        self.close_file()
        Debug(self, ".close(): Project closed")
        return True

    def switch(self, filename: str) -> None:
        """
        Closes the current project and opens another project.

        @param filename: Project filename
        """
        Debug(self, f".switch(): {filename}")

        if not self.close():
            Debug(self, ".switch(): Canceled")
            return

        self.open(filename)

        self.gui.reload()

    # ------------------------------------------------------------------------------------------------------------------

    def on_changed(self) -> None:
        """
        Gets called when the project changed.
        """
        self.gui.setWindowTitle(Version.String + " – " + self.filename + ("" if self.synced else " *"))

    def on_closing(self) -> None:
        """
        Gets called just before the project file is closed.
        Invalidates the model, also needlessly before closing the app, but that's ok.
        """
        with ModelAccess(self.gui, recalculate=False):
            self.gui.model.invalidate(do_all=True)

    # ------------------------------------------------------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validates the project.
        """
        Debug(self.gui, ".validate()")

        # Ensure valid backend type
        backend_type = self.gui.project.get_int("backend_type")
        if backend_type != backend_type_safe(backend_type):
            backend_type = self.gui.project.set_get_int("backend_type", backend_type_safe(backend_type))

        # Use default backend if selected backend is not available
        if backend_type != Backend_Type_Default and not Backend_Types_Available[backend_type]:
            Debug(self.gui, ".validate(): WARNING: Selected backend not available, using default backend", warning=True)
            self.gui.project.set_int("backend_type", Backend_Type_Default)

        # Ensue valid field type
        field_type = self.gui.project.get_int("field_type")
        if field_type != field_type_safe(field_type):
            self.gui.project.set_int("field_type", field_type_safe(field_type))

    @staticmethod
    def get_default() -> Dict:
        """
        Gets the default project.

        @return: Dictionary
        """
        return {
            "version"                                   : Version.String,
            "backend_type"                              : BACKEND_TYPE_CUDA,
            "auto_calculation"                          : "True",
            "num_cores"                                 : "0",
            "wire_points_base"                          :
                Format.points_to_str(Wire_Presets.get_by_id("Straight Line")["points"]),
            "wire_stretch"                              : "0.1000, 1.0000, 1.0000",
            "wire_slicer_limit"                         : "0.0500",
            "wire_dc"                                   : "1.0000",
            "wire_close_loop"                           : "True",
            "rotational_symmetry_count"                 : "30",
            "rotational_symmetry_radius"                : "1.0000",
            "rotational_symmetry_axis"                  : "2",
            "rotational_symmetry_offset"                : "0",
            "sampling_volume_padding"                   : "1, 1, 1",
            "sampling_volume_override_padding"          : "False",
            "sampling_volume_bounding_box"              : "0.000000, 0.000000, 0.000000; 0.000000, 0.000000, 0.000000",
            "sampling_volume_resolution_exponent"       : "3",
            "sampling_volume_label_resolution_exponent" : "0",
            "field_type"                                : FIELD_TYPE_B,
            "field_distance_limit"                      : "0.0008",
            "color_metric"                              : "Log Magnitude",
            "alpha_metric"                              : "Magnitude",
            "field_point_scale"                         : "0.0000",
            "field_arrow_head_scale"                    : "0.7500",
            "field_arrow_line_scale"                    : "0.7500",
            "field_boost"                               : "0.0000",
            "display_field_magnitude_labels"            : "True",
            "show_wire_segments"                        : "True",
            "show_wire_points"                          : "True",
            "show_colored_labels"                       : "True",
            "show_gauss"                                : "False",
            "show_coordinate_system"                    : "True",
            "show_perspective_info"                     : "True",
            "dark_background"                           : "True",
            "azimuth"                                   :
                Format.float_to_str(Perspective_Presets.get_by_id("Isometric")["azimuth"]),
            "elevation"                                 :
                Format.float_to_str(Perspective_Presets.get_by_id("Isometric")["elevation"]),
            "scale_factor"                              : "3.0000",
            "constraint_count"                          : "0"
        }
