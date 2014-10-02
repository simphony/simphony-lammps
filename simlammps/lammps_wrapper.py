""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""

import lammps

from simlammps.particle_container import ParticleContainer
from simlammps.lammps_particle_manager import LammpsParticleManager


class LammpsWrapper(object):
    """ Wrapper to LAMMPS-md

    """
    def __init__(self):
        self._lammps = lammps.lammps()
        self._particle_manager = LammpsParticleManager(self._lammps)
        self._particle_containers = {}
        self._nsteps = 10  # TODO

        # TODO
        for i in xrange(self._particle_manager.number_types):
            pc = ParticleContainer(self._particle_manager, i+1)
            self._particle_containers[str(i+1)] = pc

    def add_particle_container(self, name, particle_container=None):
        """Add particle container.

        Parameters
        ----------
        name : str
            name of particle container
        particle_container : ABCParticleContainer, optional
            particle container to be added. If none is give,
            then an empty particle container is added.

        Returns
        ----------
        ABCParticleContainer
            The particle container newly added to Lammps.  See
            get_particle_container for more information.

        """
        pass

    def get_particle_container(self, name):
        """Get particle container.

        The returned particle container can be used to query
        and change the related data inside LAMMPS.

        Parameters
        ----------
        name : str
            name of particle container to return
        """
        if name not in self._particle_containers:
            return self._particles_containers[name]
        else:
            raise ValueError(
                'Particle container \'{}\` does not exist'.format(name))

    def delete_particle_container(self, name):
        """Delete particle container.

        Parameters
        ----------
        name : str
            name of particle container to delete
        """
        pass

    def iter_particle_containers(self, names=None):
        """Returns an iterator over a subset or all
        of the particle containers. The iterator iterator yields
        (name, particlecontainer) tuples for each particle container.

        Parameters
        ----------
        names : list of str
            names of specific particle containers to be iterated over.
            If names is not given, then all particle containers will
            be iterated over.

        """
        if names is None:
            for name, pc in self._particle_containers.iteritems():
                yield name, pc
        else:
            for name, pc in names:
                yield name, self._particle_container.get(name)

    def _flush(self):
        """ Write any changes to lammps

        """
        self._particle_manager.flush()

    def run(self):
        """ Run for a specific amount of time

        """
        self._flush()
        run_command = 'run {}'.format(self._nsteps)
        self._lammps.command(run_command)
