from simphony.cuds.abstractparticles import ABCParticles


class LammpsParticles(ABCParticles):
    """ Responsible class to synchronize operations on particles

    Attributes
    ----------
    name : string
        name of particles
    data : DataContainer
        holds data
    data_extension : dict
        holds non-approved CUBA keywords

    """
    def __init__(self, manager, uname):
        # most of the work is delegated here to this manger
        self._manager = manager
        self._uname = uname

    @property
    def name(self):
        return self._manager.get_name(self._uname)

    @name.setter
    def name(self, value):
        self._manager.rename(self._uname, value)

    @property
    def data(self):
        return self._manager.get_data(self._uname)

    @data.setter
    def data(self, value):
        self._manager.set_data(value, self._uname)

    @property
    def data_extension(self):
        return self._manager.get_data_extension(self._uname)

    @data_extension.setter
    def data_extension(self, value):
        self._manager.set_data_extension(value, self._uname)

    # Particle methods ######################################################

    def add_particle(self, particle):
        """Add particle

        If particle has an uid then this is used.  If the
        particle's uid is None then a uid is generated for the
        particle.

        Returns
        -------
        int
            uid of particle

        Raises
        -------
        ValueError
           if an uid is given which already exists.

        """
        return self._manager.add_particle(particle, self._uname)

    def update_particle(self, particle):
        """Update particle

        """
        return self._manager.update_particle(particle, self._uname)

    def get_particle(self, uid):
        """Get particle

        """
        return self._manager.get_particle(uid, self._uname)

    def remove_particle(self, uid):
        """Remove particle

        """
        return self._manager.remove_particle(uid, self._uname)

    def has_particle(self, uid):
        """Has particle

        """
        return self._manager.has_particle(uid, self._uname)

    def iter_particles(self, uids=None):
        """Get iterator over particles

        """
        for p in self._manager.iter_particles(self._uname, uids):
            yield p

    # Bond methods #######################################################

    def add_bond(self, bond):
        """Add bond

        """
        pass

    def update_bond(self, bond):
        """Update particle

        """
        pass

    def get_bond(self, uid):
        """Get bond

        """
        pass

    def remove_bond(self, uid):
        """Remove bond

        """
        pass

    def has_bond(self, uid):
        """Has bond

        """

    def iter_bonds(self, uids=None):
        """Get iterator over bonds

        """
        pass
