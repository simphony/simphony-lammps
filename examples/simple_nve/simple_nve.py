# Demonstration of the SimPhoNy Lammps-md File-IO Wrapper Goal is to
# compare the internal temperature scaling in Native Lammps and the
# temperature scaling performed externally by a SimPhoNy python
# script.  Related USE CASE ID: Nano-Flow-U11d A simple molecular
# dynamics (MD) simulation using the microcanonical ensemble NVE
# (constant number of particles, volume and energy) with a
# Lennard-Jonnes 9-12 (LJ912) interatomic pair potential.  Temperature
# rescaling is done natively in SimPhoNy to demonstrate the way it can
# change the state of the system without relying on the simulation
# engine. The initial configuration is also entirely produced in
# SimPhoNy where the velocities are taken from a uniform distribution.
# The results for the temperature are compared with those produced
# natively by Lammps (using a fix temp/rescale) for initial
# validation.

from __future__ import print_function

import math

import numpy

from simphony.engine import lammps
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem
from simphony.cuds.particles import Particle, Particles
from simlammps.material import Material


def write_file(particles, file_format, file_name):
    if file_format == "EXYZ":
        f = open(file_name+".exyz", "w")
        f.write("{}\n".format(particles.count_of(CUDSItem.PARTICLE)))
        f.write("File generated by SimPhoNy 0.0.1\n")
        # normally the types of atoms should be inferred from the
        # shared data for now we assume one type, randomly chosen
        # as Al.
        for p in particles.iter_particles():
            f.write("Al {:f} {:f} {:f} ".format(
                p.coordinates[0],
                p.coordinates[1],
                p.coordinates[2]))
            # need to check first if the velocity exists.
            f.write(" {:f} {:f} {:f}\n".format(
                p.data[CUBA.VELOCITY][0],
                p.data[CUBA.VELOCITY][1],
                p.data[CUBA.VELOCITY][2]))
        # assume the supercell is already multiplied by the
        # lattice parameter This should be an issue for the
        # conversion work.
        f.write("alat\n"+"{:+f}\n".format(1.0))
        super_cell = particles.data_extension[
            lammps.CUBAExtension.BOX_VECTORS]
        f.write("supercell\n {:+f} {:+f} {:+f}\n".format(
            super_cell[0][0],
            super_cell[0][1],
            super_cell[0][2]))

        f.write(" {:+f} {:+f} {:+f}\n".format(
            super_cell[1][0],
            super_cell[1][1],
            super_cell[1][2]))

        f.write(" {:+f} {:+f} {:+f}\n".format(
            super_cell[2][0],
            super_cell[2][1],
            super_cell[2][2]))
        f.write(" Mass Al 1.0 \n")
        f.write("Cartesian coordinates\n")
        f.close()
    else:
        raise NotImplementedError()


# The total number of simulation cycles
number_NVE_cycles = 1000

# The number of MD steps in each cycle, this is the number of
# steps that are run at each call of wrapper.run().
temp_rescale_period = 200

# Create the input data in Python: This is a simple mono atomic system
# with one atomic type.

# The lattice parameter (in a cubic setup)
a_latt = 1.549

# Use a SC unit cell with basis for the FCC system
unit_cell = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
# The basis of the FCC system in the SC setup:
basis = [
    [0.0, 0.0, 0.0],
    [0.5, 0.5, 0.0],
    [0.5, 0.0, 0.5],
    [0.0, 0.5, 0.5]
]
# The number of periodic images, or duplications of the unit cell in each
# cubic lattice direction
N_dup = [4, 4, 4]
# total number of atoms after duplication
natoms = len(basis)*N_dup[0]*N_dup[1]*N_dup[2]

# Create a non-wrapper based, i.e., standalone SimPhoNy particle
# container for the atoms. Give it a name 'Test'
pc = Particles("Test")

i = 0
pos = [0, 0, 0]
atoms1 = basis
atoms = list()

# loop over the super cell (unit cell) directions
for i in range(0, 3):
    # loop over the duplicates (repetitions)
    for idup in range(0, N_dup[i]):
        # loop over the number of atoms in the basis.
        for j in range(0, len(atoms1)):
            pos = [0, 0, 0]
            for k in range(0, 3):
                pos[k] = idup * unit_cell[i][k] + atoms1[j][k]
            atoms.append(pos)
    atoms1 = atoms
    atoms = []

# have seed so the validation can be reproduced
numpy.random.seed(42)

# Define a material with a certain mass
material = Material(data={CUBA.MASS: 1.0})

