import uuid
import ctypes

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particle

from simlammps.config.domain import get_box
from simlammps.internal.particle_data_cache import ParticleDataCache
from simlammps.abc_data_manager import ABCDataManager
from simlammps.cuba_extension import CUBAExtension


class _IDGenerator(object):
    """Class keeps track of what is next LAMMPS id

    TODO provide ids that can be reused (i.e. become available
     after deletions) or complains when we have used too many..

    """
    def __init__(self):
        self._next_id = 0

    def get_new_id(self):
        """ returns next lammps-id
        """
        self._next_id += 1
        return self._next_id


class LammpsInternalDataManager(ABCDataManager):
    """  Class managing LAMMPS data information using file-io

    The class performs communicating the data to and from LAMMPS using FILE-IO
    communications (i.e. through input and output files). The class manages
    data existing in LAMMPS (via LAMMPS data file) and allows this data to be
    queried and to be changed.

    Class maintains a cache of the particle information.  This information
    is read from file whenever the read() method is called and written to
    the file whenever the flush() method is called.

    Parameters
    ----------
    lammps :
        lammps python wrapper
    """
    def __init__(self, lammps):
        super(LammpsInternalDataManager, self).__init__()

        self._lammps = lammps

        # TODO remove
        self._lammps.command("dimension 3")
        self._lammps.command("boundary p s p")
        self._lammps.command("atom_style atomic")

        # TODO This is a hack as due to pc.data_extension
        # being empty at this point
        vectors = [(25.0, 0.0, 0.0),
                   (0.0, 22.0, 0.0),
                   (0.0, 0.0, 1.0)]
        dummy_data = {}
        dummy_data[CUBAExtension.BOX_VECTORS] = vectors
        dummy_data[CUBAExtension.BOX_ORIGIN] = (0.0, 0.0, 0.0)
        self._lammps.command(get_box([dummy_data], command_format=True))
        types = 3
        self._lammps.command("create_box {} box".format(types))

        self._id_generator = _IDGenerator()

        # map from lammps-id to simphony-uid
        # (note lammps-id is also the index)
        self._lammpsid_to_uid = {}

        # map from simphony-uid (with uname) to lammps-id
        self._uid_to_lammpsid = {}

        # map from lammpsid to index location of data
        self._lammpsid_to_index = {}

        # cache of point data
        self._coordinates = []
        self._particle_data_cache = ParticleDataCache(lammps=self._lammps)

        # cache of particle containers's data
        self._pc_data = {}
        self._pc_data_extension = {}

        self._dummy_box = None

    def get_data(self, uname):
        """Returns data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return self._pc_data[uname]

    def set_data(self, data, uname):
        """Sets data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._pc_data[uname] = data

    def get_data_extension(self, uname):
        """Returns data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return self._pc_data_extension[uname]

    def set_data_extension(self, data, uname):
        """Sets data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._pc_data_extension[uname] = data

    def _handle_delete_particles(self, uname):
        """Handle when a Particles is deleted

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        del self._pc_data[uname]
        del self._pc_data_extension[uname]

        # TODO delete id->uid info
        del self._uid_to_lammpsid[uname]

    def _handle_new_particles(self, uname, particles):
        """Add new particle container to this manager.


        Parameters
        ----------
        uname : string
            non-changing unique name of particles
        particles : ABCParticles
            particle container to be added

        """
        # create empty stand-alone particle container
        # to use as a cache of for input/output to LAMMPS

        self._uid_to_lammpsid[uname] = {}

        self._pc_data[uname] = DataContainer(particles.data)
        self._pc_data_extension[uname] = {}

        # This is a hack as due to pc.data_extension
        # being empty at this point
        vectors = [(25.0, 0.0, 0.0),
                   (0.0, 22.0, 0.0),
                   (0.0, 0.0, 1.0)]
        self._pc_data_extension[uname][CUBAExtension.BOX_VECTORS] = vectors
        self._pc_data_extension[uname][CUBAExtension.BOX_ORIGIN] = (0.0,
                                                                    0.0,
                                                                    0.0)

        # self._update_simulation_box()

        # TODO have uniform way to check what is needed
        # and perform a check at a different spot.
        if CUBA.MATERIAL_TYPE not in self._pc_data[uname]:
            raise ValueError("Missing the required CUBA.MATERIAL_TYPE")

        # add each item
        for p in particles.iter_particles():
            self._add_atom(p, uname)

        # TODO bonds

    def _update_simulation_box(self):
        """Update simulation box


        """
        # TODO remove this hack. here we only set the simulation box
        # once as we don't support it being changed.
        if self._dummy_box:
            # delete old box
            self._lammps.command("region delete box")
        box = get_box([de for _, de in self._pc_data_extension.iteritems()],
                      command_format=True)

        if box != self._dummy_box:
            # we update our region and then
            # update the simulation box if
            # the dimensions have changed
            self._lammps.command(box)

            # TODO
            types = set()
            for _, data in self._pc_data.iteritems():
                types.add(data[CUBA.MATERIAL_TYPE])
            self._lammps.command("create_box {} box".format(len(types)))
            self.dummy_box = box

    def get_particle(self, uid, uname):
        """Get particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        if uid in self._uid_to_lammpsid[uname]:
            index = self._lammpsid_to_index[self._uid_to_lammpsid[uname][uid]]
            coordinates = self._get_coordinates(index)
            data = self._particle_data_cache.get_particle_data(index)

            # TODO removing type from data as it not kept as a per-particle
            # data but currently it is on the container.
            # In lammps it is only stored as a per-atom based attribute.
            # This should be changed once #9 issue is addressed
            del data[CUBA.MATERIAL_TYPE]

            p = Particle(uid=uid,
                         coordinates=coordinates,
                         data=data)
            return p
        else:
            raise KeyError("uid ({}) was not found".format(uid))

    def update_particle(self, particle, uname):
        """Update particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """
        if particle.uid in self._uid_to_lammpsid[uname]:
            self._set_particle(particle, uname)
        else:
            raise ValueError(
                "particle id ({}) was not found".format(particle.uid))

    def add_particle(self, particle, uname):
        """Add particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """
        if particle.uid not in self._uid_to_lammpsid[uname]:
            self._add_atom(particle, uname)
            return particle.uid
        else:
            raise ValueError(
                "particle with same uid ({}) alread exists".format(
                    particle.uid))

    def remove_particle(self, uid, uname):
        """Remove particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """
        raise NotImplementedError()

    def has_particle(self, uid, uname):
        """Has particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """
        return uid in self._uid_to_lammpsid[uname]

    def iter_particles(self, uname, uids=None):
        """Iterate over the particles of a certain type

        Parameters
        ----------
        uids : list of particle uids
            sequence of uids of particles that should be iterated over. If
            uids is None then all particles will be iterated over.
        uname : string
            non-changing unique name of particles

        """
        if uids:
            for uid in uids:
                yield self.get_particle(uid, uname)
        else:
            for uid in self._uid_to_lammpsid[uname].iterkeys():
                yield self.get_particle(uid, uname)

    def read(self, output_data_filename):
        """read from file

        Parameters
        ----------
        output_data_filename :
            name of data-file where info read from (i.e lammps's output).
        """
        self._update_from_lammps()

    def flush(self):
        """flush to file

        """
        if self._pc_data:
            self._send_to_lammps()
        else:
            raise RuntimeError(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when there are no particle containers
        # or when some of them do not contain any particles
        # (i.e. someone has deleted all the particles)

    def _update_from_lammps(self):
        self._coordinates = self._lammps.gather_atoms("x", 1, 3)

        self._particle_data_cache.retrieve()

        self._invalid = False

    def _send_to_lammps(self):
        coords = (ctypes.c_float * len(self._coordinates))(*self._coordinates)
        self._lammps.scatter_atoms("x", 1, 3, coords)

        # send particle data (i.e. type, velocity)
        self._particle_data_cache.send()

        # todo send mass (for each type)

    def _get_coordinates(self, index):
        """ Get coordinates for a particle

        Parameters
        ----------
        index : int
            index location of particle in array
        """
        i = index * 3
        coords = self._coordinates[i:i+3]
        return tuple(coords)

    def _set_particle(self, particle, uname):
        """ Set coordinates and data for a particle

        Parameters
        ----------
        particle : Particle
            particle to be set
        uname : string
            non-changing unique name of particle container

        """

        # TODO have arguments as particle and index
        lammpsid = self._uid_to_lammpsid[uname][particle.uid]
        index = self._lammpsid_to_index[lammpsid]
        i = index * 3
        self._coordinates[i:i+3] = particle.coordinates[0:3]

        # TODO using type from container.  in lammps it is only
        # stored as a per-atom based attribute.
        # this should be changed once #9 issue is addressed
        p_type = self._pc_data[uname][CUBA.MATERIAL_TYPE]
        data = DataContainer(particle.data)
        data[CUBA.MATERIAL_TYPE] = p_type

        self._particle_data_cache.set_particle_data(data,
                                                    index)

    def _add_atom(self, particle, uname):
        """ Add a atom at point's position to lammps

        If particle has uid equal to NONE, we will give
        it an uuid

        Parameters
        ----------
        particle : Particle
            particle with CUBA.MATERIAL_TYPE

        Returns
        -------
        int :
            lammps-id of added atom

        """
        if particle.coordinates[2] > 100:
            raise RuntimeError(
                "{} coordinates are incorrect".format(particle.coordinates))
        coordinates = ' '.join(map(str, particle.coordinates))

        p_type = self._pc_data[uname][CUBA.MATERIAL_TYPE]

        self._lammps.command(
            "create_atoms {} single {} units box".format(p_type, coordinates))

        if particle.uid is None:
            particle.uid = uuid.uuid4()

        lammps_id = self._id_generator.get_new_id()

        self._lammpsid_to_uid[lammps_id] = particle.uid
        self._uid_to_lammpsid[uname][particle.uid] = lammps_id
        self._lammpsid_to_index[lammps_id] = len(self._lammpsid_to_uid) - 1
        # TODO we probably do not need both lammpsid and index as in the
        # case of the INTERNAL wrapper, the values are ordered by
        # lammps-ids (1..N) so what the index is clear when one has
        # the lammps id.  Need to evaluate this once we support
        # the deletion of particles

        self._set_particle(particle, uname)

        return particle.uid
