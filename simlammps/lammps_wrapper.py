""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""
from simphony.core.data_container import DataContainer

from simlammps.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.lammps_process import LammpsProcess
from simlammps.config.script_writer import ScriptWriter


class LammpsWrapper(object):
    """ Wrapper to LAMMPS-md

    """
    def __init__(self):
        self._data_filename = "data.lammps"
        self._data_manager = LammpsFileIoDataManager(
            data_filename=self._data_filename)

        self.BC = DataContainer()
        self.CM = DataContainer()
        self.SP = DataContainer()

    def add_particle_container(self, particle_container):
        """Add particle container.

        Parameters
        ----------
        particle_container : ABCParticleContainer
            particle container to be added.

        Returns
        ----------
        ABCParticleContainer
            The particle container newly added to Lammps.  See
            get_particle_container for more information.

        """
        if particle_container.name in self._data_manager:
            raise ValueError(
                'Particle container \'{n}\` already exists'.format(
                    n=particle_container.name))
        else:
            return self._data_manager.new_particle_container(
                particle_container)

    def get_particle_container(self, name):
        """Get particle container.

        The returned particle container can be used to query
        and change the related data inside LAMMPS.

        Parameters
        ----------
        name : str
            name of particle container to return
        """
        if name in self._data_manager:
            return self._data_manager[name]
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
        if name in self._data_manager:
            del self._data_manager[name]
        else:
            raise ValueError(
                'Particle container \'{n}\` does not exist'.format(n=name))

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
            for name in self._data_manager:
                yield self._data_manager[name]
        else:
            for name in names:
                if name in self._data_manager:
                    yield self._data_manager[name]
                else:
                    raise ValueError(
                        'Particle container \'{n}\` does not exist'.format(
                            n=name))

    def run(self):
        """ Run for based on configuration

        """

        # before running, we flush any changes to lammps
        # and mark our data manager (cache of particles)
        # as being invalid
        self._data_manager.flush()
        self._data_manager.mark_as_invalid()

        commands = ScriptWriter.get_configuration(
            self._data_filename,
            self.BC,
            self.CM,
            self.SP)
        lammps = LammpsProcess()
        lammps.run(commands)
