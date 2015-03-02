# TODO this is an UNTESTED pseudocode developed from a use case
# that needs to be cleaned up and used as a test example during
# development

# In this use case we create a simphony model
# containing an SD for an Atomistic flow problem

from __future__ import print_function

import math

from simphony.engine import lammps
from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particle, ParticleContainer


# create the data in Python:
# this is a simple monoatomic system with one
# particle atomic type, in general we may have two
# types in the basis of the unit cell.
a_latt = 1.549

# we use a simple cubic system with basis for the FCC system
unit_cell = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
N_dup = [4, 4, 4]
basis = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]]

# total number of atoms after duplication
natoms = len(basis)*N_dup[0]*N_dup[1]*N_dup[2]

pc = ParticleContainer("Test")

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
                # print i, idup, j, k, unit_cell[i][k], basis[j][k], pos
            atoms.append(pos)
    atoms1 = atoms
    atoms = []

for pos in atoms1:
    p = Particle(coordinates=pos)

    # if this is not specified the MD wrapper assumes its zero at first anyway
    p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)

    # usually, the user asks the MD program to start
    # the velocities according to a Maxwell-Boltzmann
    # distribution.(utility functions to do this
    # would be ideal).
    pc.add_particle(p)

# should use CUBA.MATERIAL_TYPE or CUBA.ATOM_TYPE
# in the future, we would ld like to have CUBA.PERIODIC_ELEMENT
pc.data[CUBA.MATERIAL_TYPE] = 1
pc.data[CUBA.MASS] = 1

# but actually it should be "CUBA.SUPER_CELL_VECTORS" or "CUBA.BOX_VECTORS"
super_cell = [tuple(N_dup[i]*x for x in v) for i, v in enumerate(unit_cell)]
pc.data[CUBA.BOX_VECTORS] = super_cell

wrapper = lammps.LammpsWrapper()

# this might change, or CUBA.NVE...
wrapper.CM[CUBA.THERMODYNAMIC_ENSEMBLE] = "NVE"

# rescale the temperature every so many steps
N_run_cycles_temperature = 10

# sub cycle steps
# TODO replace CUBA.NUMBER_OF_TIME_STEPS with NUMBER_OF_STEPS
wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = N_run_cycles_temperature
# TODO replace CUBA.TIME_STEP with INTEGRATION_TIME_STEP
wrapper.CM[CUBA.TIME_STEP] = 0.0025

# could be possibly ["periodic", "periodic", "periodic"]
wrapper.BC[CUBA.BOX_FACES] = ["periodic", "periodic", "periodic"]
wrapper.add_particle_container(pc)

# following LJ parameters for this test:
# eps = sigma = 1.0 (we work with a normalized,
# reduced LJ model with eps=sigma= 1).
# rcut = 2.5
wrapper.SP[CUBA.PAIR_POTENTIALS] = ("lj:\n"
                                    "  global_cutoff: 1.12246\n"
                                    "  parameters:\n"
                                    "  - pair: [1, 1]\n"
                                    "    epsilon: 1.0\n"
                                    "    sigma: 1.0\n"
                                    "    cutoff: 2.5\n")

T0 = 1.0  # this is the target temperature
# T, kinetic_energy are the instantaneous temperature and kinetic energy

# this is the total number of simulation steps.
N_run_total_cycle_steps = 100

pc_MD = wrapper.get_particle_container("Test")

for run in range(0, N_run_total_cycle_steps):
    wrapper.run()

    kinetic_energy = 0.0  # kinetic energy
    number_of_points = 0
    for par in pc_MD.iter_particles():
        number_of_points += 1
        kinetic_energy += pc_MD.data[CUBA.MASS]*(
            par.data[CUBA.VELOCITY][0]*par.data[CUBA.VELOCITY][0] +
            par.data[CUBA.VELOCITY][1]*par.data[CUBA.VELOCITY][1] +
            par.data[CUBA.VELOCITY][2]*par.data[CUBA.VELOCITY][2])
    # we may also get this from the output of LAMMPS directly...
    # i.e, either the total temperature or the local kinetic energy..
    kinetic_energy *= 0.5

    print ("kinetic_energy:{} number_of_points:{}  (running {} of {})".format(
        kinetic_energy, number_of_points, run, N_run_total_cycle_steps))

    # there is a K_b in the denominator, but it is
    # assumed to be 1, due to the reduced units.
    T = 2.0*kinetic_energy/(3*number_of_points)
    fac = math.sqrt(T0/T)
    for par in pc_MD.iter_particles():
        par.data[CUBA.VELOCITY] = tuple(v*fac for v in par.data[CUBA.VELOCITY])
        # potentially, other quantities could be related, such as momentum.
        pc_MD.update_particle(par)
