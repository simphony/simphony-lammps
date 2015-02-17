""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simlammps.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.lammps_process import LammpsProcess
from simlammps.config.pair_style import PairStyle
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
        self._check_configuration()

        pair_style = PairStyle(self.SP)

        # before running, we flush any changes to lammps
        # and mark our data manager (cache of particles)
        # as being invalid
        self._data_manager.flush()
        self._data_manager.mark_as_invalid()

        commands = ScriptWriter.get_configuration(
            data_file=self._data_filename,
            number_steps=self.CM[CUBA.NUMBER_OF_TIME_STEPS],
            time_step=self.CM[CUBA.TIME_STEP],
            pair_style=pair_style.get_global_config(),
            pair_coeff=pair_style.get_pair_coeffs())
        lammps = LammpsProcess()
        lammps.run(commands)

    def _check_configuration(self):
        """ Check if everything is configured correctly

        """

        cm_requirements = [CUBA.NUMBER_OF_TIME_STEPS,
                           CUBA.TIME_STEP]

        missing = [str(req) for req in cm_requirements
                   if req not in self.CM.keys()]

        msg = ""
        if missing:
            msg = "Problem with CM component. "
            msg += "Missing: " + ', '.join(missing)

        # TODO check SP, BC

        if msg:
            # TODO throw unique exception that
            # users can catch and then try to fix
            # their configuration
            raise Exception(msg)
