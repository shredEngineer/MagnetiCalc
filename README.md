
MagnetiCalc
===========

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TN6YTPVX36YHA&source=url)
[![API Documentation](https://img.shields.io/badge/Documentation-API-orange)](https://shredengineer.github.io/MagnetiCalc/)
[![PyPI version](https://img.shields.io/pypi/v/MagnetiCalc?label=PyPI)](https://pypi.org/project/MagnetiCalc/)

**What does MagnetiCalc do?**

MagnetiCalc calculates the static magnetic flux density, vector potential, energy, self-inductance
and magnetic dipole moment of arbitrary coils. Inside a [VisPy](https://github.com/vispy/vispy) / OpenGL-accelerated
PyQt5 GUI, the magnetic flux density
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}" alt="B">-field,
in units of <i>Tesla</i>)
or the magnetic vector potential
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}" alt="A">-field,
in units of <i>Tesla-meter</i>)
is displayed in interactive 3D, using multiple metrics for highlighting the field properties.

<i>Experimental feature:</i> To calculate the energy and self-inductance of permeable (i.e. ferromagnetic) materials,
different core media can be modeled as regions of variable relative permeability;
however, core saturation is currently not modeled, leading to excessive flux density values.
 
**Who needs MagnetiCalc?**

MagnetiCalc does its job for hobbyists, students, engineers and researchers of magnetic phenomena.
I designed MagnetiCalc from scratch, because I didn't want to mess around
with expensive and/or overly complex simulation software
whenever I needed to solve a magnetostatic problem.

**How does it work?**

The <img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}" alt="B">-field calculation
is implemented using the Biot-Savart law [1], employing multiprocessing techniques;
MagnetiCalc uses just-in-time compilation ([JIT](https://numba.pydata.org/))
and, if available, GPU-acceleration ([CUDA](https://numba.pydata.org/numba-doc/dev/cuda/overview.html))
to achieve high-performance calculations.
Additionally, the use of easily constrainable "sampling volumes" allows for selective calculation over
grids of arbitrary shape and arbitrary relative permeabilities
<img src="https://render.githubusercontent.com/render/math?math=\mu_r(\mathbf{x})" alt="µ_r(x)"> (<i>experimental</i>).

The shape of any wire is modeled as a 3D piecewise linear curve.
Arbitrary loops of wire are sliced into differential current elements
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{\ell}" alt="l">),
each of which contributes to the total resulting field
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}" alt="A">,
<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}" alt="B">)
at some fixed 3D grid point (<img src="https://render.githubusercontent.com/render/math?math=\mathbf{x}" alt="x">),
summing over the positions of all current elements
(<img src="https://render.githubusercontent.com/render/math?math=\mathbf{x^'}" alt="x'">):

<img src="https://render.githubusercontent.com/render/math?math=\mathbf{A}(\mathbf{x})=I \cdot \frac{\mu_0}{4 \pi} \cdot \displaystyle \sum_\mathbf{x^'} \mu_r(\mathbf{x}) \cdot \frac{\mathbf{\ell}(\mathbf{x^')}}{\mid \mathbf{x} - \mathbf{x^'} \mid}"><br>

<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}(\mathbf{x})=I \cdot \frac{\mu_0}{4 \pi} \cdot \displaystyle \sum_\mathbf{x^'} \mu_r(\mathbf{x}) \cdot \frac{\mathbf{\ell}(\mathbf{x^'}) \times (\mathbf{x} - \mathbf{x^'})}{\mid \mathbf{x} - \mathbf{x^'} \mid}"><br>

