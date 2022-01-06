#!/usr/bin/env python3.8

# Change to "../"
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

#-----------------------------------------------------------------------------------------------------------------------

wire_filename = "../examples/My Wire.txt"

from magneticalc import API
import numpy as np

wire = [
    (np.cos(a), np.sin(a), np.sin(16 * a) / 5)
    for a in np.linspace(0, 2 * np.pi, 200)
]
API.export_wire(wire_filename, wire)

wire2 = API.import_wire(wire_filename)
assert np.array_equal(wire, wire2)

#-----------------------------------------------------------------------------------------------------------------------

export_filename = "../examples/My Export.hdf5"

from magneticalc import API
import matplotlib.pyplot as plt

data = API.import_hdf5(export_filename)
axes = data.get_axes()
a_field = data.get_a_field()

ax = plt.figure(figsize=(5, 5), dpi=150).add_subplot(projection="3d")
ax.quiver(*axes, *a_field, length=1e5, normalize=False, linewidth=.5)
plt.show()

print(".get_wire():", len(data.get_wire()))
print(".get_wire_list():", len(data.get_wire_list()))
print(".get_current():", data.get_current())
print(".get_dimension():", data.get_dimension())
print(".get_axes(reduce=True):", len(data.get_axes(reduce=True)))
print(".get_axes_list():", len(data.get_axes_list()))
print(".get_a_field_list():", len(data.get_a_field_list()))
print(".get_a_field(as_3d=True):", len(data.get_a_field(as_3d=True)))
