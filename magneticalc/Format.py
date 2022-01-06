""" Format module. """

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

from typing import List, Union
import os
import numpy as np


class Format:
    """ Format class. """

    """ Float precision. """
    FloatPrecision = 4

    """ Coordinate precision. """
    CoordinatePrecision = 6

    @staticmethod
    def absolute_filename(filename: str) -> str:
        """
        Converts a filename to an absolute filename.

        @param filename: Filename
        @return: Absolute filename
        """
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)

    @staticmethod
    def filename_uri(filename: str) -> str:
        """
        Converts a filename to a filename URI.

        @param filename: Filename
        @return: Filename URI
        """
        return "file://" + filename.replace(" ", "%20")

    @staticmethod
    def float_to_str(value: float) -> str:
        """
        Converts a float value to string.
        """
        return f"{float(value):.{Format.FloatPrecision}f}"

    @staticmethod
    def point_to_str(point: Union[np.ndarray, List[float]]) -> str:
        """
        Converts a single 3D point to string.

        @param point: Single 3D point
        @return: String
        """
        return ", ".join([f"{component:+0.0{Format.CoordinatePrecision}f}" for component in point])

    @staticmethod
    def points_to_str(points: Union[np.ndarray, List[List[float]]]) -> str:
        """
        Converts list of 3D points to string.

        @param points: List of 3D points
        @return: String
        """
        return "; ".join([Format.point_to_str(point) for point in points])

    @staticmethod
    def str_to_point(str_point: str) -> Union[np.ndarray, List[float]]:
        """
        Converts string to single 3D point.

        @param str_point: String
        @return: Single 3D point
        """
        return [float(coord) for coord in str_point.split(",")]

    @staticmethod
    def str_to_points(str_points: str) -> Union[np.ndarray, List[List[float]]]:
        """
        Converts string to list of 3D points.

        @param str_points: String
        @return: List of 3D points
        """
        return [
            Format.str_to_point(str_point) for str_point in str_points.split(";")
            if str_point != ""  # Ignoring stray semicolon at the end of the line
        ]
