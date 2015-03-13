""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""
import contextlib
import os
import tempfile
import shutil

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.core.data_container import DataContainer

from simlammps.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.lammps_process import LammpsProcess
from simlammps.config.script_writer import ScriptWriter


@contextlib.contextmanager
def _temp_directory():
    """ context manager that provides temp directory

    The name of the created temp directory is returned when context is entered
    and this directory is deleted when context is exited
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class LammpsWrapper(ABCModelingEngine):
    """ Wrapper to LAMMPS-md

    """
    def __init__(self):
        self._data_manager = LammpsFileIoDataManager()

        self.BC = DataContainer()
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.CM_extension = {}
        self.SP_extension = {}
        self.BC_extension = {}

    def add_particles(self, particles):
        """Add particles.

        Parameters
        ----------
        particles : ABCParticles
            particles to be added.

        Returns
        ----------
        ABCParticles
            The particles newly added to Lammps.  See
            get_particles for more information.

        """
        if particles.name in self._data_manager:
            raise ValueError(
                'Particle container \'{n}\` already exists'.format(
                    n=particles.name))
        else:
            return self._data_manager.new_particles(
                particles)

    def get_particles(self, name):
        """Get particles

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

    def delete_particles(self, name):
        """Delete particles

        Parameters
        ----------
        name : str
            name of particles to delete
        """
        if name in self._data_manager:
            del self._data_manager[name]
        else:
            raise KeyError(
                'Particles \'{n}\` does not exist'.format(n=name))

    def iter_particles(self, names=None):
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
        """ Run lammps-engine based on configuration and data

        """
        with _temp_directory() as temp_dir:
            input_data_filename = os.path.join(temp_dir, "data_in.lammps")
            output_data_filename = os.path.join(temp_dir, "data_out.lammps")

            # before running, we flush any changes to lammps
            self._data_manager.flush(input_data_filename)

            commands = ScriptWriter.get_configuration(
                input_data_file=input_data_filename,
                output_data_file=output_data_filename,
                BC=_combine(self.BC, self.BC_extension),
                CM=_combine(self.CM, self.CM_extension),
                SP=_combine(self.SP, self.SP_extension))
            lammps = LammpsProcess(log_directory=temp_dir)
            lammps.run(commands)

            # after running, we read any changes from lammps
            self._data_manager.read(output_data_filename)

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
