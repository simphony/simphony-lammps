Converting from existing LAMMPS input files
===========================================

The Simphony-LAMMPS library provides a set of tools to convert existing
lammps data files to SimPhoNy CUDS format. While these tools are not required when
using the LAMMPS SimPhoNy engine, they can be helpful in converting existing
LAMMPS data to SimPhoNy format.  See the following examples:


.. rubric:: Conversion from lammps data file to list CUDS ```Particles```

.. literalinclude:: ../../examples/file_conversion/convert.py

.. note::

  There needs to be an executable called "lammps" that can be found in
  the PATH for the example to work.