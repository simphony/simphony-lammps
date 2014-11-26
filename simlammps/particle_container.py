import numpy

from simphony.cuds.abstractparticles import ABCParticleContainer

MAX_INT = numpy.iinfo(numpy.uint32).max


class ParticleContainer(ABCParticleContainer):
    """
    Responsible class to synchronize operations on particles

    """
    def __init__(self, manager, particle_type):
        self._manager = manager
        self._particle_type = particle_type

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
        return self._manager.add_particle(self._particle_type, particle)

    def update_particle(self, particle):
        """Update particle

        """
        return self._manager.update_particle(particle)

    def get_particle(self, id):
        """Get particle

        """
        return self._manager.get_particle(id)

    def remove_particle(self, id):
        """Remove particle

        """
        return self._manager.remove_particle(id)

    def has_particle(self, id):
        """Has particle

        """
        pass

    def iter_particles(self, ids=None):
        """Get iterator over particles

        """
        for p in self._manager.iter_id_particles(
                particle_type=self._particle_type, ids=ids):
            yield p

    # Bond methods #######################################################

    def add_bond(self, bond):
        """Add bond

        If bond has an id then this is used.  If the
        bond's id is None then a id is generated for the
        bond.

        Returns
        -------
        int
            id of bond

        Raises
        -------
        ValueError
           if an id is given which already exists.

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
