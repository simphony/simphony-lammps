import ctypes

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

        for entry in self._data_entries:
            self._cache[entry.CUBA] = []

    def retrieve(self):
        for entry in self._data_entries:
            self._cache[entry.CUBA] = self._lammps.gather_atoms(
                entry.lammps_name,
                entry.type,
                entry.count)

    def send(self):
        for entry in self._data_entries:
            values = self._cache[entry.CUBA]

            if entry.type is 1:
                values = (ctypes.c_float * len(values))(*values)
            else:
                values = (ctypes.c_int * len(values))(*values)
            self._lammps.scatter_atoms(entry.lammps_name,
                                       entry.type,
                                       entry.count,
                                       values)

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

    def set_particle_data(self, data, index):
        """ set particle data

        Parameters
        ----------
        data : DataContainer
            data of the particle

        index : int
            index location of particle in cache to be updated

        """
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
