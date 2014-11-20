from simphony.cuds.particles import Particle


class LammpsFileIoDataManager(object):
    """  Class managing Lammps data information using
        FILE-IO communications (i.e. through input and output
        files).

        Class manages data existing in Lammps in lammps
        and allows user to query and change them.

    """
    def __init__(self, lammps):
        self._lammps = lammps
        self.number_types = 3  # TODO derive from LAMMPS

        # id-to-lammps-index map
        self._id_to_index = {}

        # lammps-index-to-id map
        self._index_to_id = {}

        # cache of point data
        self._coordinates = []
        self._types = []

        # flags to keep track of current state of this
        # cache  (e.g. _invalid is True when we no longer
        # have up-to-date information; _modified is
        # is True when we changed our copy of the
        # information, i.e. we have modified the cache)
        self._invalid = True
        self._modified = False

    def get_particle(self, id):
        self._ensure_up_to_date()
        if id in self._id_to_index:
            coordinates = self._get_coordinates(id)
            p = Particle(id=id, coordinates=coordinates)
            return p
        else:
            raise KeyError("id ({}) was not found".format(id))

    def update_particle(self, particle):
        self._ensure_up_to_date()
        if particle.id in self._id_to_index:
            self._set_coordinates(particle)
        else:
            raise KeyError("id ({}) was not found".format(id))

    def add_particle(self, particle_type, particle):
        self._ensure_up_to_date()
        if particle.id not in self._id_to_index:
            return self._add_atom(particle_type, particle)
        else:
            raise KeyError(
                "particle with same id ({}) alread exists".format(id))

    def iter_id_particles(self, particle_type, ids=None):
        """Iterate over the particles of a certain type

        Parameters:

        ids : list of particle ids
            sequence of ids of particles that should be iterated over. If
            ids is None then all particles will be iterated over.

        """
        self._ensure_up_to_date()
        if ids:
            raise NotImplemented()
        else:
            for i, t in enumerate(self._types):
                if t == particle_type:
                    yield self._index_to_id[i]

    def flush(self):
        self._send_to_lammps()

    def mark_as_invalid(self):
        self._invalid = True

# Private methods #######################################################
    def _ensure_up_to_date(self):
        if self._invalid:
            self._update_from_lammps()

    def _update_from_lammps(self):

        self._id_to_index = {}
        self._index_to_id = {}
        ids = self._lammps.gather_atoms("id", 0, 1)
        for index, id_value in enumerate(ids):
            self._id_to_index[id_value] = index
            self._index_to_id[index] = id_value
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)
        self._types = self._lammps.gather_atoms("type", 0, 1)
        assert(len(self._types) == len(self._index_to_id))
        self._invalid = False

    def _send_to_lammps(self):
        if self._modified:
            self._lammps.scatter_atoms("x", 1, 3, self._coordinates)

    def _get_coordinates(self, id):
        """ Get coordinates for a particle

        """
        i = self._id_to_index[id] * 3
        coords = self._coordinates[i:i+3]
        return tuple(coords)

    def _set_coordinates(self, particle):
        """ Set coordinates for a particle

        """
        self._modified = True
        i = self._id_to_index[particle.id] * 3
        self._coordinates[i:i+3] = particle.coordinates[0:3]

    def _add_atom(self, particle_type, particle):
        """ Add a atom at point's position to lammps

        """
        self._modified = True
        coordinates = ' '.join(map(str, particle.coordinates))
        self._lammps.command(
            "create_atoms 1 single {} units box".format(coordinates))

        self.mark_as_invalid()

        # TODO  fix how id is calculated
        id = self._lammps.get_natoms()
        return id
