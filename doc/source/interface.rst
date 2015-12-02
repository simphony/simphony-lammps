LAMMPS engine for SimPhoNy
==========================

The SimPhoNy engine for LAMMPS is available in the SimPhoNy through the engine plugin named ``lammps``

After installation, the user should be able to import the ``lammps`` engine plugin module::

  from simphony.engine import lammps
    engine = lammps.LammpsWrapper()



Interface to LAMMPS
--------------------

The SimPhoNy LAMMPS engine (see :class:`LammpsWrapper`) can be configured to
interface with LAMMPS in two separate ways:

* FILE-IO - input and output files are used to configure and run LAMMPS engine
* INTERNAL - the LAMMPS library interface is used to run LAMMPS and access the
  internal state.

Despite performance differences, it should not matter whether the user is
using the File-IO or the INTERNAL interface as the API is the same.

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

This engine-wrapper uses LAMMPS Molecular Dynamics Simulator. A recent stable
version (10 Aug 2015, tagged r13864) of LAMMPS is supported and has been
tested. See ``install_lammps.sh`` for an example installation instructions.
For general LAMMPS install information, see http://lammps.sandia.gov/index.html

The installation of LAMMPS differs depending on what interface is used:

- FILE-IO: There needs to be an executable called "lammps" that can be found in
  the PATH.
- INTERNAL:  The LAMMPS-provided Python wrapper to LAMMPS needs to be
  installed.Instructions on building LAMMPS as a shared library and installing
  the Python wrapper can be found on LAMMPS website
  (http://lammps.sandia.gov/doc/Section_python.html#py_3)

Limitations of the INTERNAL interface
-------------------------------------
The following are known limitations when using the INTERNAL interface to LAMMPS:
 - Currently an upper limit of particle types (CUBA.MATERIAL_TYPE) is set due to
   the fact that LAMMPS only allows the number of types be configured at start
   (and not changed later) (https://github.com/simphony/simphony-lammps-md/issues/66)
 - No notification is provided to the user when an internal error occurs in the
   LAMMPS shared library as the library calls `exit(1)` and the process
   immediately exists (without an exception or writing to standard
   output/error).  (https://github.com/simphony/simphony-lammps-md/issues/63)
