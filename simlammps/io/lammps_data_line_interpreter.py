from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS

from ..common.atom_style_description import ATOM_STYLE_DESCRIPTIONS


class LammpsDataLineInterpreter(object):
    """  Class interprets lines in LAMMPS data files using atom-style

    Lines should be interpreted differently based upon their atom style.
    For example, sphere atom style::

       Atoms # sphere
       1 1 0.5 1.0000000000000000e+00 -5.0 0.0 0.0000000000000000e+00 0 0 0
       2 1 0.5 1.0000000000000000e+00 10.0 0.0 0.0000000000000000e+00 0 0 0

    The "sphere" atom style is interpreted as::

       atom-ID atom-type diameter mass x y z

    While "atomic" atom style::

       Atoms # atomic
       1 3 1.00000000000000e+00 1.0000000000000e+00 1.00000000000000e+00 0 0 0
       2 1 2.00000000000000e+00 2.0000000000000e+00 2.0000000000000e+00 0 0 0

    is interpreted as::

       atom-ID atom-type x y z

    Note that the last 3 values were not discussed because in the lammps
    documentation, it is noted that "each line can optionally have 3 flags
    (nx,ny,nz) appended to it, which indicate which image of a periodic
    simulation box the atom is in"

    Parameters
    ----------
    atom_style : AtomStyle
        style that lammps is using for "atoms"
    convert_atom_type_to_material :
        converts from atom_type to material

    """
    def __init__(self, atom_style, convert_atom_type_to_material):
        self._atom_style = atom_style
        self._convert_atom_type_to_material = convert_atom_type_to_material

    def convert_atom_values(self, values):
        """  Converts list of values to CUBA/value dictionary

        Parameters
        ----------
        values : iterable of numbers
            numbers read from line in atom section of LAMMPS data file

        Returns:
        --------
        coordinates : (float, float, float)
            x-y-z coordinates
        cuba_values : dict
            dictionary with CUBA keys/values

        """

        # material type is always first
        cuba_values = {CUBA.MATERIAL_TYPE:
                       self._convert_atom_type_to_material(values[0])}

        index = 1
        for value_info in ATOM_STYLE_DESCRIPTIONS[self._atom_style].attributes:
            cuba_values[value_info.cuba_key], index = \
                LammpsDataLineInterpreter.process_value(value_info,
                                                        values,
                                                        index)

        # coordinates come next
        coordinates = tuple(values[index:index+3])

        return coordinates, cuba_values

    def convert_velocity_values(self, values):
        """  Converts list of velocity values to CUBA/value dictionary

        Parameters
        ----------
        values : iterable of numbers
            numbers read from line in velocity section of LAMMPS data file

        Returns:
        --------
        cuba_velocity_values : dict
            dictionary with CUBA keys/values (related to velocity)

        """

        index = 0
        cuba_velocity_values = {}
        atom_style_description = ATOM_STYLE_DESCRIPTIONS[self._atom_style]
        for value_info in atom_style_description.velocity_attributes:
            cuba_velocity_values[value_info.cuba_key], index = \
                LammpsDataLineInterpreter.process_value(value_info,
                                                        values,
                                                        index)

        return cuba_velocity_values

    @staticmethod
    def process_value(value_info, values, index):
        """ return cuba value and updated index

        Parameters
        ----------
        value_info : ValueInfo
            information on value info
        values : list of numbers
            values to be processed
        index : int
            starting index of values to be processed

        Returns:
        --------
        cuba_value : CUBA
            value in correct cuba form (e.g. type)
        index : int
            incremented index (i.e. incremented pass this value)

        """
        keyword = KEYWORDS[value_info.cuba_key.name]

        # TODO we are assuming that we only have a single
        # -dimension array (e.g. shape is [1] or [3]
        # instead of shape being something like a [2, 3] matrix)
        shape = keyword.shape
        if shape == [1]:
            cuba_value = values[index]
            index += 1
        else:
            cuba_value = tuple(values[index:index+shape[0]])
            index += shape[0]

        if value_info.convert_to_cuba:
            cuba_value = value_info.convert_to_cuba(cuba_value)

        return cuba_value, index
