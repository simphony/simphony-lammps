from __future__ import print_function
import subprocess

<<<<<<< HEAD
from simphony.core.cuds_item import CUDSItem
from simlammps import read_data_file
=======
from simphony.engine import lammps
from simphony.core.cuba import CUBA
>>>>>>> common-version
from simlammps.cuba_extension import CUBAExtension

lammps_script = """# example of creating lammps data file (to be then used by SimPhoNy"
dimension	2
atom_style	atomic

# create geometry
lattice		hex 0.7
region		box block 0 20 0 10 -0.25 0.25
create_box	3 box
create_atoms	1 box

mass		1 1.0
mass		2 1.0
mass		3 1.0

# LJ potentials
pair_style	lj/cut 1.12246
pair_coeff	* * 1.0 1.0 1.12246

# define groups
region	     1 block INF INF INF 1.25 INF INF
group	     lower region 1
region	     2 block INF INF 8.75 INF INF INF
group	     upper region 2
group	     boundary union lower upper
group	     flow subtract all boundary

set	     group lower type 2
set	     group upper type 3

# initial velocities
compute      mobile flow temp
velocity     flow create 1.0 482748 temp mobile
velocity     boundary set 0.0 0.0 0.0

# write atoms to a lammps data file
write_data example.data"""

with open("lammps_example_script", "w") as script_file:
    script_file.write(lammps_script)

subprocess.check_call("lammps < lammps_example_script", shell=True)


<<<<<<< HEAD
particles, state_data = read_data_file("example.data")
print("\n\nFinished converting files")
print("\nA Particles data-set was read from the file:")
print("    '{}' has {} particles".format(
    particles.name,
    particles.count_of(CUDSItem.PARTICLE)))
=======
for particles in particles_list:
    number_particles = sum(1 for _ in particles.iter(item_type=CUBA.PARTICLE))
>>>>>>> common-version

number_materials = sum(1 for _ in state_data.iter_materials())
print("\n{} materials were read from the file.\n".format(number_materials))

box_description = \
    ""\
    "The data-set has the following simulation box description:\n"\
    "    CUBAExtension.BOX_ORIGIN: {}\n" \
    "    CUBAExtension.BOX_VECTORS: {}"

print(box_description.format(
    particles.data_extension[CUBAExtension.BOX_ORIGIN],
    particles.data_extension[CUBAExtension.BOX_VECTORS]))
