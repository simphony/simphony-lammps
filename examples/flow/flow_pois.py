from __future__ import print_function
import shutil
import sys
import numpy.testing as npt

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.lammps_process import LammpsProcess
from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler

# This example is to run a lammps flow
# problem. This example is to corresponds to the
# lammps example 'in.flow.pois'
# In this script, we do the following:
# (1) run lammps with 'in.flow.pois'
# (2) run lammps with SimPhoNy (with a similar configuration)
# (3) compare results


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

# a hack to use the data (420 atoms laid out in a lattice)
# produced by in.flow.pois script.  TODO this should be replaced using
# the available methods (e.g. add_particlecontainer,
# add_particle, update_particle)
shutil.copyfile("examples/flow/original_input.data", "data.lammps")
wrapper.dummy_init_data()

wrapper.run()

# ----------------------------
# (3) compare results
# ----------------------------
# TODO this should be done another way.
#
# data.lammps should have the final result of the simphony-based
# calculation while final_data.lammps should have the final result
# using in.flow.pois script

handler = LammpsSimpleDataHandler()
parser = LammpsDataFileParser(handler=handler)

parser.parse('final_data.lammps')
atoms_lammps_script = handler.get_atoms()

parser.parse('data.lammps')
atoms_lammps_simphony = handler.get_atoms()

assert len(atoms_lammps_script) == len(atoms_lammps_simphony)

# compare what was produced in each file
msg = None
for id, atom_script in atoms_lammps_script.iteritems():
    atom_simphony = atoms_lammps_simphony[id]
    try:
        npt.assert_allclose(
            atom_simphony, atom_script, rtol=1e-8, atol=0)
    except AssertionError:
        if not msg:
            msg = " Results did not match up.\n"
        msg += " atom with id={}\n".format(id)
        msg += "   simphony-based: {}\n".format(atom_simphony)
        msg += "   script-based  : {}\n".format(atom_script)

if msg:
    sys.exit(msg)