for pos in atoms1:
    pos2 = [pos[0]*a_latt, pos[1]*a_latt, pos[2]*a_latt]
    p = Particle(coordinates=pos2)
    # usually, user asks the MD program to initialize the velocities
    # according to a Maxwell-Boltzmann distribution.(To DO: utility
    # functions in SimPhoNy).  Here we define a uniform random
    # distribution, the MD algorithm will in any case result in a MB
    # one quickly.
    p.data[CUBA.VELOCITY] = [
        numpy.random.uniform(-0.5, 0.5),
        numpy.random.uniform(-0.5, 0.5),
        numpy.random.uniform(-0.5, 0.5)
    ]
    p.data[CUBA.MATERIAL_TYPE] = material.uid
    pc.add_particles([p])


# Calculate the velocity of center of mass and reset it to zero to avoid drift.
# TODO: move to utility function
v_cm = [0, 0, 0]
for p in pc.iter_particles():
    v_cm[0] += p.data[CUBA.VELOCITY][0]
    v_cm[1] += p.data[CUBA.VELOCITY][1]
    v_cm[2] += p.data[CUBA.VELOCITY][2]

number_of_points = pc.count_of(CUDSItem.PARTICLE)

v_cm[0] /= number_of_points
v_cm[1] /= number_of_points
v_cm[2] /= number_of_points

for p in pc.iter_particles():
    p.data[CUBA.VELOCITY][0] -= v_cm[0]
    p.data[CUBA.VELOCITY][1] -= v_cm[1]
    p.data[CUBA.VELOCITY][2] -= v_cm[2]
    pc.update_particles([p])

super_cell = [
    tuple(N_dup[i]*x*a_latt for x in v) for i, v in enumerate(unit_cell)]
pc.data_extension = {lammps.CUBAExtension.BOX_VECTORS: super_cell}

# define the wrapper to use.
wrapper = lammps.LammpsWrapper()

# Add material
wrapper.SD.add_material(material)

# define the CM component of the SimPhoNy application model:
wrapper.CM_extension[lammps.CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"
wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = temp_rescale_period
wrapper.CM[CUBA.TIME_STEP] = 0.0025

# Define the BC component of the SimPhoNy application model:
wrapper.BC_extension[lammps.CUBAExtension.BOX_FACES] = ["periodic",
                                                        "periodic",
                                                        "periodic"]
pc_w = wrapper.add_dataset(pc)

# define the SP component of the SimPhoNy application model.  The
# following are the LJ parameters for this test. Normalized reduced
# LJ model with eps=sigma= 1, rcut = 2.5
# Use a direct YML description, to change.
wrapper.SP_extension[lammps.CUBAExtension.PAIR_POTENTIALS] = \
    ("lj:\n"
     "  global_cutoff: 1.12246\n"
     "  parameters:\n"
     "  - pair: [1, 1]\n"
     "    epsilon: 1.0\n"
     "    sigma: 1.0\n"
     "    cutoff: 2.5\n")

# The target temperature
# T, kinetic_energy are the instantaneous temperature and kinetic energy
T0 = 1.0

# The simulation is performed on the particle container with the
# wrapper, not on pc.  pc_MD is the particle container in the wrapper.
pc_MD = wrapper.get_dataset("Test")

# Create an extended special xyz file for atomistics.
write_file(particles=pc_MD, file_format="EXYZ",
           file_name="Input")
# output the temperature data to a file
ft = open("temp.dat", "w")
ft.write("#File generated by SimPhoNy 0.0.1\n")
ft.write("# Time T K\n")

for run in range(0, number_NVE_cycles):
    wrapper.run()
    # Save an extended special xyz file for atomistics.
    write_file(particles=pc_MD, file_format="EXYZ",
               file_name="input"+str(run))
    kinetic_energy = 0.0  # kinetic energy
    number_of_points = 0
    for par in pc_MD.iter_particles():
        number_of_points += 1
        ke = material.data[CUBA.MASS]*(
            par.data[CUBA.VELOCITY][0]*par.data[CUBA.VELOCITY][0] +
            par.data[CUBA.VELOCITY][1]*par.data[CUBA.VELOCITY][1] +
            par.data[CUBA.VELOCITY][2]*par.data[CUBA.VELOCITY][2])
        kinetic_energy += ke

    kinetic_energy *= 0.5
    kinetic_energy /= number_of_points

    T = 2.0*kinetic_energy/3.0

#   Possibly add a window in which the temperature rescale kicks in if
#   math.fabs( (T0-T)/T0) > 0.1:
    fac = math.sqrt(T0/T)
    ft.write('{:d} {:f} {:f} {:<2f}\n'.format(run, T, kinetic_energy, fac))
    print (("kinetic_energy:{} number_of_points:{} "
           "fac:{} T0:{} (running {} of {})").format(kinetic_energy,
                                                     number_of_points,
                                                     fac,
                                                     T0,
                                                     run,
                                                     number_NVE_cycles))

    for par in pc_MD.iter_particles():
        par.data[CUBA.VELOCITY] = tuple(v*fac for v in par.data[CUBA.VELOCITY])
        # potentially, other quantities could be related, such as momentum.
        pc_MD.update_particles([par])
ft.close()
