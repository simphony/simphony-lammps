from simphony.cuds.abstractparticles import ABCParticleContainer


class LammpsParticleContainer(ABCParticleContainer):
    """ Responsible class to synchronize operations on particles

    """
    def __init__(self, manager, uname):
        # most of the work is delegated here to this manger
        self._manager = manager

        self._uname = uname

        # holds non-approved CUBA keywords
        self.data_extension = {}

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

    # Particle methods ######################################################

    def add_particle(self, particle):
        """Add particle

        If particle has an id then this is used.  If the
        particle's id is None then a id is generated for the
        particle.

        Returns
        -------
        int
            id of particle

        Raises
        -------
        ValueError
           if an id is given which already exists.

        """
        return self._manager.add_particle(particle, self._uname)

    def update_particle(self, particle):
        """Update particle

        """
        return self._manager.update_particle(particle, self._uname)

    def get_particle(self, id):
        """Get particle

        """
        return self._manager.get_particle(id, self._uname)

    def remove_particle(self, id):
        """Remove particle

        """
        return self._manager.remove_particle(id, self._uname)

    def has_particle(self, id):
        """Has particle

        """
        return self._manager.has_particle(id, self._uname)

    def iter_particles(self, ids=None):
        """Get iterator over particles

        """
        for p in self._manager.iter_particles(self._uname, ids):
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

    def get_bond(self, id):
        """Get bond

        """
        pass

    def remove_bond(self, id):
        """Remove bond

        """
        pass

    def has_bond(self, id):
        """Has bond

        """

    def iter_bonds(self, ids=None):
        """Get iterator over bonds

        """
        pass
