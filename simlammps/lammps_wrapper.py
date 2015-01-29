""" LAMMPS SimPhoNy Wrapper

This module provides a wrapper to LAMMPS-md
"""
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simlammps.lammps_particle_container import LammpsParticleContainer
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

        self._particle_containers = {}

        self.BC = DataContainer()
        self.CM = DataContainer()
        self.SP = DataContainer()

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
        if name in self._particle_containers:
            raise ValueError(
                'Particle container \'{n}\` already exists'.format(n=name))
        else:
            pc = LammpsParticleContainer(self._data_manager, name)
            # TODO improve
            self._data_manager.new_particle_container(name)
            self._particle_containers[name] = pc

            if particle_container:
                pc.data = DataContainer(particle_container.data)
                for p in particle_container.iter_particles():
                    pc.add_particle(p)
            return self._particle_containers[name]

    def get_particle_container(self, name):
        """Get particle container.

        The returned particle container can be used to query
        and change the related data inside LAMMPS.

        Parameters
        ----------
        name : str
            name of particle container to return
        """
        if name in self._particle_containers:
            return self._particle_containers[name]
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
        if name in self._particle_containers:
            pc = self._particle_containers[name]
            all_ids = list(p.id for p in pc.iter_particles())
            for pid in all_ids:
                pc.remove_particle(pid)

            del self._particle_containers[name]
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
            for name, pc in self._particle_containers.iteritems():
                yield name, pc
        else:
            for name in names:
                yield name, self._particle_containers.get(name)

    def run(self):
        """ Run for based on configuration

        """
        self._check_configuration()

        pair_style = PairStyle(self.CM)

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
