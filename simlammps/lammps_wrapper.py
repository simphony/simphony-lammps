""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper for  LAMMPS-md
"""
import contextlib
import os
import tempfile
import shutil

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.core.data_container import DataContainer

from simlammps.io.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.io.lammps_process import LammpsProcess
from simlammps.internal.lammps_internal_data_manager import (
    LammpsInternalDataManager)
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
    def __init__(self, use_internal_interface=False):
        """ Constructor.

        Parameters
        ----------
        use_internal_interface : bool, optional
            If true, then the internal interface (library) is used when
            communicating with LAMMPS, if false, then file-io interface is
            used where input/output files are used to communicate with LAMMPS

        """

        self._use_internal_interface = use_internal_interface

        if self._use_internal_interface:
            # TODO
            import lammps
            self._lammps = lammps.lammps(cmdargs=["-screen", "none"])
            self._data_manager = LammpsInternalDataManager(self._lammps)
        else:
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

        if self._use_internal_interface:
            # before running, we flush any changes to lammps
            self._data_manager.flush()

            # TODO this has to be rewritten as
            # we only want to send configuration commands
            # once (or after they change) but the 'run'
            # command each time
            commands = ""

            commands += ScriptWriter.get_pair_style(
                _combine(self.SP, self.SP_extension))
            commands += ScriptWriter.get_fix(CM=_combine(self.CM,
                                                         self.CM_extension))
            commands += ScriptWriter.get_pair_coeff(
                _combine(self.SP, self.SP_extension))
            commands += ScriptWriter.get_run(CM=_combine(self.CM,
                                                         self.CM_extension))

            for command in commands.splitlines():
                self._lammps.command(command)

            # after running, we read any changes from lammps
            # TODO rework
            self._data_manager.read()
        else:
            with _temp_directory() as temp_dir:
                input_data_filename = os.path.join(
                    temp_dir, "data_in.lammps")
                output_data_filename = os.path.join(
                    temp_dir, "data_out.lammps")

                # before running, we flush any changes to lammps
                self._data_manager.flush(input_data_filename)

                commands = ScriptWriter.get_configuration(
                    input_data_file=input_data_filename,
                    output_data_file=output_data_filename,
                    BC=_combine(self.BC, self.BC_extension),
                    CM=_combine(self.CM, self.CM_extension),
                    SP=_combine(self.SP, self.SP_extension))
                lammps_process = LammpsProcess(log_directory=temp_dir)
                lammps_process.run(commands)

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
