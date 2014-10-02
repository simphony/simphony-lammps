from simphony.cuds.particle import Particle


class LammpsParticleManager(object):
    """  Class holding Lammps particle information

        Class keeps track of what particles exists
        in the lamp world and allows user to query
        and change them.

    """
    def __init__(self, lammps):
        self._lammps = lammps
        self.dimension = 2  # TODO derive from LAMMPS
        self.number_types = 3  # TODO derive from LAMMPS

    def update(self):
        # id-to-index map
        self._id_to_index = {}

        # index-to-id map
        self._index_to_id = {}

        ids = self._lammps.gather_atoms("id", 0, 1)
        for index, id_value in enumerate(ids):
            self._id_to_index[id_value] = index
            self._index_to_id[index] = id_value
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)
        self._types = self._lammps.gather_atoms("type", 0, 1)
        assert(len(self._types) == len(self._index_to_id))
        self._up_to_date = True

    def get_particle(self, id):
        self._ensure_up_to_date()
        if id in self._id_to_index:
            coordinates = self._get_coordinates(id)
            p = Particle(id=id, coordinates=coordinates)
            return p
        else:
            raise KeyError("id ({}) was not found".format(id))

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
        self._up_to_date = False

# Private methods #######################################################
    def _ensure_up_to_date(self):
        if not self._up_to_date:
            self.update()

    def _get_coordinates(self, id):
        """ Get coordintes for a point

        Always return a 3-dimenional coordinates

        """
        i = self._id_to_index[id] * self.dimension
        coords = [0.0] * 3
        coords[0:self.dimension] = self._coordinates[i:i+self.dimension]
        return coords
