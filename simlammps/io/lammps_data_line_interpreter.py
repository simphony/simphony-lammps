from enum import Enum


from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS


class AtomStyle(Enum):
    ATOMIC = 0
    GRANULAR = 1
    SPHERE = 1  # "granular" in LIGGHTS


class _ValueEntry(object):
    """  Information needed to interpret a value entry as CUBA value

    Parameters:
    -----------
    cuba_key : CUBA
        what CUBA attribute this value corresponds to
    conversion :
        method to value(s) to CUBA representation
    """
    def __init__(self, cuba_key, conversion=None):
        self.cuba_key = cuba_key
        self._conversion = conversion

    def process(self, values, index):
        """ return cuba value and

        Parameters
        ----------
        values : list of int

        Returns:
        --------
        cuba_value, index : CUBA, int
            value in correct cuba form (e.g. type) and new index
        """
        keyword = KEYWORDS[self.cuba_key.name]

        # TODO we are assuming that we only have a single
        # -dimension array (e.g. shape is [1] or [3]
        # instead of shape being something like [2, 3])
        shape = keyword.shape
        if shape == [1]:
            cuba_value = values[index]
            index += 1
        else:
            cuba_value = tuple(values[index.index+shape[0]])
            index += shape[0]

        if self._conversion:
            cuba_value = self._conversion(cuba_value)

        return cuba_value, index


# map from AtomStyle to associated list of data-properties
Styles = {AtomStyle.ATOMIC: [],
          AtomStyle.GRANULAR:
              [_ValueEntry(cuba_key=CUBA.RADIUS,
                           conversion=lambda x: x / 2),  # diameter to radius
               _ValueEntry(cuba_key=CUBA.DENSITY)]}


# TODO possibly attempt to interpret style from file (i.e. "Atoms # sphere")

class LammpsDataLineInterpreter(object):
    """  Class interprets lines in LAMMPS data files using atom-style

    Lines should be interpreted differently based upon their atom style.
    For example, sphere atom style::

       Atoms # sphere
       1 1 0.5 1.0000000000000000e+00 -5.0 0.0 0.0000000000000000e+00 0 0 0
       2 1 0.5 1.0000000000000000e+00 10.0 0.0 0.0000000000000000e+00 0 0 0

    The "sphere" atom style is interpreted as::

       atom-ID atom-type diameter density x y z

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

    """
    def __init__(self, atom_style=AtomStyle.ATOMIC):
        self._atom_style = atom_style

    def convert_atom_values(self, values):
        """  Converts list of values to CUBA/value dictionary

        Parameters
        ----------
        values : iterable of numbers
            numbers read from line in atom section of LAMMPS data file

        Returns
        -------
        (coordinates, cuba_values) : ((float, float, float), dict)
            (x-y-z coordinates, dictionary with CUBA keys/values)
        """

        # material type is always first
        cuba_values = {CUBA.MATERIAL_TYPE: values[0]}

        index = 1
        for entry in Styles[self._atom_style]:
            cuba_values[entry.cuba_key], index = entry.process(values, index)

        # coordinates come next
        coordinates = tuple(values[index:index+3])

        return coordinates, cuba_values
