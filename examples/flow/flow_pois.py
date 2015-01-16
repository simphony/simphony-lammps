from __future__ import print_function
import sys
from sets import Set

from simphony.core.cuba import CUBA

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
    positions and types.  however, the id's do not have
    to match up (they can be totally different).
    Here, we just collect all the types and positions
    and check if they match.
    """

    handler = LammpsSimpleDataHandler()
    parser = LammpsDataFileParser(handler=handler)

    parser.parse(file_name)
    atoms = handler.get_atoms()

    # collect types and positions
    positions = Set()
    for index, atom in atoms.iteritems():
        atom_type = str(atom[0])
        coords = ' {0[0]:.3e} {0[1]:.3e} {0[2]:.3e}'.format(
            atom[1:4])
        positions.add(atom_type + coords)
    return positions

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
wrapper.CM[CUBA.NUMBEROF_TIME_STEPS] = 10000
wrapper.CM[CUBA.TIME_STEP] = 0.003
wrapper.CM[CUBA.PAIR_STYLE] = "lj"
wrapper.CM[CUBA.PAIR_STYLE_PARAMETERS] = ("- global_cutoff: 1.12246\n"
                                          "- pair: [1, 1]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n"
                                          "- pair: [1, 2]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n"
                                          "- pair: [1, 3]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n"
                                          "- pair: [2, 2]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n"
                                          "- pair: [2, 3]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n"
                                          "- pair: [3, 3]\n"
                                          "  epsilon: 1.0\n"
                                          "  sigma: 1.0\n"
                                          "  cutoff: 1.12246\n")

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
    msg = """ Results did not match up.
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
    print ("Results from a simphony-controlled lammps\
 succesfully matched up with results produced by lammps")
