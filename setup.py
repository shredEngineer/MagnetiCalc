""" MagnetiCalc setup script. """

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

from setuptools import setup

version = {}
with open("magneticalc/Version.py") as file:
    exec(file.read(), version)

setup(
    packages=["magneticalc"],
    package_dir={"magneticalc": "magneticalc"},
    name="MagnetiCalc",
    version=version["__VERSION__"],
    description="""MagnetiCalc calculates the magnetic field of arbitrary coils in vacuum, examples included.
Inside a VisPy/OpenGL-accelerated PyQt5 GUI, the static magnetic flux density (B-field due to DC currents) is displayed
in interactive 3D, using multiple metrics for highlighting this field's properties.
Alternatively, the magnetic vector potential (A-field) may be displayed.
All parameters and presets can interactively be changed inside the GUI.
There is also an experimental feature to calculate the coil's energy and self-inductance.""",
    url="https://github.com/shredEngineer/MagnetiCalc",
    author="Paul Wilhelm",
    author_email="anfrage@paulwilhelm.de",
    license="ISC License",
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Development Status :: 4 - Beta"
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms=["any"],
    python_requires=">=3.6",
    install_requires=[
        "PyQt5",
        "qtawesome>=1.0.0",
        "vispy>=0.6.5",
        "matplotlib",
        "numpy",
        "colorit>=0.1.0",
        "si-prefix>=1.2.2"
    ]
)
