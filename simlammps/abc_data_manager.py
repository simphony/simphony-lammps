import uuid
import abc

from simlammps.lammps_particles import LammpsParticles


class ABCDataManager(object):
    """  Class managing Lammps data information

    The class performs communicating the data to and from lammps. The
    class manages data existing in Lammps and allows this data to be
    queried and to be changed.

    Class maintains and provides LammpsParticles (which implements
    the ABCParticles class).  The queries and changes to LammpsParticles
    occurs through the many abstract methods in this class.  See subclasses
    to understand how the communication occurs.


    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        # map from name to unique name
        self._unames = {}

        # map from unique name to names
        self._names = {}

        # dictionary of lammps_particle
        # where the the key is the unique name
        self._lpcs = {}

    def get_name(self, uname):
        """
        Get the name of a particle container

        Parameters
        ----------
        uname : string
            unique name of particle container

        Returns
        -------
        string
            name of particle container

        """
        return self._names[uname]

    def rename(self, uname, new_name):
        """ Rename a particle container

        Parameters
        ---------
        uname :
            unique name of particle container to be renamed
        new_name :
            new name of the particle container

        """
        del self._unames[self._names[uname]]
        self._unames[new_name] = uname
        self._names[uname] = new_name

    def __iter__(self):
        """ Iter over names of particle containers

        """
        for name in self._unames:
            yield name

    def __contains__(self, name):
        """ Checks if particle container with this name exists

        """
        return name in self._unames

    def __getitem__(self, name):
        """ Returns particle container with this name

        """
        return self._lpcs[self._unames[name]]

    def __delitem__(self, name):
        """Deletes lammps particle container and associated cache

        """
        self._handle_delete_particles(self._unames[name])
        del self._lpcs[self._unames[name]]
        del self._unames[name]

    def new_particles(self, particles):
        """Add new particle container to this manager.

        Parameters
        ----------
        particles : ABCParticles
            particle container to be added

        Returns
        -------
        LammpsParticles

        """

        # generate a unique name for this particle container
        # that will not change over the lifetime of the wrapper.
        uname = uuid.uuid4()

        self._unames[particles.name] = uname
        self._names[uname] = particles.name

        lammps_pc = LammpsParticles(self, uname)
        self._lpcs[uname] = lammps_pc

        self._handle_new_particles(uname, particles)
        return lammps_pc

    @abc.abstractmethod
    def _handle_delete_particles(self, uname):
        """Handle when a Particles is deleted

        Parameters
        ----------
        uname : string
            non-changing unique name of particles to be deleted

        """

    @abc.abstractmethod
    def _handle_new_particles(self, uname, particles):
        """Handle when new particles are added

        Parameters
        ----------
        uname : string
            non-changing unique name associated with particles to be added

        particles : ABCParticles
            particle container to be added

        """

    @abc.abstractmethod
    def get_data(self, uname):
        """Returns data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def set_data(self, data, uname):
        """Sets data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
    @abc.abstractmethod
    def get_data_extension(self, uname):
        """Returns extension data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def set_data_extension(self, data, uname):
        """Sets extension data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def get_particle(self, uid, uname):
        """Get particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def update_particles(self, iterable, uname):
        """Update particle

        Parameters
        ----------
        iterable : iterable of Particle objects
            the particles that will be updated.
        uname : string
            non-changing unique name of particles

        Raises
        ------
        ValueError :
            If any particle inside the iterable does not exist.

        """

    @abc.abstractmethod
    def add_particles(self, iterable, uname):
        """Add particles

        Parameters
        ----------
        iterable : iterable of Particle objects
            the particles that will be added.
        uname : string
            non-changing unique name of particles

        ValueError :
            when there is a particle with an uids that already exists
            in the container.

        """

    @abc.abstractmethod
    def remove_particle(self, uid, uname):
        """Remove particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def has_particle(self, uid, uname):
        """Has particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """

    @abc.abstractmethod
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

    @abc.abstractmethod
    def number_of_particles(self, uname):
        """Get number of particles in a container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """

    @abc.abstractmethod
    def flush(self, input_data_filename=None):
        """flush to file

        Parameters
        ----------
        input_data_filename : string, optional
            name of data-file where inform is written to (i.e lammps's input).
        """

    @abc.abstractmethod
    def read(self, output_data_filename=None):
        """read from file

        Parameters
        ----------
        output_data_filename : string, optional
            name of data-file where info read from (i.e lammps's output).
        """
