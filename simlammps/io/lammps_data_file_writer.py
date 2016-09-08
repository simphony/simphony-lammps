import time

import numpy

from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS

from ..common.atom_style_description import ATOM_STYLE_DESCRIPTIONS
from ..common.atom_style import get_lammps_string


class LammpsDataFileWriter(object):
    """  Class writes Lammps data file

    Lammps data file (a file type produced by lammps command
    `write_data`) contains a list of atoms and/or bonds. This
    class provides the means to write such file.

    Parameters
    ----------
    filename : str
        filename
    atom_style : AtomStyle
    number_atoms : int
        number of atoms
    number_atom_types : int
        number of atom types
    simulation_box : str
        simulation box
    material_type_to_mass : map of masses according to type, optional
        masses of each type

    """
    def __init__(self,
                 filename,
                 number_atoms,
                 number_atom_types,
                 atom_style,
                 simulation_box=None,
                 material_type_to_mass=None
                 ):
        self._file = open(filename, 'w')
        self._atom_style = atom_style
        self._number_atoms = number_atoms
        self._written_atoms = 0
        self._velocity_lines = []

        lines = ["LAMMPS data file via write_data"
                 ", file written by SimPhony-Lammps,  {}\n\n".format(
                     time.asctime(time.localtime()))]

        lines.append('{} atoms\n'.format(number_atoms))
        lines.append('{} atom types\n\n'.format(number_atom_types))
        lines.append("\n")
        lines.append(simulation_box)
        lines.append("\n")

        if material_type_to_mass:
            lines.append("Masses\n\n")
            for material_type in sorted(material_type_to_mass):
                mass = material_type_to_mass[material_type]
                lines.append('{} {}\n'.format(material_type, mass))
            lines.append("\n")

        self._file.writelines(lines)

        self._file.write("\nAtoms # {}\n\n".format(
            get_lammps_string(self._atom_style)))

    def write_atom(self, particle, material_type):
        """ Write an atom

        Atom lines should be written based on their atom style.  For example,
        "sphere" items are written as:::

           atom-ID atom-type diameter mass x y z

        While "atomic" atom style::

           atom-ID atom-type x y z


        Parameters
        ---------
        particle : Particle
            particle (containing required info for atom_type)
        material_type : int
            material type (i.e. CUBA.MATERIAL_TYPE)

        Returns
        -------
        lammps_id : int
            id used by lammps in file

        """
        self._written_atoms += 1

        if self._written_atoms > self._number_atoms:
            raise RuntimeError("Trying to write more atoms than expected")

        lammps_id = self._written_atoms
        atom_type = material_type

        # first comes 'id' and 'type'
        atom_line = '{0} {1}'.format(lammps_id, atom_type)

        # then write everything that is specific to this atom_style
        atom_description = ATOM_STYLE_DESCRIPTIONS[self._atom_style]
        for info in atom_description.attributes:
            value = info.convert_from_cuba(particle.data[info.cuba_key]) \
                if info.convert_from_cuba else particle.data[info.cuba_key]

            atom_line += ' {}'.format(format_cuba_value(value,
                                                        info.cuba_key))

        # then write the coordinates
        coordinates = format_cuba_value(particle.coordinates,
                                        CUBA.VELOCITY)  # using similar type
        atom_line += ' {} 0 0 0\n'.format(coordinates)
        self._file.write(atom_line)

        # save velocity line which will be written later
        velocity_line = '{0}'.format(lammps_id)
        for info in atom_description.velocity_attributes:
            value = info.convert_from_cuba(particle.data[info.cuba_key]) \
                if info.convert_from_cuba else particle.data[info.cuba_key]

            velocity_line += ' {}'.format(
                format_cuba_value(value, info.cuba_key))
        self._velocity_lines.append(velocity_line + '\n')

        if self._written_atoms == self._number_atoms:
            self._file.write("\nVelocities\n\n")
            self._file.writelines(self._velocity_lines)
            self._file.write("\n")

        return lammps_id

    def close(self):
        self._file.close()
        if self._written_atoms != self._number_atoms:
            raise RuntimeError(
                "Expected to write {} atoms but only wrote {}".format(
                    self._number_atoms,
                    self._written_atoms))


def format_number(value, dtype):
    if dtype == numpy.float64:
        return '{0:.16e}'.format(value)
    else:
        return '{}'.format(value)


def format_cuba_value(cuba_value, cuba_key):
    keyword = KEYWORDS[cuba_key.name]

    shape = keyword.shape
    dtype = keyword.dtype
    if shape == [1]:
        return format_number(cuba_value, dtype)
    elif shape == [3]:
        return '{} {} {}'.format(format_number(cuba_value[0], dtype),
                                 format_number(cuba_value[1], dtype),
                                 format_number(cuba_value[2], dtype))
    else:
        raise RuntimeError("Unsupported type: ".format(dtype))
