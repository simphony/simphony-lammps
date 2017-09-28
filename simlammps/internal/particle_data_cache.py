import ctypes
import numpy

from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS
from simphony.core.data_container import DataContainer

from simlammps.common.atom_style_description import get_all_attributes


class ParticleDataCache(object):
    """ Class handles particle-related data

    Class stores all particle-related data and has methods
    in order to retrieve this data from LAMMPS and send this
    data to LAMMPS.

    Parameters
    ----------
    lammps :
        lammps python wrapper
    atom_style : AtomStyle
        style of atoms
    material_atom_type_manager : MaterialAtomTypeManager
        class that manages the relationship between material-uid and atom_type

    """
    def __init__(self, lammps, atoms_style, material_atom_type_manager):
        self._lammps = lammps

        self._material_atom_type_manager = material_atom_type_manager

        self._data_attributes = get_all_attributes(atoms_style)

        # map from uid to 'index in lammps arrays'
        self._index_of_uid = {}

        # cache of particle-related data (stored by CUBA keyword)
        self._cache = {}

        # cache of coordinates
        self._coordinates = []

        self._cache[CUBA.MATERIAL_TYPE] = []

        for attribute in self._data_attributes:
            self._cache[attribute.cuba_key] = []

    def retrieve(self):
        """ Retrieve all data from lammps

        """
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)

        for attribute in self._data_attributes:
            keyword = KEYWORDS[attribute.cuba_key.name]

            # we handle material type seperately
            if attribute.cuba_key == CUBA.MATERIAL_TYPE:
                self._cache[attribute.cuba_key] = self._lammps.gather_atoms(
                    "type",
                    0,
                    1)
                continue

            self._cache[attribute.cuba_key] = self._lammps.gather_atoms(
                attribute.lammps_key,
                _get_type(keyword),
                _get_count(keyword))

    def send(self):
        """ Send data to lammps

        """
        self._lammps.scatter_atoms(
            "x", 1, 3,
            (ctypes.c_double * len(self._coordinates))(*self._coordinates))

        for attribute in self._data_attributes:
            keyword = KEYWORDS[attribute.cuba_key.name]
            values = self._cache[attribute.cuba_key]

            # we handle material type seperately
            if attribute.cuba_key == CUBA.MATERIAL_TYPE:
                self._lammps.scatter_atoms("type",
                                           0,
                                           1,
                                           (ctypes.c_int * len(
                                               values))(*values))
                continue

            self._lammps.scatter_atoms(attribute.lammps_key,
                                       _get_type(keyword),
                                       _get_count(keyword),
                                       (_get_ctype(keyword) * len(values))(
                                           *values))

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

        index = self._index_of_uid[uid]

        for attribute in self._data_attributes:
            # we handle material type seperately
            if attribute.cuba_key == CUBA.MATERIAL_TYPE:
                # convert from the integer atom_type to material-uid)
                data[CUBA.MATERIAL_TYPE] = \
                    self._material_atom_type_manager.get_material_uid(
                        self._cache[CUBA.MATERIAL_TYPE][index])
                continue

            count = _get_count(KEYWORDS[attribute.cuba_key.name])
            i = index * count
            if count > 1:
                # always assuming that its a tuple
                # ( see https://github.com/simphony/simphony-common/issues/18 )
                data[attribute.cuba_key] = tuple(
                    self._cache[attribute.cuba_key][i:i+count])
            else:
                data[attribute.cuba_key] = self._cache[attribute.cuba_key][i]
        return data

    def get_coordinates(self, uid):
        """ Get coordinates for a particle

        Parameters
        ----------
        uid : uid
            uid of particle
        """
        i = self._index_of_uid[uid] * 3
        coordinates = self._coordinates[i:i+3]
        return tuple(coordinates)

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

        # add each attribute
        for attribute in self._data_attributes:
            value = data[attribute.cuba_key]

            if attribute.cuba_key == CUBA.MATERIAL_TYPE:
                # convert to atom_type (int)
                value = self._material_atom_type_manager.get_atom_type(value)
            self._add_to_cache(attribute.cuba_key,
                               index,
                               value)

    def _add_to_cache(self, cuba_key, index, value):
        """ Add value to cache

        Parameters
        ----------
        cuba_key : CUBA
            cuba key
        index : int
            index in cache
        value : float or int or float[3] or int[3]
            value added to cache

        """
        keyword = KEYWORDS[cuba_key.name]
        shape = keyword.shape

        if shape == [1]:
            if index < len(self._cache[cuba_key]):
                self._cache[cuba_key][index] = value
            elif index == len(self._cache[cuba_key]):
                self._cache[cuba_key].append(value)
            else:
                msg = "Problem with index {}".format(index)
                raise IndexError(msg)
        elif shape == [3]:
            index = index * 3
            self._cache[cuba_key][index:index+3] = value[0:3]
        else:
            raise RuntimeError("Unsupported shape: {0}".format(shape))


def _get_ctype(keyword):
    """ get ctype

    Parameters
    ----------
    keyword : Keyword

    """
    if keyword.dtype == numpy.int32:
        return ctypes.c_int
    elif keyword.dtype == numpy.float64:
        return ctypes.c_double
    else:
        raise RuntimeError(
            "Unsupported type {}".format(keyword.dtype))


def _get_type(keyword):
    """ get type

    Get type which is a 1 or 0 to signify if its a
    int or float for lammps gather/scatter methods

    Parameters
    ----------
    keyword : Keyword

    """
    if keyword.dtype == numpy.int32:
        return 0
    elif keyword.dtype == numpy.float64:
        return 1
    else:
        raise RuntimeError(
            "Unsupported type {}".format(keyword.dtype))


def _get_count(keyword):
    """ get count type

    Parameters
    ----------
    keyword : Keyword

    """
    if keyword.shape == [1]:
        return 1
    elif keyword.shape == [3]:
        return 3
    else:
        raise RuntimeError("Unsupported shape: ".format(keyword.shape))
