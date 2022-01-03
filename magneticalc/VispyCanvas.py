""" VispyCanvas module. """

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

from __future__ import annotations
import time
import numpy as np
from typing import Optional
from si_prefix import si_format
from vispy import io, scene, visuals
from vispy.scene.cameras import TurntableCamera
from vispy.visuals.visual import Visual
from magneticalc.Debug import Debug
from magneticalc.Field import Field
from magneticalc.Metric import Metric
from magneticalc.Theme import Theme

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class VispyCanvas(scene.SceneCanvas):
    """ VispyCanvas class. """

    # Font
    DefaultFontFace = Theme.DefaultFontFace
    DefaultFontSize = 9

    # Enable to additionally debug drawing of visuals
    DebugVisuals = False

    # Enable to additionally debug perspective changes
    DebugPerspective = False

    # Base colors
    White = np.array([1, 1, 1, 1])
    Black = np.array([0, 0, 0, 1])

    # Display settings
    FieldArrowHeadSize = 10
    FieldPointSize = 10
    WirePointSize = 4
    WirePointSelectedSize = 10
    WirePointSelectedColor = (1, 0, 0)

    # Zoom limits
    ScaleFactorMin = 1e-3
    ScaleFactorMax = 1e+4

    # Magnitude limit (mitigating divisions by zero)
    MagnitudeLimit = 1e-12

    # Formatting settings
    MagnitudePrecision = 1

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, gui: GUI) -> None:
        """
        Initialize VisPy canvas.

        @param gui: GUI
        """
        scene.SceneCanvas.__init__(self)
        Debug(self, ": Init")

        self.unfreeze()

        self.gui = gui

        self.redraw_start_time: Optional[float] = None

        self.view_main = self.central_widget.add_view()
        self.view_text = self.view_main.add_view()

        self.view_main.camera = TurntableCamera(
            fov=0,  # Use orthographic projection
            translate_speed=3
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.font_manager = visuals.text.text.FontManager(method="gpu")

        self.visual_perspective_info = scene.visuals.create_visual_node(visuals.TextVisual)(
            parent=self.view_text.scene,
            pos=(10, 10),
            anchor_x="left",
            anchor_y="bottom",
            face=self.DefaultFontFace,
            font_size=self.DefaultFontSize,
            font_manager=self.font_manager
        )

        self.visual_field_labels = []  # See: L{create_field_labels}, L{delete_field_labels}, L{redraw_field_labels}

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.visual_coordinate_system = scene.visuals.create_visual_node(visuals.XYZAxisVisual)()

        self.visual_wire_segments = scene.visuals.create_visual_node(visuals.LineVisual)()
        self.visual_wire_points_selected = scene.visuals.create_visual_node(visuals.MarkersVisual)()
        self.visual_wire_points_sliced = scene.visuals.create_visual_node(visuals.MarkersVisual)()
        self.visual_field_points = scene.visuals.create_visual_node(visuals.MarkersVisual)()
        self.visual_field_arrow_lines = scene.visuals.create_visual_node(visuals.LineVisual)()
        self.visual_field_arrow_heads = scene.visuals.create_visual_node(visuals.MarkersVisual)()

        if self.DebugVisuals:
            Debug(self, f": visual_wire_segments        =    {self.visual_wire_segments}")
            Debug(self, f": visual_wire_points_selected = {self.visual_wire_points_selected}")
            Debug(self, f": visual_wire_points_sliced   = {self.visual_wire_points_sliced}")
            Debug(self, f": visual_field_points         = {self.visual_field_points}")
            Debug(self, f": visual_field_arrow_lines    =    {self.visual_field_arrow_lines}")
            Debug(self, f": visual_field_arrow_heads    = {self.visual_field_arrow_heads}")

        self.foreground = None
        self.background = None
        self.update_color_scheme()

        self.initializing = False
        self.visual_startup_info = scene.visuals.create_visual_node(visuals.TextVisual)(
            parent=self.view_text.scene,
            pos=(10, 10 + 2 * self.DefaultFontSize),
            anchor_x="left",
            anchor_y="bottom",
            bold=True,
            text="Performing initial just-in-time compilation;\n"
                 "subsequent calculations will execute faster!\n",
            color=(1, .55, 0),  # Orange
            face=self.DefaultFontFace,
            font_size=self.DefaultFontSize,
            font_manager=self.font_manager
        )

        # Initially load perspective from configuration
        self.load_perspective(redraw=False)

        # Insert perspective change handler
        self.signals_blocked = False
        self.super_perspective_changed = self.view_main.camera.view_changed
        self.view_main.camera.view_changed = self.on_perspective_changed

        self.freeze()

    def update_color_scheme(self) -> None:
        """
        Updates the color scheme.
        """
        Debug(self, ".update_color_scheme()")

        self.foreground = self.White if self.gui.config.get_bool("dark_background") else self.Black
        self.background = self.Black if self.gui.config.get_bool("dark_background") else self.White
        self.bgcolor = self.background
        self.visual_perspective_info.color = np.append(self.foreground[:3], 0.6)

    def set_visible(self, visual: Visual, is_visible: bool) -> None:
        """
        Sets some visual's visibility.

        @param visual: Visual
        @param is_visible: Visibility
        """
        visual.parent = self.view_main.scene if is_visible else None

    def load_perspective(self, redraw: bool = True) -> None:
        """
        Loads perspective from configuration.

        @param redraw: Enable to trigger final re-draw
        """
        Debug(self, ".load_perspective()")

        self.signals_blocked = True
        self.view_main.camera.azimuth = self.gui.config.get_float("azimuth")
        self.view_main.camera.elevation = self.gui.config.get_float("elevation")
        self.view_main.camera.scale_factor = self.gui.config.get_float("scale_factor")
        self.signals_blocked = False

        if redraw:
            self.on_perspective_changed()
            self.redraw()

    def on_perspective_changed(self) -> None:
        """
        Handles a change of perspective.
        """
        if self.DebugPerspective:
            if self.signals_blocked:
                Debug(self, ".on_perspective_changed(): Skipped")
                return
            else:
                Debug(self, ".on_perspective_changed()")

        # Limit scale factor
        if self.view_main.camera.scale_factor > self.ScaleFactorMax:
            self.view_main.camera.scale_factor = self.ScaleFactorMax
        elif self.view_main.camera.scale_factor < self.ScaleFactorMin:
            self.view_main.camera.scale_factor = self.ScaleFactorMin

        if self.view_main.camera.azimuth != self.gui.config.get_float("azimuth"):
            self.gui.config.set_float("azimuth", self.view_main.camera.azimuth)
            if self.DebugPerspective:
                Debug(self, f".on_perspective_changed(): azimuth = {self.view_main.camera.azimuth}")

        if self.view_main.camera.elevation != self.gui.config.get_float("elevation"):
            self.gui.config.set_float("elevation", self.view_main.camera.elevation)
            if self.DebugPerspective:
                Debug(self, f".on_perspective_changed(): elevation = {self.view_main.camera.elevation}")

        if self.view_main.camera.scale_factor != self.gui.config.get_float("scale_factor"):
            self.gui.config.set_float("scale_factor", self.view_main.camera.scale_factor)
            if self.DebugPerspective:
                Debug(self, f".on_perspective_changed(): scale_factor = {self.view_main.camera.scale_factor}")

        self.super_perspective_changed()
        self.redraw_perspective_info()

    def redraw_perspective_info(self) -> None:
        """
        Re-draws the perspective info text.
        """
        visible = self.gui.config.get_bool("show_perspective_info")

        self.visual_perspective_info.parent = self.view_text.scene if visible else None

        if visible:
            # Calculate linearized zoom value from VisPy "scale factor"
            zoom_log_range = np.log10(self.ScaleFactorMax) - np.log10(self.ScaleFactorMin)
            zoom_log_shift = np.log10(self.view_main.camera.scale_factor) - np.log10(self.ScaleFactorMin)
            zoom = 1000 * (1 - zoom_log_shift / zoom_log_range)

            self.visual_perspective_info.text = \
                f"Azimuth: {self.view_main.camera.azimuth:+4.0f} °   " + \
                f"Elevation: {self.view_main.camera.elevation:+3.0f} °   " + \
                f"Zoom: {zoom:4.0f}"

    def redraw(self) -> None:
        """
        Re-draws the entire scene.
        """
        Debug(self, ".redraw()")

        self.redraw_start_time = time.monotonic()

        self.update_color_scheme()

        if self.gui.model.is_valid():
            self.initializing = False
        self.visual_startup_info.parent = self.view_text if self.initializing else None

        self.set_visible(self.visual_coordinate_system, self.gui.config.get_bool("show_coordinate_system"))
        self.redraw_perspective_info()

        # Enable to see which model state is being drawn; may be used for debugging.
        # print(self.gui.model)

        self.redraw_wire_segments()
        self.redraw_wire_points_sliced()
        self.redraw_wire_points_selected()

        # Determine which field colors to use (if at all)
        if self.gui.model.metric.is_valid():
            # Use metric colors
            boost = self.gui.config.get_float("field_boost")
            direction = 1 if self.gui.config.get_bool("dark_background") else -1
            colors = Metric.boost_colors(boost, direction, self.gui.model.metric.get_colors().copy())
        else:
            if self.gui.model.sampling_volume.is_valid():
                # Use foreground color for all arrows and points
                colors = [self.foreground] * self.gui.model.sampling_volume.get_points_count()
            else:
                # Dummy argument (not accessed by redraw_field_arrows/_points/_labels in this case)
                colors = None

        self.redraw_field_arrows(colors)
        self.redraw_field_points(colors)
        self.redraw_field_labels(colors)

        redraw_time = time.monotonic() - self.redraw_start_time
        Debug(self, f".redraw(): Finished (took {redraw_time:.2f} s)", success=True)

    # ------------------------------------------------------------------------------------------------------------------

    def redraw_wire_segments(self) -> None:
        """
        Re-draws wire segments.
        """
        visible = self.gui.model.wire.is_valid() and self.gui.config.get_bool("show_wire_segments")

        self.set_visible(self.visual_wire_segments, visible)

        if visible:
            if self.DebugVisuals:
                Debug(self, ".redraw_wire_segments(): pos[{len(self.gui.model.wire.get_points_sliced())}]")

            self.visual_wire_segments.set_data(
                pos=self.gui.model.wire.get_points_sliced(),
                connect="strip",
                color=self.foreground
            )

    def redraw_wire_points_sliced(self) -> None:
        """
        Re-draws sliced wire points.
        """
        visible = \
            self.gui.model.wire.is_valid() and \
            self.gui.config.get_bool("show_wire_points")

        self.set_visible(self.visual_wire_points_sliced, visible)

        if visible:
            if self.DebugVisuals:
                Debug(self, ".redraw_wire_points_sliced(): pos[{len(self.gui.model.wire.get_points_sliced())}]")

            self.visual_wire_points_sliced.set_data(
                pos=self.gui.model.wire.get_points_sliced(),
                face_color=self.foreground,
                size=VispyCanvas.WirePointSize,
                edge_width=0,
                edge_color=None,
                symbol="disc"
            )

    def redraw_wire_points_selected(self) -> None:
        """
        Re-draws selected wire base points.
        """
        point_index = self.gui.sidebar_left.wire_widget.table.get_selected_row()

        visible = \
            self.gui.model.wire.is_valid() and \
            self.gui.config.get_bool("show_wire_points") and \
            point_index is not None

        if visible:
            points_selected = np.array([
                self.gui.model.wire.get_points_transformed()[i]
                for i in range(
                    point_index,
                    len(self.gui.model.wire.get_points_transformed()) + point_index - 1,
                    len(self.gui.model.wire.get_points_base())
                )
            ])

            if self.DebugVisuals:
                Debug(self, ".redraw_wire_points_selected(): pos[{len(points_selected)}]")

            self.visual_wire_points_selected.set_data(
                pos=points_selected,
                face_color=VispyCanvas.WirePointSelectedColor,
                size=VispyCanvas.WirePointSelectedSize,
                edge_width=0,
                edge_color=None,
                symbol="disc"
            )

        self.set_visible(self.visual_wire_points_selected, visible)

    # ------------------------------------------------------------------------------------------------------------------

    def redraw_field_arrows(self, colors: np.ndarray) -> None:
        """
        Re-draws field arrows.

        @param colors: Colors
        """
        sampling_volume_resolution = self.gui.model.sampling_volume.get_resolution()
        arrow_head_scale = VispyCanvas.FieldArrowHeadSize * self.gui.config.get_float("field_arrow_head_scale")
        arrow_line_scale = 2 * (1 / sampling_volume_resolution) * self.gui.config.get_float("field_arrow_line_scale")

        visible = \
            self.gui.model.field.is_valid() and \
            (arrow_head_scale > 0 or arrow_line_scale > 0) and \
            self.gui.sidebar_left.wire_widget.table.get_selected_row() is None

        if visible:

            line_pairs = np.zeros([2 * self.gui.model.sampling_volume.get_points_count(), 3])
            head_points = np.zeros([self.gui.model.sampling_volume.get_points_count(), 3])

            line_pairs, head_points = Field.get_arrows(
                self.gui.model.sampling_volume.get_points(),
                self.gui.model.field.get_vectors(),
                line_pairs,
                head_points,
                arrow_line_scale,
                VispyCanvas.MagnitudeLimit
            )

            if self.DebugVisuals:
                Debug(self, ".redraw_field_arrows(): arrow lines: pos[{len(line_pairs)}] color[{len(colors)}]")

            self.visual_field_arrow_lines.set_data(
                pos=line_pairs,
                connect="segments",
                color=np.repeat(colors, 2, axis=0)
            )

            if self.DebugVisuals:
                Debug(self, ".redraw_field_arrows(): arrow heads: pos[{len(head_points)}] face_color[{len(colors)}]")

            self.visual_field_arrow_heads.set_data(
                pos=head_points,
                face_color=colors,
                size=arrow_head_scale,
                edge_width=0,
                edge_color=None,
                symbol="diamond"
            )

        self.set_visible(self.visual_field_arrow_lines, visible)
        self.set_visible(self.visual_field_arrow_heads, visible)

    def redraw_field_points(self, colors: np.ndarray) -> None:
        """
        Re-draws field points.

        @param colors: Colors
        """
        point_scale = VispyCanvas.FieldPointSize * self.gui.config.get_float("field_point_scale")

        visible = \
            self.gui.model.sampling_volume.is_valid() and \
            point_scale > 0 and \
            self.gui.sidebar_left.wire_widget.table.get_selected_row() is None

        if visible:
            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_field_points(): "
                    "pos[{self.gui.model.sampling_volume.get_points_count()}] face_color[{len(colors)}]"
                )

            self.visual_field_points.set_data(
                pos=self.gui.model.sampling_volume.get_points(),
                face_color=colors,
                size=point_scale,
                edge_width=0,
                edge_color=None,
                symbol="disc"
            )

        self.set_visible(self.visual_field_points, visible)

    # ------------------------------------------------------------------------------------------------------------------

    def create_field_labels(self) -> None:
        """
        Creates field labels.
        """
        n = len(self.gui.model.sampling_volume.get_labeled_indices())

        if self.DebugVisuals:
            Debug(self, f".create_field_labels(): Creating {n} labels …")

        show_gauss = self.gui.config.get_bool("show_gauss")
        field_units, field_factor = self.gui.model.field.get_units(show_gauss=show_gauss)

        # Iterate through the labeled sampling volume points
        for i in range(n):

            sampling_volume_point, field_vector_index = self.gui.model.sampling_volume.get_labeled_indices()[i]
            magnitude = np.linalg.norm(self.gui.model.field.get_vectors()[field_vector_index])
            if np.isnan(magnitude):
                text = "NaN"
            else:
                text = si_format(
                    magnitude * field_factor,
                    precision=VispyCanvas.MagnitudePrecision,
                    exp_format_str="{value}e{expof10} "
                ) + field_units

            visual = scene.visuals.create_visual_node(visuals.TextVisual)(
                parent=None,
                pos=sampling_volume_point,
                face=self.DefaultFontFace,
                font_size=self.DefaultFontSize,
                color=self.foreground,
                text=text,
                font_manager=self.font_manager
            )

            self.visual_field_labels.append(visual)

        if self.DebugVisuals:
            Debug(self, f".create_field_labels(): Created {n} labels")

    def delete_field_labels(self) -> None:
        """
        Deletes the field labels.
        """
        for visual in self.visual_field_labels:
            visual.parent = None

        if self.DebugVisuals:
            Debug(self, f".delete_field_labels(): Deleted {len(self.visual_field_labels)}")

        self.visual_field_labels = []

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def redraw_field_labels(self, colors) -> None:
        """
        Re-draws field labels.

        @param colors: Colors
        """
        visible = \
            self.gui.model.metric.is_valid() and \
            self.gui.config.get_bool("display_field_magnitude_labels") and \
            self.gui.sidebar_left.wire_widget.table.get_selected_row() is None

        if visible:

            # Create field labels if necessary
            # noinspection PySimplifyBooleanCheck
            if self.visual_field_labels == []:
                self.create_field_labels()

            if self.DebugVisuals:
                Debug(self, f".redraw_field_labels(): Coloring {len(self.visual_field_labels)}")

            # Update label colors
            for i in range(len(self.visual_field_labels)):

                if self.gui.config.get_bool("show_colored_labels"):
                    # Use metric color at labeled sampling volume point
                    _, field_vector_index = self.gui.model.sampling_volume.get_labeled_indices()[i]
                    self.visual_field_labels[i].color = np.append(colors[field_vector_index][:3], 1.0)
                else:
                    # Use foreground color for all labels
                    self.visual_field_labels[i].color = self.foreground

        for visual in self.visual_field_labels:
            visual.parent = self.view_main.scene if visible else None

    # ------------------------------------------------------------------------------------------------------------------

    def save_image(self, filename: str) -> None:
        """
        Saves the currently displayed scene to PNG file.

        @param filename: Filename
        """
        Debug(self, f".save_image({filename})")

        io.write_png(filename, self.render())
