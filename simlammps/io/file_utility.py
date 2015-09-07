from simphony.cuds.particles import Particle, Particles
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.cuba_extension import CUBAExtension


def read_data_file(filename):
    """ Reads LAMMPS data file and create CUDS objects

    Reads LAMMPS data file and create list of Particles. The returned list
    of Particles will contain a Particles for each atom type (i.e.
    CUBA.MATERIAL_TYPE). The name of the Particles will be the atom type (e.g.
    a Particles with atom_type/CUBA.MATERIAL_TYPE of 1 will have the name "1")

    Parameters
    ----------
    filename : str
        filename of lammps data file

    Returns
    -------
    particles_list : list of Particles

    """
    handler = LammpsSimpleDataHandler()
    parser = LammpsDataFileParser(handler=handler)
    parser.parse(filename)

    atoms = handler.get_atoms()
    velocities = handler.get_velocities()
    masses = handler.get_masses()

    box_origin = handler.get_box_origin()
    box_vectors = handler.get_box_vectors()

    type_to_particles_map = {}

    # set up a Particles for each different type
    for atom_type, mass in masses.iteritems():
        data = DataContainer()
        data[CUBA.MASS] = mass

        data_extension = {}
        data_extension[CUBAExtension.BOX_ORIGIN] = box_origin
        data_extension[CUBAExtension.BOX_VECTORS] = box_vectors

        particles = Particles(name="{}".format(atom_type))
        particles.data = data
        particles.data_extension = dict(data_extension)

        type_to_particles_map[atom_type] = particles

    # add each particle to each Particles
    for lammps_id, atom in atoms.iteritems():
        p = Particle()
        p.coordinates = tuple(atom[1:4])

        p.data[CUBA.VELOCITY] = tuple(velocities[lammps_id])

        atom_type = atom[0]
        type_to_particles_map[atom_type].add_particles([p])

    return type_to_particles_map.values()
