from collections import namedtuple

import ctypes

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

# name is lammps'name (e.g. "x")
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
        # map from uid to index in lammps arrays
        self._index_of_uid = {}

        # cache of particle-related data (stored by CUBA keyword)
        self._cache = {}

        # cache of coordinates
        self._coordinates = []

        for entry in self._data_entries:
            self._cache[entry.CUBA] = []

    def retrieve(self):
        """ Retrieve all data from lammps

        """
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)

        for entry in self._data_entries:
            self._cache[entry.CUBA] = self._lammps.gather_atoms(
                entry.lammps_name,
                entry.type,
                entry.count)

    def send(self):
        """ Send data to lammps

        """
        self._lammps.scatter_atoms(
            "x", 1, 3,
            (ctypes.c_double * len(self._coordinates))(*self._coordinates))

        for entry in self._data_entries:
            values = self._cache[entry.CUBA]

            self._lammps.scatter_atoms(
                entry.lammps_name,
                entry.type,
                entry.count,
                (_get_ctype(entry) * len(values))(*values))

    def get_particle_data(self, uid):
        """ get particle data

        Parameters
        ----------
        uid : UUID
            uid for particle

        Returns
        -------
        data : DataContainer
            data of the particle
        """
        data = DataContainer()
        for entry in self._data_entries:
            i = self._index_of_uid[uid] * entry.count
            if entry.count > 1:
                # always assuming that its a tuple
                # ( see https://github.com/simphony/simphony-common/issues/18 )
                data[entry.CUBA] = tuple(
                    self._cache[entry.CUBA][i:i+entry.count])
            else:
                data[entry.CUBA] = self._cache[entry.CUBA][i]
        return data

    def set_particle(self, coordinates, data, uid):
        """ set particle coordinates and data

        Parameters
        ----------
        coordinates : tuple of floats
            particle coordinates
        data : DataContainer
            data of the particle
        uid : uuid
            uuid of the particle

        """
        if uid not in self._index_of_uid:
            self._index_of_uid[uid] = len(self._index_of_uid)

        i = self._index_of_uid[uid] * 3
        self._coordinates[i:i+3] = coordinates[0:3]

        index = self._index_of_uid[uid]
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
                    msg = "Problem with index {}".format(uid)
                    raise IndexError(msg)

    def get_coordinates(self, uid):
        """ Get coordinates for a particle

        Parameters
        ----------
        uid : uid
            uid of particle
        """
        i = self._index_of_uid[uid] * 3
        coords = self._coordinates[i:i+3]
        return tuple(coords)


def _get_ctype(entry):
    """ get ctype's type for entry

    Parameters
    ----------
    entry : LammpsData
        info about the atom parameter
    """
    if entry.type == 0:
        return ctypes.c_int
    elif entry.type == 1:
        return ctypes.c_double
    else:
        raise RuntimeError(
            "Unsupported type {}".format(entry.type))
