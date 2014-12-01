from __future__ import print_function
import sys
from sets import Set

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.lammps_process import LammpsProcess
from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.dummy import LammpsDummyConfig

# This example is to run a lammps flow
# problem. This example is to corresponds to the
# lammps example 'in.flow.pois'
# In this script, we do the following:
# (1) run lammps with 'in.flow.pois'
# (2) run lammps with SimPhoNy (with a similar configuration)
# (3) compare results


def get_set(file_name):
    """ Get set which each entry describes a point

    compare what was produced in each file
    each file should have particles with matching
    positions and velocities.  however, the id's
    can be totally different.  Here, we just collect
    all the positions and check if they match
    """

    handler = LammpsSimpleDataHandler()
    parser = LammpsDataFileParser(handler=handler)

    parser.parse(file_name)
    atoms = handler.get_atoms()
    vel = handler.get_velocities()

    positions_velocities = Set()
    for index, atom in atoms.iteritems():
        positions_velocities.add(
            str(atom[0]) + str(atom[1:4]) + str(vel[index]))
    return positions_velocities

# ----------------------------
# (1) run lammps with in.flow.pois
# ----------------------------
lammps = LammpsProcess()
command = ""
with open('examples/flow/in.flow.pois', 'r') as script:
        command = script.read()
lammps.run(command)

# ----------------------------
# (2) run lammps with SimPhony
# ----------------------------

wrapper = LammpsWrapper()
for i, pc in LammpsDummyConfig.get_particle_containers().iteritems():
    wrapper.add_particle_container(str(i), pc)

wrapper.run()

# ----------------------------
# (3) compare results
# ----------------------------
# TODO this should be done another way.
#
# data.lammps should have the final result of the simphony-based
# calculation while final_data.lammps should have the final result
# using in.flow.pois script

simphony_positions = get_set('final_data.lammps')
script_positions = get_set('data.lammps')

missing_point = False
msg = ""
for coord in simphony_positions:
    if coord not in script_positions:
        missing_point = True
if missing_point:
    msg = msg + """ Results did not match up.
Corresponding particle(s) not found. See
simphony_coordinates.txt and script_coordinates.txt """
    with open('script_coordinates.txt', 'w') as f:
        for c in sorted(script_positions):
            f.write(c + "\n")
    with open('simphony_coordinates.txt', 'w') as f:
        for c in sorted(simphony_positions):
            f.write(c + "\n")

if msg:
    sys.exit(msg)
else:
    print ("Results from a simphony-controlled lammps \
            succesfully matched up with results produced by lammps")
