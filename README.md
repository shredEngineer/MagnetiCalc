
MagnetiCalc
===========

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TN6YTPVX36YHA&source=url)
[![API Documentation](https://img.shields.io/badge/Documentation-API-orange)](https://shredengineer.github.io/MagnetiCalc/)
[![PyPI version](https://img.shields.io/pypi/v/MagnetiCalc?label=PyPI)](https://pypi.org/project/MagnetiCalc/)

**What does MagnetiCalc do?**

MagnetiCalc calculates the magnetic field of arbitrary air coils, examples included.
Inside a VisPy/OpenGL-accelerated PyQt5 GUI, the static magnetic flux density (B-field due to DC currents) is displayed
in interactive 3D, using multiple metrics for highlighting this field's properties.
All parameters and presets can interactively be changed inside the GUI.

**Who needs MagnetiCalc?**

MagnetiCalc does its job for hobbyists, students, engineers and researchers of magnetic phenomena.
I designed MagnetiCalc from scratch, because I didn't want to mess around
with expensive and/or overly complex simulation software
whenever I needed to solve a magnetostatic problem.

**How does it work?**

The field calculation is implemented using the Biot-Savart law [1], employing multiprocessing techniques.
The use of easily constrainable "sampling volumes" allows for selective calculation over
arbitrary shapes.

The shape of any wire is modeled as a 3D piecewise linear curve.
Arbitrary loops of wire are sliced into differential current elements,
each of which contributes to the total magnetic flux density
<img src="https://render.githubusercontent.com/render/math?math=\vec{B}">
at some fixed 3D grid point.

At each grid point, the field is displayed using colored arrows and/or dots;
field color and alpha transparency are individually mapped using one of the various available metrics.

[1]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 204, (5.4).

Screenshot
----------

![Screenshot](https://raw.githubusercontent.com/shredEngineer/MagnetiCalc/master/docs/Screenshot.png)

(Screenshot taken from the latest GitHub release.)

Installation
------------
Tested with Python 3.8 in Ubuntu 20.04.

### Prerequisites

The following dependency packages have to be installed first (Ubuntu 20.04):
```shell
sudo apt install python3-dev
sudo apt install libxcb-xinerama0 --reinstall
```

### Option A: Automatic install via pip
**Note:** On some systems, it may be necessary to upgrade pip first:
```shell
python3 -m pip install pip --upgrade
```

Install MagnetiCalc to the user site-packages directory and start it from there: 
```shell
pip3 install magneticalc
python3 -m magneticalc
```

This will automatically install all dependency packages.

### Option B: Manual download
First, manually install all dependency packages (upgrading each to the latest version):
```shell
pip3 install PyQt5 qtawesome vispy matplotlib numpy colorit si-prefix --upgrade
```

Clone the latest version of MagnetiCalc from GitHub and start it directly: 
```shell
git clone https://github.com/shredEngineer/MagnetiCalc
cd MagnetiCalc
python3 -m magneticalc
```

For debugging, you may now also install (uninstall) the package in a virtual environment:
```shell
pip install .
…
pip uninstall magneticalc -y
``` 

ToDo
----
* Improve Windows support; add installation instructions, ensure consistent PyQt5 look and feel.
* Add support for adding, editing and removing sampling volume constraints;
  the SamplingVolume module already supports constraints, but the GUI currently doesn't.
  This will also require changes to the way the field labels are currently distributed (relying on a *complete* grid).
* Add support for selective display over a portion of the metric range, in order to get a kind of iso-contour display. 
* Add support for calculation of compensation factor, i.e. the ratio of total vector sum to metric limits.
* Add support for calculation of self-inductance;
  a loop detector creates polygons over which the B-field is integrated,
  yielding the loop magnetic flux <img src="https://render.githubusercontent.com/render/math?math=\Phi=L\cdot I">.
* Add support for different media with arbitrary geometry and permeability.
* Add support for multiple wires, study mutual induction.
* Add support for vector potential (A-field) and electric E-field calculation.
* Move the field and metric calculations directly to the OpenGL shader engines,
  thus most likely drastically shortening overall computation time.

Contribute
----------
You are invited to contribute to MagnetiCalc in any way you like! :)

If this software has been helpful to you in some way or another, please let me and others know!

License
-------
Copyright © 2020, Paul Wilhelm, M. Sc. <[anfrage@paulwilhelm.de](mailto:anfrage@paulwilhelm.de)>

<b>ISC License</b>

Permission to use, copy, modify, and/or distribute this software for any<br>
purpose with or without fee is hereby granted, provided that the above<br>
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES<br>
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF<br>
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR<br>
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES<br>
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN<br>
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF<br>
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Video Demo
----------
Here is a very short demo of an earlier version of MagnetiCalc in action:

[![Magnetic Field Calculation with Python (MagnetiCalc)](https://raw.githubusercontent.com/shredEngineer/MagnetiCalc/master/docs/Video-Thumb.png)](https://www.youtube.com/watch?v=rsVbu5uF0eU)
