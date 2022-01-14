""" Project module. """

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

from __future__ import annotations
from typing import Dict, Optional
import re
from PyQt5.QtWidgets import QMessageBox as QMB
from magneticalc.QtWidgets2.QMessageBox2 import QMessageBox2
from magneticalc.Backend_Types import BACKEND_TYPE_CUDA
from magneticalc.Backend_Types import Backend_Types_Available, Backend_Type_Default, backend_type_safe
from magneticalc.Config import Config
from magneticalc.Debug import Debug
from magneticalc.Field_Types import FIELD_TYPE_B, field_type_safe
from magneticalc.Format import Format
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

    def open(self, filename: Optional[str], reload: bool = True) -> bool:
        """
        Opens a project from file, or the default project.

        @param filename: Project filename, or None to load the default project
        @param reload: Enable to reload GUI
        @return: True if successful, False otherwise
        """
        if filename is not None:
            Debug(self, ".open(): Loading project file")
            self.load_file(filename=filename, default_config=Project.get_default())

            if not self.validate():
                Debug(self, ".open(): ERROR: Invalid project file. Using default project.", error=True)

                # Let's try this again with the default project
                self.cleanup()
                filename = None

        if filename is None:
            Debug(self, ".open(): Loading default project")
            self.load(default_config=Project.get_default())

            if not self.validate():
                Debug(self, ".open(): ERROR: Invalid default project. Aborting.", error=True)
                return False

        if reload:
            self.gui.reload()

        return True

    def close(self, invalidate: bool = True) -> bool:
        """
        Attempts to close the project, but lets user choose to cancel closing, or save/discard changes if there are any.

        @param invalidate: Enable to invalidate the GUI afterwards
        @return: False if canceled, True if saved/discarded
        """
        if self.gui.calculation_thread is not None:
            self.gui.interrupt_calculation()

        if not self.synced:
            Debug(self, ".close(): WARNING: Project has unsaved changes", warning=True)

            messagebox = QMessageBox2(
                title="Project Changed",
                text="Do you want to save your changes?",
                icon=QMB.Question, buttons=QMB.Save | QMB.Discard | QMB.Cancel, default_button=QMB.Save
            )
            if not messagebox.user_accepted or messagebox.choice == QMB.Cancel:
                Debug(self, ".close(): Canceled")
                return False
            elif messagebox.choice == QMB.Save:
                Debug(self, ".close(): Saving changes to project", success=True)
                self.save_file()
            else:
                Debug(self, ".close(): WARNING: Discarding changes to project", warning=True)

        if invalidate:
            Debug(self, ".close(): Invalidating GUI")
            self.gui.model.invalidate(do_all=True)
        else:
            Debug(self, ".close(): WARNING: Not invalidating GUI", warning=True)

        self.cleanup()
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

    # ------------------------------------------------------------------------------------------------------------------

    def on_changed(self) -> None:
        """
        Gets called when the project changed.
        """
        name = self.filename or "Default Project"
        self.gui.setWindowTitle(Version.String + " – " + name + ("" if self.synced else " *"))

    # ------------------------------------------------------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Validates the project.

        @return: True if valid project, False otherwise
        """
        Debug(self, f".validate(): Application version string: {Version.String}")

        # Parse project version
        project_version = self.gui.project.get_str("version")
        Debug(self, f".validate(): Project version string: {project_version}")

        # noinspection RegExpAnonymousGroup
        pattern = re.compile(r"MagnetiCalc v(\d+)\.(\d+)\.(\d+)")
        result = pattern.search(project_version)
        if result is None:
            error_head = "Invalid Project"
            error_text = \
                "Cannot determine project version.\n\n" \
                "Opening default project instead."
            Debug(self, f".validate(): ERROR: {error_head}: " + error_text.replace("\n", " "), error=True)
            QMessageBox2(title=error_head, text=error_text, icon=QMB.Warning, buttons=QMB.Ok, default_button=QMB.Ok)
            return False
        project_maj, project_min, project_rev = [int(result.groups()[i]) for i in range(3)]

        # Check for compatible major version
        if project_maj > Version.VERSION_MAJ:
            error_head = "Incompatible Project"
            error_text = \
                "This project was created with a newer major version of MagnetiCalc.\n" \
                "Please upgrade MagnetiCalc!\n\n" \
                "Opening default project instead."
            Debug(self, f".validate(): ERROR: {error_head}: " + error_text.replace("\n", " "), error=True)
            QMessageBox2(title=error_head, text=error_text, icon=QMB.Warning, buttons=QMB.Ok, default_button=QMB.Ok)
            return False

        # Upgrade an older project if necessary
        if not self.upgrade(project_maj, project_min, project_rev):
            error_head = "Failed Upgrade"
            error_text = \
                "Could not upgrade project format.\n\n" \
                "Opening default project instead."
            Debug(self, f".validate(): ERROR: {error_head}: " + error_text.replace("\n", " "), error=True)
            QMessageBox2(title=error_head, text=error_text, icon=QMB.Warning, buttons=QMB.Ok, default_button=QMB.Ok)
            return False

        # Ensure valid backend type
        backend_type = self.gui.project.get_int("backend_type")
        if backend_type != backend_type_safe(backend_type):
            backend_type = self.gui.project.set_get_int("backend_type", backend_type_safe(backend_type))

        # Use default backend if selected backend is not available
        if backend_type != Backend_Type_Default and not Backend_Types_Available[backend_type]:
            Debug(self, ".validate(): WARNING: Selected backend not available, using default backend", warning=True)
            self.gui.project.set_int("backend_type", Backend_Type_Default)

        # Ensure valid field type
        field_type = self.gui.project.get_int("field_type")
        if field_type != field_type_safe(field_type):
            self.gui.project.set_int("field_type", field_type_safe(field_type))

        return True

    # ------------------------------------------------------------------------------------------------------------------

    def upgrade(self, project_maj: int, project_min: int, project_rev: int) -> bool:
        """
        Upgrades the project if necessary.

        @param project_maj: Project major version
        @param project_min: Project minor version
        @param project_rev: Project revision
        @return: False on error, True otherwise
        """
        if 1 <= project_maj < 2:
            if self._upgrade_1_x_x_to_2_x_x():
                info_head = "Upgraded Project"
                info_text = \
                    "You project was upgraded from (1.x.x) to (2.x.x) format."
                Debug(self, f".upgrade(): {info_head}: " + info_text.replace("\n", " "), success=True)
                QMessageBox2(
                    title=info_head, text=info_text, icon=QMB.Information, buttons=QMB.Ok, default_button=QMB.Ok
                )
            else:
                return False

        Debug(self, ".upgrade(): Done", success=True)
        return True

    def _upgrade_1_x_x_to_2_x_x(self) -> bool:
        """
        Upgrades the project from 1.x.x to 2.x.x format.

        @return: True if successful, False otherwise
        """
        Debug(self, ": Upgrading from (1.x.x) to (2.x.x) format", warning=True)

        assert self._parser is not None, "Not initialized"

        if not self._parser.has_section("User"):
            Debug(self, ": ERROR: Missing User section", error=True)
            return False

        # First, we modify the old User section.
        # The "wire_count" key is added, and the "wire_" and "rotational_symmetry_" keys are joined.
        # Then the wire parameters can be accessed as one group in a Config_Collection.
        self._parser["User"]["wire_count"] = "1"
        self.rename_key("wire_points_base", "wire_points_base_1", section="User")
        self.rename_key("wire_stretch", "wire_stretch_1", section="User")
        self.rename_key("wire_slicer_limit", "wire_slicer_limit_1", section="User")
        self.rename_key("wire_dc", "wire_dc_1", section="User")
        self.rename_key("wire_close_loop", "wire_close_loop_1", section="User")
        self.rename_key("rotational_symmetry_count", "wire_rotational_symmetry_count_1", section="User")
        self.rename_key("rotational_symmetry_radius", "wire_rotational_symmetry_radius_1", section="User")
        self.rename_key("rotational_symmetry_axis", "wire_rotational_symmetry_axis_1", section="User")
        self.rename_key("rotational_symmetry_offset", "wire_rotational_symmetry_offset_1", section="User")

        # Then, we upgrade to the latest DEFAULT section.
        # This also upgrades the version string.
        self._parser["DEFAULT"] = self.get_default()

        # Finally, the User section merged with the DEFAULT section, and the User section is deleted.
        # This eliminates redundancy. (Should have done it that way right from the beginning.)
        user_copy = {key: value for key, value in sorted(list(self._parser["User"].items()))}
        self._parser.remove_section("User")
        self._parser["DEFAULT"] = user_copy

        self.synced = False

        return True

    # ------------------------------------------------------------------------------------------------------------------

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
            "wire_points_base_1"                        :
                Format.points_to_str(Wire_Presets.get_by_id("Straight Line")["points"]),
            "wire_stretch_1"                            : "0.1000, 1.0000, 1.0000",
            "wire_slicer_limit_1"                       : "0.0500",
            "wire_dc_1"                                 : "1.0000",
            "wire_close_loop_1"                         : "True",
            "wire_rotational_symmetry_count_1"          : "30",
            "wire_rotational_symmetry_radius_1"         : "1.0000",
            "wire_rotational_symmetry_axis_1"           : "2",
            "wire_rotational_symmetry_offset_1"         : "0",
            "sampling_volume_padding"                   : "-1, 1, 1",
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
