# Demonstration of the SimPhoNy Lammps-md File-IO Wrapper using the
# final CUDS in D1.6 perform a simple molecular dynamics with several
# ensembles using SimPhoNy CUDS


from __future__ import print_function

import math
import numpy


from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem
from simphony.cuds.particles import Particle, Particles

from simphony.api import CUDS, Simulation
from simphony.cuds.meta import api

##############################################################
##### Preprocessing step                                ######          
##### Create initial PARTICLES                          ######
##### can be replaced with the crystal tools in common. ######
##############################################################
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
# The number of periodic images, or duplications of the unit cell in
# each cubic lattice direction
N_dup = [4, 4, 4]
# total number of atoms after duplication
natoms = len(basis)*N_dup[0]*N_dup[1]*N_dup[2]

# create a Data set CUDS component named test 
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

for pos in atoms1:
    pos2 = [pos[0]*a_latt, pos[1]*a_latt, pos[2]*a_latt]
    p = Particle(coordinates=pos2)
    # Usually, user asks the MD program to initialize the velocities
    # according to a Maxwell-Boltzmann distribution. In this example
    # we define a uniform random distribution, the MD algorithm will
    # in any case result in a MB one quickly.
    p.data[CUBA.VELOCITY] = [
        numpy.random.uniform(-0.5, 0.5),
        numpy.random.uniform(-0.5, 0.5),
        numpy.random.uniform(-0.5, 0.5)
    ]
    pc.add_particles([p])


# Calculate the velocity of center of mass and reset it to zero to
# avoid drift of the whole system.
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
######################################



# define a material:
mat = api.Material(name='a_material')

# give it a (shared) material property
mat.data[CUBA.MASS]=1.0

# mark all particles in pc to belong to mat: 
for p in pc.iter_particles():
    p.data[CUBA.MATERIAL] = mat.uid

# define a cuds to hold the computational model:
cuds = CUDS (name= 'fluid') 

# add pc to it. 
cuds.add(pc) 

# create a simulation box CUDS component, and add it as a CUDS
# component:
box = api.Box(name='simulation_box') 

super_cell = [
    tuple(N_dup[i]*x*a_latt for x in v) for i, v in enumerate(unit_cell)]

box.vector = [super_cell(:,1), super_cell(:,2), super_cell(:,3)] 
# need to check the order. 

cuds.add(box)

# create a molecular dynamics model (NVE with temperature rescaling)

md_nve = api.MolecularDynamics(name='md_test') 
# add the physics equation to the CUDS computational model. 
cuds.add(md_nve)
# or in one statement: cuds.add(MD(name='mdnve')) 


# create a empty thermostat as a general material relation
thermo = api.TemperatureRescaling (name='tempscale')
thermo.description = 'a simple temperature rescaling test'
thermo.temperature = [0.0, 1.0] # scale the temperature from 0  to 1
thermo.coupling_time = 0.000025 # this is in time units, not steps.
# add the thermostat to the CUDS computational model. 
thermo.materials = [mat.uid]
cuds.add(thermo) 

# create a new solver component:
sp = api.SolverParameter(name = 'solverParameters')


# integration time:
itime = IntegrationTime(name="md_nve_integration_time")
itime.time=0.0
itime.step=0.0025
itime.final = 0.25
cuds.add(itime)

verlet = Verlet(name="Verlet")

cuds.add(verlet)

# define periodic boundary condition
pbc = api.Periodic(name= 'pbc')
cuds.add(pbc)

# attache this to the boundaries of the box: 
box= cuds.get('simulation_box')
box.condition = [cuds.get('pbc').uid,  pbc.uid, pbc.udi]
cuds.update(box) 


# define the interatomic force as material relation  
lj = Lennard_Jones_6_12 (name = 'LennardJones') 
lj.cutoff_distance = 2.5
lj.energy_well_depth = 1.0
lj.van_der_waals_radius = 1.0 
lj.materials = [cuds.get('mat').uid, cuds.get('mat').uid] 
# sim = Simulation(cuds = cuds, engine = LAMMPS() ) 

# initialisation of the simulation
sim = Simulation(cuds, "LAMMPS", use_internal_interface = true) 
sim.run()

newcuds= sim.get_cuds() 
newcuds.remove('thermo') 
thermo = NoseHoover(name='thermo')
thermo.temperature= [ 1.0, 1.2]
thermo.coupling_time=0.00000025
thermo.materials=[newcuds.get('mat').uid,]
newcuds.add(thermo)
pc=newcuds.get('Test') 
# pc is now a proxy to the pc in the "wrapper" managed by the sim. 
particle = pc.get_particle(112324)
particle.data[CUBA.VELOCITY]= -5.0 
pc.update_particles([particle,]) 

sim.run()

