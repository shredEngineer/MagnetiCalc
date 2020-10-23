""" VispyCanvas module. """

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

import numpy as np
from vispy import io, scene, visuals
from vispy.scene.cameras import TurntableCamera
from magneticalc.Debug import Debug


class VispyCanvas(scene.SceneCanvas):
    """ VispyCanvas class. """

    # Font
    DefaultFont = "DejaVu Sans Mono"

    # Enable to additionally debug drawing of visuals
    DebugVisuals = False

    # Base colors
    White = np.array([1, 1, 1, 1])
    Black = np.array([0, 0, 0, 1])

    # Display settings
    ArrowHeadSize = 6
    WirePointSize = 4

    # Zoom limits
    ScaleFactorMin = 1e-2
    ScaleFactorMax = 1e+3

    # Preset: Isometric
    Isometric = {
        "id": "Isometric",
        "azimuth": 135,
        "elevation": np.arctan(1 / np.sqrt(2)) * 180 / np.pi
    }

    # Preset: XY-plane
    PlaneXY = {
        "id": "Plane XY",
        "azimuth": 0,
        "elevation": 90
    }

    # Preset: XZ-plane
    PlaneXZ = {
        "id": "Plane XZ",
        "azimuth": 0,
        "elevation": 0
    }

    # Preset: YZ-plane
    PlaneYZ = {
        "id": "Plane YZ",
        "azimuth": 90,
        "elevation": 0
    }

    Presets = [
        Isometric,
        PlaneXY,
        PlaneXZ,
        PlaneYZ
    ]

    def __init__(self, gui):
        """
        Initialize VisPy canvas.

        @param gui: GUI
        """
        scene.SceneCanvas.__init__(self)

        self.unfreeze()

        self.gui = gui

        self.view_main = self.central_widget.add_view()
        self.view_text = self.view_main.add_view()

        self.view_main.camera = TurntableCamera(
            fov=0,  # Use orthographic projection
            translate_speed=3
        )

        self.visual_coordinate_system = scene.visuals.create_visual_node(visuals.XYZAxisVisual)()

        self.visual_perspective_info = scene.visuals.create_visual_node(visuals.TextVisual)(
            parent=self.view_text.scene,
            pos=(10, 10),
            anchor_x="left",
            anchor_y="bottom",
            font_size=9,
            face=self.DefaultFont,
        )

        self.visual_wire_segments = scene.visuals.create_visual_node(visuals.LineVisual)()
        self.visual_wire_points_sliced = scene.visuals.create_visual_node(visuals.MarkersVisual)()
        self.visual_field_points = scene.visuals.create_visual_node(visuals.MarkersVisual)()
        self.visual_field_arrow_lines = scene.visuals.create_visual_node(visuals.LineVisual)()
        self.visual_field_arrow_heads = scene.visuals.create_visual_node(visuals.MarkersVisual)()

        self.foreground = None
        self.background = None
        self.update_color_scheme()

        # Initially load perspective from configuration
        self.load_perspective(redraw=False)

        # Insert perspective change handler
        self.super_perspective_changed = self.view_main.camera.view_changed
        self.view_main.camera.view_changed = self.on_perspective_changed

        self.freeze()

    def update_color_scheme(self):
        """
        Updates the color scheme.
        """
        self.foreground = self.White if self.gui.config.get_bool("dark_background") else self.Black
        self.background = self.Black if self.gui.config.get_bool("dark_background") else self.White
        self.bgcolor = self.background
        self.visual_perspective_info.color = np.append(self.foreground[:3], 0.6)

    def set_visible(self, visual, is_visible):
        """
        Sets some visual's visibility.

        @param visual: Visual
        @param is_visible: Visibility (boolean)
        """
        visual.parent = self.view_main.scene if is_visible else None

    def load_perspective(self, redraw=True):
        """
        Loads perspective from configuration.

        @param redraw: Enable to trigger final re-draw
        """
        self.view_main.camera.azimuth = self.gui.config.get_float("azimuth")
        self.view_main.camera.elevation = self.gui.config.get_float("elevation")
        self.view_main.camera.scale_factor = self.gui.config.get_float("scale_factor")

        if redraw:
            self.redraw()

    def on_perspective_changed(self):
        """
        Handles a change of perspective.
        """

        # Limit scale factor
        if self.view_main.camera.scale_factor > self.ScaleFactorMax:
            self.view_main.camera.scale_factor = self.ScaleFactorMax
        elif self.view_main.camera.scale_factor < self.ScaleFactorMin:
            self.view_main.camera.scale_factor = self.ScaleFactorMin

        self.super_perspective_changed()
        self.redraw_perspective_info()

    def redraw_perspective_info(self):
        """
        Re-draws the perspective info text.
        """
        visible = self.gui.config.get_bool("show_perspective_info")

        self.visual_perspective_info.parent = self.view_text.scene if visible else None

        if visible:
            zoom_log_range = np.log10(self.ScaleFactorMax) - np.log10(self.ScaleFactorMin)
            zoom_log_shift = np.log10(self.view_main.camera.scale_factor) - np.log10(self.ScaleFactorMin)
            zoom = 1000 * (1 - zoom_log_shift / zoom_log_range)

            self.visual_perspective_info.text = \
                f"Azimuth: {self.view_main.camera.azimuth:+4.0f} °   " + \
                f"Elevation: {self.view_main.camera.elevation:+3.0f} °   " + \
                f"Zoom: {zoom:4.0f}"

    def redraw(self):
        """
        Re-draws the entire scene.
        """
        Debug(self, ".redraw()", color=(0, 128, 0))

        self.update_color_scheme()

        self.set_visible(self.visual_coordinate_system, self.gui.config.get_bool("show_coordinate_system"))
        self.redraw_perspective_info()

        self.redraw_wire_segments()
        self.redraw_wire_points()

        # Determine which field colors to use (if at all)
        if self.gui.model.metric.is_valid():
            # Use metric colors
            colors = [self.boost_color(color) for color in self.gui.model.metric.get_colors()]
        else:
            if self.gui.model.sampling_volume.is_valid():
                # Use foreground color for all arrows and points
                colors = [self.foreground] * len(self.gui.model.sampling_volume.get_points())
            else:
                # Dummy argument (not accessed by redraw_field_arrows & redraw_field_points in this case)
                colors = None

        self.redraw_field_arrows(colors)
        self.redraw_field_points(colors)

    def redraw_wire_segments(self):
        """
        Re-draws wire segments.
        """
        visible = self.gui.model.wire.is_valid() and self.gui.config.get_bool("show_wire_segments")

        self.set_visible(self.visual_wire_segments, visible)

        if visible:
            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_wire_segments(): "
                    f"pos[{len(self.gui.model.wire.get_points_sliced())}]",
                    color=(255, 0, 255)
                )

            self.visual_wire_segments.set_data(
                pos=self.gui.model.wire.get_points_sliced(),
                connect="strip",
                color=self.foreground
            )

    def redraw_wire_points(self):
        """
        Re-draws wire points.
        """
        visible = \
            self.gui.model.wire.is_valid() and \
            self.gui.config.get_bool("show_wire_points")

        self.set_visible(self.visual_wire_points_sliced, visible)

        if visible:
            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_wire_points(): "
                    f"pos[{len(self.gui.model.wire.get_points_sliced())}]",
                    color=(255, 0, 255)
                )

            self.visual_wire_points_sliced.set_data(
                pos=self.gui.model.wire.get_points_sliced(),
                face_color=self.foreground,
                size=VispyCanvas.WirePointSize,
                edge_width=0,
                edge_color=None,
                symbol="disc"
            )

    def redraw_field_arrows(self, colors):
        """
        Re-draws field arrows.

        @param colors: Colors
        """
        arrow_scale = self.gui.config.get_float("field_arrow_scale")

        visible = \
            self.gui.model.sampling_volume.is_valid() and \
            self.gui.model.field.is_valid() and \
            arrow_scale > 0

        self.set_visible(self.visual_field_arrow_lines, visible)
        self.set_visible(self.visual_field_arrow_heads, visible)

        if visible:

            line_pairs = np.zeros([2 * len(self.gui.model.sampling_volume.get_points()), 3])
            head_points = np.zeros([len(self.gui.model.sampling_volume.get_points()), 3])

            for i in range(len(self.gui.model.sampling_volume.get_points())):

                # Calculate normalized field direction
                field_vector_length = max(1e-12, np.linalg.norm(self.gui.model.field.get_vectors()[i]))
                field_direction_norm = self.gui.model.field.get_vectors()[i] / field_vector_length

                # Calculate arrow start & end coordinates
                p_start = self.gui.model.sampling_volume.get_points()[i] + field_direction_norm / 2 / 2 * arrow_scale
                p_end = self.gui.model.sampling_volume.get_points()[i] - field_direction_norm / 2 / 2 * arrow_scale

                # Populate arrow line & head coordinates
                line_pairs[2 * i + 0] = p_start
                line_pairs[2 * i + 1] = p_end
                head_points[i] = p_end

            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_field_arrows(): arrow lines: "
                    f"pos[{len(line_pairs)}] "
                    f"color[{len(colors)}]",
                    color=(255, 0, 255))

            self.visual_field_arrow_lines.set_data(
                pos=line_pairs,
                connect="segments",
                color=np.repeat(colors, 2, axis=0)
            )

            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_field_arrows(): arrow heads: "
                    f"pos[{len(head_points)}] "
                    f"face_color[{len(colors)}]",
                    color=(255, 0, 255)
                )

            self.visual_field_arrow_heads.set_data(
                pos=head_points,
                face_color=colors,
                size=VispyCanvas.ArrowHeadSize,
                edge_width=0,
                edge_color=None,
                symbol="diamond"
            )

    def redraw_field_points(self, colors):
        """
        Re-draws field points.
        
        @param colors: Colors
        """
        point_scale = self.gui.config.get_float("field_point_scale")

        visible = \
            self.gui.model.sampling_volume.is_valid() and \
            point_scale > 0

        self.set_visible(self.visual_field_points, visible)

        if visible:
            if self.DebugVisuals:
                Debug(
                    self,
                    ".redraw_field_points(): "
                    f"pos[{len(self.gui.model.sampling_volume.get_points())}] "
                    f"face_color[{len(colors)}]",
                    color=(255, 0, 255)
                )

            self.visual_field_points.set_data(
                pos=self.gui.model.sampling_volume.get_points(),
                face_color=colors,
                size=point_scale,
                edge_width=0,
                edge_color=None,
                symbol="disc"
            )

    def boost_color(self, color):
        """
        "Boosts" a color value.

        @param color: Color (4-tuple)
        @return: Color (4-tuple)
        """
        direction = 1 if self.gui.config.get_bool("dark_background") else -1
        boost = self.gui.config.get_float("field_boost")

        r = max(0, min(color[0] + direction * boost, 1))
        g = max(0, min(color[1] + direction * boost, 1))
        b = max(0, min(color[2] + direction * boost, 1))
        a = max(0, min(color[3] + boost, 1))

        return [r, g, b, a]

    def save_image(self, filename):
        """
        Saves the currently displayed scene to PNG file.

        @param filename: Filename
        """
        io.write_png(filename, self.render())
