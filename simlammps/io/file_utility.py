from simphony.cuds.particles import Particle, Particles
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.io.lammps_data_line_interpreter import LammpsDataLineInterpreter
from simlammps.config.domain import get_box
from simlammps.cuba_extension import CUBAExtension
from simlammps.common.atom_style import (AtomStyle, get_atom_style)
from simlammps.io.lammps_data_file_writer import LammpsDataFileWriter
from simlammps.state_data import StateData
from simlammps.material import Material


def read_data_file(filename, atom_style=None, name=None):
    """ Reads LAMMPS data file and create CUDS objects

    Reads LAMMPS data file and create a Particles and StateData. The StateData
    will contain a material for each atom type (e.g. CUBA.MATERIAL_TYPE).

    The attributes for each particle are based upon what atom-style
    the file contains (i.e. "sphere" means that particles in addition to having
    CUBA.VELOCITY will also have a CUBA.RADIUS and CUBA.MASS). See
    'atom_style' for more details.

    Parameters
    ----------
    filename : str
        filename of lammps data file
    atom_style : AtomStyle, optional
        type of atoms in the file.  If None, then an attempt of
        interpreting the atom-style in the file is performed.
    name : str, optional
        name to be given to returned Particles.  If None, then filename is
        used.

    Returns
    -------
    particles : Particles
        particles
    SD : StateData
        SD containing materials

    """
    handler = LammpsSimpleDataHandler()
    parser = LammpsDataFileParser(handler=handler)

    parser.parse(filename)

    if atom_style is None:
        atom_style = (
            get_atom_style(handler.get_atom_type())
            if handler.get_atom_type()
            else AtomStyle.ATOMIC)

    types = (atom_t for atom_t in range(1, handler.get_number_atom_types()+1))
    atoms = handler.get_atoms()
    velocities = handler.get_velocities()
    masses = handler.get_masses()

    box_origin = handler.get_box_origin()
    box_vectors = handler.get_box_vectors()

    type_to_material_map = {}

    SD = StateData()

    # set up a Material for each different type
    for atom_type in types:
        material = Material()
        description = "Material for lammps atom type (originally '{}')".format(
            atom_type
        )
        material.description = description
        type_to_material_map[atom_type] = material.uid
        SD.add_material(material)

    # add masses to materials
    for atom_type, mass in masses.iteritems():
        material = SD.get_material(type_to_material_map[atom_type])
        material.data[CUBA.MASS] = mass
        SD.update_material(material)

    def get_material(atom_type):
        return type_to_material_map[atom_type]

    interpreter = LammpsDataLineInterpreter(atom_style, get_material)

    # create particles
    particles = Particles(name=name if name else filename)
    particles.data_extension = {CUBAExtension.BOX_ORIGIN: box_origin,
                                CUBAExtension.BOX_VECTORS: box_vectors}

    # add each particle
    for lammps_id, values in atoms.iteritems():
        coordinates, data = interpreter.convert_atom_values(values)
        data.update(interpreter.convert_velocity_values(velocities[lammps_id]))

        p = Particle(coordinates=coordinates, data=data)
        particles.add_particles([p])

    return particles, SD


def write_data_file(filename,
                    particles,
                    state_data,
                    atom_style=AtomStyle.ATOMIC):
    """ Writes LAMMPS data file from CUDS objects

    Writes LAMMPS data file from a list of Particles.

    The particles will be annotated with their Simphony-uid. For example::

        10 1 17 -1.0 10.0 5.0 6.0   # uid:'40fb302c-6e71-11e5-b35f-08606e7c2200'  # noqa


    Parameters
    ----------
    filename : str
        filename of lammps data file

    particles : Particles or iterable of Particles
        particles

    state_data : StateData
        SD containing materials

    atom_style : AtomStyle, optional
        type of atoms to be written to file

    Raises

    """
    if type(particles) is not list:
        particles = [particles]

    num_particles = sum(
        pc.count_of(CUDSItem.PARTICLE) for pc in particles)

    # get a mapping from material_type to atom_type
    #  note that atom_type goes from 1 to N
    material_to_atom = {}
    number_atom_types = 0
    for material in state_data.iter_materials():
        number_atom_types += 1
        material_to_atom[material.uid] = number_atom_types

    box = get_box([pc.data_extension for pc in particles])

    material_type_to_mass = None if not _style_has_masses(
        atom_style) else _get_mass(state_data)

    writer = LammpsDataFileWriter(filename,
                                  atom_style=atom_style,
                                  number_atoms=num_particles,
                                  number_atom_types=number_atom_types,
                                  material_type_to_atom_type=material_to_atom,
                                  simulation_box=box,
                                  material_type_to_mass=material_type_to_mass)
    for pc in particles:
        for p in pc.iter_particles():
            writer.write_atom(p)
    writer.close()


def _style_has_masses(atom_style):
    """ Returns if atom style has masses

    """
    # TODO have a relationship between atom_style and if masses are needed
    return atom_style != AtomStyle.GRANULAR


def _get_mass(state_data):
    """ Get a dictionary from 'material type' to 'mass'.

    Parameters:
    -----------
    state_data : StateData
        SD containing material with mass

    """
    material_type_to_mass = {}
    for material in state_data.iter_materials():
        try:
            material_type_to_mass[material.uid] = material.data[CUBA.MASS]
        except KeyError:
            raise RuntimeError(
                "CUBA.MASS is missing from material '{}'".format(
                    material.uid))
    return material_type_to_mass