At each grid point, the field magnitude (or field angle in some plane) is displayed using colored arrows and/or dots;
field color and alpha transparency are individually mapped using one of the various
[available metrics](#appendix-metrics).

The coil's energy <img src="https://render.githubusercontent.com/render/math?math=E" alt="E"> [2]
and self-inductance <img src="https://render.githubusercontent.com/render/math?math=L" alt="L"> [3]
are calculated by summing the squared
<img src="https://render.githubusercontent.com/render/math?math=\mathbf{B}" alt="B">-field
over the entire sampling volume;
ensure that the sampling volume encloses a large, non-singular portion of the field:

<img src="https://render.githubusercontent.com/render/math?math=E=\frac{1}{\mu_0} \cdot \displaystyle \sum_\mathbf{x} \frac{\mathbf{B}(\mathbf{x}) \cdot \mathbf{B}(\mathbf{x})}{\mu_r(\mathbf{x})}"><br>

<img src="https://render.githubusercontent.com/render/math?math=L=\frac{1}{\I^2} \cdot E"><br>

Additionally, the scalar magnetic dipole moment
<img src="https://render.githubusercontent.com/render/math?math=m" alt="m"> [4]
is calculated by summing over all current elements:

<img src="https://render.githubusercontent.com/render/math?math=m=\Bigl| I \cdot \frac{1}{2} \cdot \displaystyle \sum_\mathbf{x^'} \mathbf{x^'} \times \mathbf{\ell}(\mathbf{x^'}) \Bigr|"><br>

***References***

[1]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 204, (5.4).<br>
[2]: Kraus, Electromagnetics, 4th Edition, p. 269, 6-9-1.<br>
[3]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 252, (5.157).<br>
[4]: Jackson, Klassische Elektrodynamik, 5. Auflage, S. 216, (5.54).


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

Install (or upgrade) MagnetiCalc to the user site-packages directory and start it from there: 
```shell
python3 -m pip install magneticalc --upgrade
python3 -m magneticalc
```

This will automatically install all dependency packages.

**Note:** From within a *Jupyter Notebook*, MagnetiCalc must be installed and run like this:
```python
import sys
!{sys.executable} -m pip install magneticalc --upgrade
!{sys.executable} -m magneticalc
```

### Option B: Manual download
First, manually install all dependency packages (upgrading each to the latest version):
```shell
python3 -m pip install numpy numba PyQt5 vispy qtawesome colorit si-prefix --upgrade
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

### Enabling CUDA Support

Tested in Ubuntu 20.04, using the NVIDIA CUDA 10.1 driver and NVIDIA GeForce GTX 1650 GPU.

Please refer to the
[Numba Installation Guide](https://numba.pydata.org/numba-doc/latest/user/installing.html)
which includes the steps necessary to get CUDA up and running.

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

Contribute
----------
You are invited to contribute to MagnetiCalc in any way you like! :)

If this software has been helpful to you in some way or another, please let me and others know!

ToDo
----
* Add installation instructions for Windows, ensure consistent PyQt5 look and feel.
* Add support for modeling of core material saturation and hysteresis effects.
* Add support for selective display over a portion of the metric range, in order to get a kind of iso-contour display.
* Add support for multiple wires, study mutual induction.

Video
-----
A very short demo of MagnetiCalc in action:

[![Magnetic Field Calculation with Python (MagnetiCalc)](https://raw.githubusercontent.com/shredEngineer/MagnetiCalc/master/docs/Video-Thumb.png)](https://www.youtube.com/watch?v=d3QKdYfOuvQ)

Links
-----
If you want to comment on the project or see additional info, please visit my personal website:
https://paulwilhelm.de/magneticalc/

*Appendix:* Metrics
-------------------

| Metric               | Symbol                                                                                                 | Description                           |
|----------------------|--------------------------------------------------------------------------------------------------------|---------------------------------------|
| ``Magnitude``        | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}\mid">                      | Magnitude in space                    |
| ``Magnitude X``      | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{X}\mid">                  | Magnitude in X-direction              |
| ``Magnitude Y``      | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{Y}\mid">                  | Magnitude in Y-direction              |
| ``Magnitude Z``      | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{Z}\mid">                  | Magnitude in Z-direction              |
| ``Magnitude XY``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{XY}\mid">                 | Magnitude in XY-plane                 |
| ``Magnitude XZ``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{XZ}\mid">                 | Magnitude in XZ-plane                 |
| ``Magnitude YZ``     | <img src="https://render.githubusercontent.com/render/math?math=\mid\vec{B}_{YZ}\mid">                 | Magnitude in YZ-plane                 |
| ``Divergence``       | <img src="https://render.githubusercontent.com/render/math?math=\nabla\cdot\vec{B}">                   | Divergence                            |
| ``Divergence +``     | <img src="https://render.githubusercontent.com/render/math?math=%2b\{\nabla\cdot\vec{B}\}_{>0}">       | Positive Divergence                   |
| ``Divergence –``     | <img src="https://render.githubusercontent.com/render/math?math=-\{\nabla\cdot\vec{B}\}_{<0}">         | Negative Divergence                   |
| ``Log Magnitude``    | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B}\mid">                   | Logarithmic Magnitude in space        |
| ``Log Magnitude X``  | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_X}\mid">                 | Logarithmic Magnitude in X-direction  |
| ``Log Magnitude Y``  | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_Y}\mid">                 | Logarithmic Magnitude in Y-direction  |
| ``Log Magnitude Z``  | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B_Z}\mid">                 | Logarithmic Magnitude in Z-direction  |
| ``Log Magnitude XY`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B}_{XY}\mid">              | Logarithmic Magnitude in XY-plane     |
| ``Log Magnitude XZ`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B}_{XZ}\mid">              | Logarithmic Magnitude in XZ-plane     |
| ``Log Magnitude YZ`` | <img src="https://render.githubusercontent.com/render/math?math=ln \mid\vec{B}_{YZ}\mid">              | Logarithmic Magnitude in YZ-plane     |
| ``Log Divergence``   | <img src="https://render.githubusercontent.com/render/math?math=ln \ \ \nabla\cdot\vec{B}">            | Logarithmic Divergence                |
| ``Log Divergence +`` | <img src="https://render.githubusercontent.com/render/math?math=ln \ %2b\{\nabla\cdot\vec{B}\}_{>0}">  | Positive Logarithmic Divergence       |
| ``Log Divergence –`` | <img src="https://render.githubusercontent.com/render/math?math=ln \ -\{\nabla\cdot\vec{B}\}_{<0}">    | Negative Logarithmic Divergence       |
| ``Angle XY``         | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B}_{XY}">           | Field angle in XY-plane               |
| ``Angle XZ``         | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B}_{XZ}">           | Field angle in XZ-plane               |
| ``Angle YZ``         | <img src="https://render.githubusercontent.com/render/math?math=\measuredangle\vec{B}_{YZ}">           | Field angle in YZ-plane               |
