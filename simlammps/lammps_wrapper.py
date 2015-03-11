""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.core.data_container import DataContainer

from simlammps.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.lammps_process import LammpsProcess
from simlammps.config.script_writer import ScriptWriter


class LammpsWrapper(ABCModelingEngine):
    """ Wrapper to LAMMPS-md

    """
    def __init__(self):
        self._input_data_filename = "data_in.lammps"
        self._output_data_filename = "data_out.lammps"
        self._data_manager = LammpsFileIoDataManager(
            input_data_filename=self._input_data_filename,
            output_data_filename=self._output_data_filename)

        self.BC = DataContainer()
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.CM_extension = {}
        self.SP_extension = {}
        self.BC_extension = {}

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
            raise KeyError(
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
            raise KeyError(
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
                    raise KeyError(
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
            input_data_file=self._input_data_filename,
            output_data_file=self._output_data_filename,
            BC=_combine(self.BC, self.BC_extension),
            CM=_combine(self.CM, self.CM_extension),
            SP=_combine(self.SP, self.SP_extension))
        lammps = LammpsProcess()
        lammps.run(commands)

    def add_lattice(self, lattice):
        raise NotImplementedError()

    def add_mesh(self, mesh):
        raise NotImplementedError()

    def delete_lattice(self, name):
        raise NotImplementedError()

    def delete_mesh(self, name):
        raise NotImplementedError()

    def get_lattice(self, name):
        raise NotImplementedError()

    def get_mesh(self, name):
        raise NotImplementedError()

    def iter_lattices(self, names=None):
        raise NotImplementedError()

    def iter_meshes(self, names=None):
        raise NotImplementedError()


def _combine(data_container, data_container_extension):
    """ Combine a the approved CUBA with non-approved CUBA key-values

    Parameters
    ----------
    data_container : DataContainer
        data container with CUBA attributes
    data_container_extension : dict
        data container with non-approved CUBA attributes

    Returns
    ----------
    dict
        dictionary containing the approved adn non-approved
        CUBA key-values

    """
    result = dict(data_container_extension)
    result.update(data_container)
    return result
