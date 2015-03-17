import random

from simphony.cuds.particles import Particle, Particles
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from simlammps.cuba_extension import CUBAExtension


class ExampleConfigurator:
    """  Example configuration

    Class provides an example configuration for a
    lammps wrapper

    """

    @staticmethod
    def set_configuration(wrapper):
        """ Configure example wrapper with example settings

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
        ExampleConfigurator.set_configuration(wrapper)

        # add particle containers
        ExampleConfigurator.add_particles(wrapper)

    @staticmethod
    def add_particles(wrapper):
        """ Add containers of particles to wrapper

        The wrapper is configured with containers of particles that contain
        mass, type/materialtype, and velocitiy.  They correspond to
        the configuration performed in configure_wrapper method

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        for i in range(1, 4):
            data = DataContainer()
            data[CUBA.MASS] = 1
            data[CUBA.MATERIAL_TYPE] = i
            pc = Particles(name="foo{}".format(i))
            pc.data = data

            random.seed(42)
            for _ in range(100):
                coord = (random.uniform(0.0, 25.0),
                         random.uniform(0.0, 22.0),
                         0.0)
                p = Particle(coordinates=coord)
                p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
                pc.add_particle(p)
            pc_w = wrapper.add_particles(pc)

            vectors = [(25.0, 0.0, 0.0),
                       (0.0, 22.0, 0.0),
                       (0.0, 0.0, 1.0)]
            pc_w.data_extension[CUBAExtension.BOX_VECTORS] = vectors

            pc_w.data_extension[CUBAExtension.BOX_ORIGIN] = (0.0, 0.0, 0.0)
