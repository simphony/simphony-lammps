""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""

import lammps

from enum import Enum

from simlammps.particle_container import ParticleContainer
from simlammps.lammps_internal_data_manager import LammpsInternalDataManager
from simlammps.lammps_fileio_data_manager import LammpsFileIoDataManager


class WrapperControlType(Enum):
    FILEIO = 1
    INTERNAL = 2


class LammpsWrapper(object):
    """ Wrapper to LAMMPS-md

    """
    def __init__(self, control=WrapperControlType.FILEIO):
        self._lammps = lammps.lammps(cmdargs=["-screen", "none"])

        if control == WrapperControlType.FILEIO:
            self._data_manager = LammpsFileIoDataManager(self._lammps)
        else:
            self._data_manager = LammpsInternalDataManager(self._lammps)

        self._particle_containers = {}
        self._nsteps = 10  # TODO

        # TODO
        for i in xrange(self._data_manager.number_types):
            pc = ParticleContainer(self._data_manager, i+1)
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
        self._data_manager.flush()

    def _mark_as_invalid(self):
        """ Mark as being invalid

        """
        self._data_manager.mark_as_invalid()

    def _write_restart_file(self, file_name="restart.lammps"):
        """ Dump atoms to file

        """
        self._lammps.command("write_restart {}".format(file_name))

    def run(self):
        """ Run for a specific amount of steps

        """
        # before running, we flush any changes to lammps
        # and mark are cache info as being invalid
        self._flush()
        self._mark_as_invalid()

        run_command = 'run {}'.format(self._nsteps)
        self._lammps.command(run_command)
