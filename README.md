
MagnetiCalc
===========

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TN6YTPVX36YHA&source=url)
[![API Documentation](https://img.shields.io/badge/Documentation-API-orange)](https://shredengineer.github.io/MagnetiCalc/)
[![PyPI version](https://img.shields.io/pypi/v/MagnetiCalc?label=PyPI)](https://pypi.org/project/MagnetiCalc/)

**What does MagnetiCalc do?**

MagnetiCalc calculates the magnetic field of arbitrary coils in vacuum, examples included.
Inside a VisPy/OpenGL-accelerated PyQt5 GUI, the static magnetic flux density
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}">-field due to DC currents,
in units of <i>Tesla</i>) is displayed
in interactive 3D, using multiple metrics for highlighting the field properties.
Alternatively, the magnetic vector potential
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}">-field, in units of <i>Tesla-meter</i>)
may be displayed.
All parameters and presets can interactively be changed inside the GUI.
There is also an experimental feature to calculate the coil's energy and self-inductance.

**Who needs MagnetiCalc?**

MagnetiCalc does its job for hobbyists, students, engineers and researchers of magnetic phenomena.
I designed MagnetiCalc from scratch, because I didn't want to mess around
with expensive and/or overly complex simulation software
whenever I needed to solve a magnetostatic problem.

**How does it work?**

The <img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}">-field calculation
is implemented using the Biot-Savart law [1], employing multiprocessing techniques.
The use of easily constrainable "sampling volumes" allows for selective calculation over
grids of arbitrary shape.

The shape of any wire is modeled as a 3D piecewise linear curve.
Arbitrary loops of wire are sliced into differential current elements
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{\ell}">),
each of which contributes to the total resulting field
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}">,
<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}">)
at some fixed 3D grid point (<img src="https://render.githubusercontent.com/render/math?math=\mathbf{x}">),
integrated over the positions of all current elements
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{x^'}">): 

<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}(\mathbf{x})=I \cdot \frac{\mu_0}{4 \pi} \cdot \displaystyle \int \frac{\mathbf{\ell}(\mathbf{x^')}}{|\mathbf{x} - \mathbf{x^'}|} \,d\mathbf{x^'}"><br>

<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}(\mathbf{x})=I \cdot \frac{\mu_0}{4 \pi} \cdot \displaystyle \int \frac{\mathbf{\ell}(\mathbf{x^'}) \times (\mathbf{x} - \mathbf{x^'})}{|\mathbf{x} - \mathbf{x^'}|} \,d\mathbf{x^'}"><br>

At each grid point, the field magnitude (or field angle in some plane) is displayed using colored arrows and/or dots;
field color and alpha transparency are individually mapped using one of the various available metrics:

| Metric               | Symbols                                                                                      | Description                         |
|----------------------|----------------------------------------------------------------------------------------------|-------------------------------------|
| ``Magnitude``        | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}\mid">            | Magnitude in space                  |
| ``Magnitude XY``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B_{XY}}\mid">       | Magnitude in XY-plane               |
| ``Magnitude XZ``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B_{XZ}}\mid">       | Magnitude in XZ-plane               |
| ``Magnitude YZ``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B_{YZ}}\mid">       | Magnitude in YZ-plane               |
| ``Log Magnitude``    | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B}\mid">         | Logarithmic Magnitude in space      |
| ``Log Magnitude XY`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_{XY}}\mid">    | Logarithmic Magnitude in XY-plane   |
| ``Log Magnitude XZ`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_{XZ}}\mid">    | Logarithmic Magnitude in XZ-plane   |
| ``Log Magnitude YZ`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_{YZ}}\mid">    | Logarithmic Magnitude in YZ-plane   |
| ``AngleXY``          | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B_{XY}}"> | Field angle in XY-plane             |
| ``AngleXZ``          | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B_{XZ}}"> | Field angle in XZ-plane             |
| ``AngleYZ``          | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B_{YZ}}"> | Field angle in YZ-plane             |

As an experimental feature,
the coil's energy <img src="https://render.githubusercontent.com/render/math?math=E"> [2]
and self-inductance <img src="https://render.githubusercontent.com/render/math?math=L"> [3]
are calculated by integrating the squared
<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}">-field over the entire sampling volume.
However, these values are currently not reliable, varying strongly with the other parameters;
essentially, the sampling volume must enclose a large, non-singular portion of the field.

<img src="https://render.githubusercontent.com/render/math?math=E=\frac{1}{\mu_0} \cdot \displaystyle \int \mathbf{B} \cdot \mathbf{B} \,d\mathbf{x^'}"><br>

<img src="https://render.githubusercontent.com/render/math?math=L=\frac{1}{\I^2} \cdot E"><br>

[1]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 204, (5.4).<br>
[2]: Kraus, Electromagnetics, 4th Edition, p. 269, 6-9-1.<br>
[3]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 252, (5.157).


Screenshot
----------

![Screenshot](https://raw.githubusercontent.com/shredEngineer/MagnetiCalc/master/docs/Screenshot.png)

(Screenshot taken from the latest GitHub release.)

Installation
------------
Tested with Python 3.8 in Ubuntu 20.04.

If you have trouble installing MagnetiCalc,
make sure to file an [issue](https://github.com/shredEngineer/MagnetiCalc/issues)
so I can help you get it up and running!

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
python3 -m pip install magneticalc
python3 -m magneticalc
```

This will automatically install all dependency packages.

**Note:** From inside a *Jupyter Notebook*, MagnetiCalc may be installed and run like this:
```python
import sys
!{sys.executable} -m pip install magneticalc
!{sys.executable} -m magneticalc
```

### Option B: Manual download
First, manually install all dependency packages (upgrading each to the latest version):
```shell
python3 -m pip install PyQt5 qtawesome vispy matplotlib numpy colorit si-prefix --upgrade
```

Clone the latest version of MagnetiCalc from GitHub and start it directly: 
```shell
git clone https://github.com/shredEngineer/MagnetiCalc
cd MagnetiCalc
python3 -m magneticalc
```

For debugging, you may now also install (uninstall) the package in a virtual environment:
```shell
python3 -m pip install .
…
python3 -m pip uninstall magneticalc -y
``` 

ToDo
----
* Improve the calculation of self-inductance; there seems to be a scaling error!
* Add support for saving/loading configuration to/from other filenames.
* Add installation instructions for Windows, ensure consistent PyQt5 look and feel.
* Add support for adding, editing and removing sampling volume constraints;
  the SamplingVolume module already supports constraints, but the GUI currently doesn't.
  This will also require changes to the way the field labels are currently distributed (relying on a *complete* grid).
* Add support for selective display over a portion of the metric range, in order to get a kind of iso-contour display. 
* Add support for different media with arbitrary geometry and permeability.
* Add support for multiple wires, study mutual induction.
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

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Video Demo
----------
Here is a very short demo of an earlier version of MagnetiCalc in action:

[![Magnetic Field Calculation with Python (MagnetiCalc)](https://raw.githubusercontent.com/shredEngineer/MagnetiCalc/master/docs/Video-Thumb.png)](https://www.youtube.com/watch?v=rsVbu5uF0eU)

Links
-----
If you want to comment on the project or see additional info, please visit my personal website:
https://paulwilhelm.de/magneticalc/