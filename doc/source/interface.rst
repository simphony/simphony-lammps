Interface to LAMMPS
===================

The SimPhoNy LAMMPS engine (see :class:`LammpsWrapper`) can be configured to interface with LAMMPS in two separate ways:

* FILE-IO - use file and file output operations to run LAMMPS engine
* INTERNAL - uses the internal interface of LAMMPS to run LAMMPS engine

Despite performance differences, it should not matter whether the user is using the File-IO or the INTERNAL interface as the API is the same.

::

   # wrapper defaults to FILE-IO
   from simphony.engine import lammps
       engine = lammps.LammpsWrapper()

::

   # or use INTERNAL wrapper
   from simphony.engine import lammps
       engine = lammps.LammpsWrapper(use_internal_interface=true)


Installation of LAMMPS
----------------------

.. include:: lammps_install_short.rst

The installation of LAMMPS differs depending on what interface is used:

- FILE-IO: There needs to be an executable called "lammps" that can be found in the PATH.
- INTERNAL:  The LAMMPS-provided Python wrapper to LAMMPS needs to be installed.  Instructions on building LAMMPS as a shared library and installing the Python wrapper can be found on LAMMPS website (http://lammps.sandia.gov/doc/Section_python.html#py_3)

