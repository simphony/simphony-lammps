from simphony.cuds.particles import Particle, Particles
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.io.lammps_data_line_interpreter import LammpsDataLineInterpreter
from simlammps.cuba_extension import CUBAExtension
from simlammps.io.atom_style import (AtomStyle, get_atom_style)


def read_data_file(filename, atom_style=None):
    """ Reads LAMMPS data file and create CUDS objects

    Reads LAMMPS data file and create list of Particles. The returned list
    of Particles will contain a Particles for each atom type (i.e.
    CUBA.MATERIAL_TYPE). The name of the Particles will be the atom type (e.g.
    a Particles with atom_type/CUBA.MATERIAL_TYPE of 1 will have the name "1")

    The attributes for each particle are based upon what atom-style
    the file contains (i.e. "sphere" means that particles in addition to having
    CUBA.VELOCITY will also have a CUBA.RADIUS and CUBA.DENSITY). See
    'atom_style' for more details.

    Parameters
    ----------
    filename : str
        filename of lammps data file

    atom_style : AtomStyle
        type of atoms in the file.  If None, then an attempt of
        interpreting the atom-style in the file is performed.

    Returns
    -------
    particles_list : list of Particles
        list of Particles where each Particles has a name equal
        to their CUBA.MATERIAL_TYPE and is filled up with
        particles of that type.

    """
    handler = LammpsSimpleDataHandler()
    parser = LammpsDataFileParser(handler=handler)

    parser.parse(filename)

    if atom_style is None:
        atom_style = (
            get_atom_style(handler.get_atom_type())
            if handler.get_atom_type()
            else AtomStyle.ATOMIC)

    interpreter = LammpsDataLineInterpreter(atom_style)

    types = (atom_t for atom_t in range(1, handler.get_number_atom_types()+1))
    atoms = handler.get_atoms()
    velocities = handler.get_velocities()
    masses = handler.get_masses()

    box_origin = handler.get_box_origin()
    box_vectors = handler.get_box_vectors()

    type_to_particles_map = {}

    # set up a Particles for each different type
    for atom_type in types:
        data = DataContainer()
        data[CUBA.MATERIAL_TYPE] = atom_type

        data_extension = {CUBAExtension.BOX_ORIGIN: box_origin,
                          CUBAExtension.BOX_VECTORS: box_vectors}

        particles = Particles(name="{}".format(atom_type))
        particles.data = data
        particles.data_extension = dict(data_extension)

        type_to_particles_map[atom_type] = particles

    # set masses
    for atom_type, mass in masses.iteritems():
        data = type_to_particles_map[atom_type].data
        data[CUBA.MASS] = mass
        type_to_particles_map[atom_type].data = data

    # add each particle to each Particles
    for lammps_id, values in atoms.iteritems():
        p = Particle()
        p.coordinates, p.data = interpreter.convert_atom_values(values)

        # TODO #9 (removing material type
        atom_type = p.data[CUBA.MATERIAL_TYPE]
        del p.data[CUBA.MATERIAL_TYPE]

        p.data[CUBA.VELOCITY] = tuple(velocities[lammps_id][0:3])

        type_to_particles_map[atom_type].add_particles([p])

    return type_to_particles_map.values()
