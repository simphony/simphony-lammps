INTERFACE
=========

The SimPhoNy LAMMPS engine (see :class:`LammpsWrapper`) can be configured to interface with LAMMPS in two separate ways:

* FILE-IO - use file and file output operations to run LAMMPS engine
* INTERNAL - uses the internal interface of LAMMPS to run LAMMPS engine

It should not matter whether the user is using a File-IO or the INTERNAL as the API is the same for the
SimPhoNy user.  The user will only see a performance difference between the two interfaces to LAMMPS.


::

   from simphony.engine import lammps
       wrapper = lammps.LammpsWrapper(interface=InterfaceType.FILEIO)


::

    from simphony.engine import lammps
       wrapper = lammps.LammpsWrapper(interface=InterfaceType.INTERNAL)