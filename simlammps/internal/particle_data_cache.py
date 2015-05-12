from collections import namedtuple

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

# type = 0 = int or 1 = double
# count = # of per-atom values, 1 or 3, etc
_LammpsData = namedtuple(
    '_LammpsData', ['CUBA', 'lammps_name', "type", "count"])


class ParticleDataCache(object):
    """ Class handles particle-related data

    Class stores all particle-related data and has methods
    in order to retrieve this data from LAMMPS and send this
    data to LAMMPS.


    Parameters
    ----------
    lammps :
        lammps python wrapper

    """
    def __init__(self, lammps):
        self._lammps = lammps

        # TODO this should be based on what atom-style we are using
        # and configured by the user of this class (instead of
        # hard coded here)
        self._data_entries = [_LammpsData(CUBA=CUBA.VELOCITY,
                                          lammps_name="v",
                                          type=1,  # double
                                          count=3),
                              _LammpsData(CUBA=CUBA.MATERIAL_TYPE,
                                          lammps_name="type",
                                          type=0,  # int
                                          count=1)]

        self._cache = {}
        self._coordinates = []
        self._id_cache = None

        for entry in self._data_entries:
            self._cache[entry.CUBA] = []

    def retrieve(self):
        """ Retrieve

        Parameters
        ----------
        particle : Particle
            particle to be set
        uname : string
            non-changing unique name of particle container

        """

        self._id_cache = self._lammps.gather_atoms("id", 0, 1)
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)

        for entry in self._data_entries:
            self._cache[entry.CUBA] = self._lammps.gather_atoms(
                entry.lammps_name,
                entry.type,
                entry.count)

    def send(self):
        for entry in self._data_entries:
            values = self._cache[entry.CUBA]

            extract = self._lammps.extract_atom(entry.lammps_name,
                                                _get_extract_type(entry))

            if entry.count == 1:
                for i in range(len(values)):
                    extract[i] = values[i]
            elif entry.count == 3:
                for i in range(len(values)/3):
                    for j in range(entry.count):
                        extract[i][j] = values[i*3+j]
            else:
                raise RuntimeError("Unsupported count {}".format(
                    entry.count))
            return

    def get_particle_data(self, index):
        """ get particle data

        Parameters
        ----------
        index : int
            index location of particle in cache

        Returns
        -------
        data : DataContainer
            data of the particle
        """
        data = DataContainer()
        for entry in self._data_entries:
            i = index * entry.count
            if entry.count > 1:
                # always assuming that its a tuple
                # ( see https://github.com/simphony/simphony-common/issues/18 )
                data[entry.CUBA] = tuple(
                    self._cache[entry.CUBA][i:i+entry.count])
            else:
                data[entry.CUBA] = self._cache[entry.CUBA][i]
        return data

    def set_particle(self, coordinates, data, index):
        """ set particle coordinates and data

        Parameters
        ----------
        coordinates : tuple of floats
            particle coordinates
        data : DataContainer
            data of the particle
        index : int
            index location of particle in cache to be updated

        """
        i = index * 3
        self._coordinates[i:i+3] = coordinates[0:3]

        for entry in self._data_entries:
            i = index * entry.count
            if entry.count > 1:
                self._cache[entry.CUBA][i:i+entry.count] = \
                    data[entry.CUBA][0:entry.count]
            else:
                if i < len(self._cache[entry.CUBA]):
                    self._cache[entry.CUBA][i] = data[entry.CUBA]
                elif i == len(self._cache[entry.CUBA]):
                    self._cache[entry.CUBA].append(data[entry.CUBA])
                else:
                    msg = "Problem with index {}".format(index)
                    msg += "When particle data is first set it," \
                           " it must be set in order (from 0 to N"
                    raise IndexError(msg)

    def get_coordinates(self, index):
        """ Get coordinates for a particle

        Parameters
        ----------
        index : int
            index location of particle in array
        """
        i = index * 3
        coords = self._coordinates[i:i+3]
        return tuple(coords)


def _get_extract_type(entry):
    """ get LAMMPS "extract" type for extract_atoms method

    Parameters
    ----------
    entry : LammpsData
        info about the atom parameter

    for the method extract_atoms, the parameter 'type' can be:
       0 = vector of ints
       1 = array of ints
       2 = vector of doubles
       3 = array of doubles

    """
    if entry.count == 1 and entry.type == 0:
        return 0
    elif entry.count == 3 and entry.type == 0:
        return 1
    elif entry.count == 1 and entry.type == 1:
        return 2
    elif entry.count == 3 and entry.type == 1:
        return 3
    else:
        raise RuntimeError(
            "Unsupported type {} and count {}".format(entry.type,
                                                      entry.count))
