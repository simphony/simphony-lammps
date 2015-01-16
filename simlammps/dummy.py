import uuid
from sets import Set

from simphony.cuds.particles import Particle, ParticleContainer
from simphony.core.cuba import CUBA

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler


class LammpsDummyConfig:
    """  Class provides some dummy configuration and state data

    """

    @staticmethod
    def configure_wrapper(wrapper):
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

        # add particle containers
        for i, pc in LammpsDummyConfig.get_particle_containers().iteritems():
            name = "foo{}".format(i)
            wrapper.add_particle_container(name, pc)

    @staticmethod
    def get_configuration():
        """ Get dummy configuration

        See text below to see what the placeholders in
        the string.
        """
        return CONFIGURATION

    @staticmethod
    def get_particle_containers():

        """ Get particle containers that match configuration

        Creating particle container with specific types
        to match how the wrapper is configuring things at the moment
        """
        pcs = []

        # reading positions/velocities from file
        handler = LammpsSimpleDataHandler()
        parser = LammpsDataFileParser(handler=handler)

        parser.parse('examples/flow/original_input.data')
        atoms = handler.get_atoms()
        velocities = handler.get_velocities()

        assert(len(atoms) == len(velocities))

        pcs = {}
        possible_atom_types = Set()
        for i in range(1, 4):
            pcs[i] = ParticleContainer()
            pcs[i].data[CUBA.MASS] = 1
            pcs[i].data[CUBA.MATERIAL_TYPE] = i
            possible_atom_types.add(i)

        for id, atom in atoms.iteritems():
            coord = tuple(atom[1:4])
            vel = tuple(velocities[id])
            p = Particle(id=uuid.uuid4(), coordinates=coord)
            p.data[CUBA.VELOCITY] = vel

            atom_type = atom[0]
            assert(atom_type in possible_atom_types)

            # add particle to PC which has
            # matching type
            pcs[atom_type].add_particle(p)
        return pcs

# dummy configuration
CONFIGURATION = """
# Control file generated by SimPhoNy
# 2-d LJ flow simulation

dimension	2
boundary	p s p

atom_style	atomic
neighbor	0.3 bin
neigh_modify	delay 5

{PAIR_STYLE}

# read from simphony-generated file
read_data {DATAFILE}

{PAIR_COEFF}

# define groups based on type

group flow type 1
group lower type 2
group upper type 3

compute	     mobile flow temp
fix	     1 all nve
fix	     2 flow temp/rescale 200 1.0 1.0 0.02 1.0
fix_modify   2 temp mobile

# Poiseuille flow

fix	     3 lower setforce 0.0 0.0 0.0
fix	     4 upper setforce 0.0 NULL 0.0
fix	     5 upper aveforce 0.0 -1.0 0.0
fix	     6 flow addforce 0.5 0.0 0.0
fix	     7 all enforce2d

# Run

timestep	{TIME_STEP}
thermo		500
thermo_modify	temp mobile

run {NUMBER_STEPS}

# write reults to simphony-generated file
write_data {DATAFILE}
"""
