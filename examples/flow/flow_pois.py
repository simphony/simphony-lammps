from __future__ import print_function
from simlammps.lammps_wrapper import LammpsWrapper


wrapper = LammpsWrapper()

# we *workaround* the fact that we cannot
# configure the wrapper/lammps yet by directly
# using the LAMMPS python interface.

# LAMMPS: 2-d LJ flow simulation

wrapper._lammps.command("dimension	2")
wrapper._lammps.command("boundary	p s p")

wrapper._lammps.command("atom_style	atomic")
wrapper._lammps.command("neighbor	0.3 bin")
wrapper._lammps.command("neigh_modify	delay 5")

# LAMMPS: create geometry

wrapper._lammps.command("lattice		hex 0.7")
wrapper._lammps.command("region		box block 0 20 0 10 -0.25 0.25")
wrapper._lammps.command("create_box	3 box")
wrapper._lammps.command("create_atoms	1 box")

wrapper._lammps.command("mass		1 1.0")
wrapper._lammps.command("mass		2 1.0")
wrapper._lammps.command("mass		3 1.0")

# LAMMPS: LJ potentials

wrapper._lammps.command("pair_style	lj/cut 1.12246")
wrapper._lammps.command("pair_coeff	* * 1.0 1.0 1.12246")

# LAMMPS: define groups

wrapper._lammps.command("region	     1 block INF INF INF 1.25 INF INF")
wrapper._lammps.command("group	     lower region 1")
wrapper._lammps.command("region	     2 block INF INF 8.75 INF INF INF")
wrapper._lammps.command("group	     upper region 2")
wrapper._lammps.command("group	     boundary union lower upper")
wrapper._lammps.command("group	     flow subtract all boundary")

wrapper._lammps.command("set	     group lower type 2")
wrapper._lammps.command("set	     group upper type 3")

# LAMMPS: initial velocities

# (compute thermodynamic information. see thermo )
wrapper._lammps.command("compute	     mobile flow temp")
wrapper._lammps.command("velocity     flow create 1.0 482748 temp mobile")
wrapper._lammps.command("fix	     1 all nve")
wrapper._lammps.command("fix	     2 flow temp/rescale 200 1.0 1.0 0.02 1.0")
wrapper._lammps.command("fix_modify   2 temp mobile")

# LAMMPS: Poiseuille flow

wrapper._lammps.command("velocity     boundary set 0.0 0.0 0.0")
wrapper._lammps.command("fix	     3 lower setforce 0.0 0.0 0.0")
wrapper._lammps.command("fix	     4 upper setforce 0.0 NULL 0.0")
wrapper._lammps.command("fix	     5 upper aveforce 0.0 -1.0 0.0")
wrapper._lammps.command("fix	     6 flow addforce 0.5 0.0 0.0")
wrapper._lammps.command("fix	     7 all enforce2d")

# LAMMPS: Run

wrapper._lammps.command("timestep	0.003")

# (output the thermodynamic information.  See early compute)
wrapper._lammps.command("thermo		500")
wrapper._lammps.command("thermo_modify	temp mobile")

wrapper._lammps.command("dump            1 all atom 500 dump.*.flow")
wrapper._lammps.command("run 10000")
