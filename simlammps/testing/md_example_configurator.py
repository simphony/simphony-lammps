import random

from simphony.cuds.particles import Particle, Particles
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from simlammps.cuba_extension import CUBAExtension


class MDExampleConfigurator:
    """  MD Example configuration

    Class provides an example configuration for a
    lammps molecular dynamic engine

    """

    @staticmethod
    def set_configuration(wrapper):
        """ Configure example engine with example settings

        The wrapper is configured with required CM, SP, BC parameters

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """

        # CM
        wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = 10000
        wrapper.CM[CUBA.TIME_STEP] = 0.003
        wrapper.CM_extension[CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"

        # SP
        pair_potential = ("lj:\n"
                          "  global_cutoff: 1.12246\n"
                          "  parameters:\n"
                          "  - pair: [1, 1]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [1, 2]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [1, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [2, 2]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [2, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [3, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.0001\n")
        wrapper.SP_extension[CUBAExtension.PAIR_POTENTIALS] = pair_potential

        # BC
        wrapper.BC_extension[CUBAExtension.BOX_FACES] = (
            "periodic", "periodic", "periodic")

    @staticmethod
    def configure_wrapper(wrapper):
        """ Configure example wrapper with example settings and particles

        The wrapper is configured with required CM, SP, BC parameters
        and is given particles (see add_particles)

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        # configure
        MDExampleConfigurator.set_configuration(wrapper)

        # add particle containers
        MDExampleConfigurator.add_particles(wrapper)

    @staticmethod
    def add_particles(wrapper):
        """ Add containers of particles to wrapper

        The wrapper is configured with containers of particles that contain
        mass, type/materialtype, and velocity.  They correspond to
        the configuration performed in configure_wrapper method

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        for i in range(1, 4):
            pc = Particles(name="foo{}".format(i))

            random.seed(42)
            for _ in range(10):
                coord = (random.uniform(0.0, 25.0),
                         random.uniform(0.0, 22.0),
                         0.0)
                p = Particle(coordinates=coord)
                p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
                pc.add_particle(p)

            MDExampleConfigurator.add_configure_particles(wrapper,
                                                          pc,
                                                          mass=i,
                                                          material_type=i)

    @staticmethod
    def add_configure_particles(wrapper, pc, mass=1, material_type=1):
        """ Add containers of particles to wrapper and  configure it properly.

        The wrapper is configured with containers of particles that contain
        mass, type/materialtype, and velocity.  They correspond to
        the configuration performed in configure_wrapper method

        Parameters
        ----------
        wrapper : ABCModelingEngine
            wrapper
        pc : Particles
            particle container to be added and configured
        mass : int
            mass of particles
        material : int, optional
            material type of particles
        """
        data = DataContainer()
        data[CUBA.MASS] = mass
        data[CUBA.MATERIAL_TYPE] = material_type

        pc.data = data

        pc_w = wrapper.add_particles(pc)

        # TODO this should be a class variable
        vectors = [(25.0, 0.0, 0.0),
                   (0.0, 22.0, 0.0),
                   (0.0, 0.0, 1.0)]

        pc_w.data_extension = {CUBAExtension.BOX_VECTORS: vectors,
                               CUBAExtension.BOX_ORIGIN: (0.0, 0.0, 0.0)}
        return pc_w
