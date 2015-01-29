import random

from simphony.cuds.particles import Particle, ParticleContainer
from simphony.core.cuba import CUBA


class ExampleConfigurator:
    """  Example configuration

    Class provides an example configuration for a
    lammps wrapper

    """

    @staticmethod
    def configure_wrapper(wrapper):
        """ Configure example wrapper with example settings and particles

        The wrapper is configured with required CM, SP, BC parameters
        and is given particles (see get_particle_containers)

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = 10000
        wrapper.CM[CUBA.TIME_STEP] = 0.003

        wrapper.CM[CUBA.PAIR_POTENTIALS] = ("lj:\n"
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

        # add particle containers
        i = 0
        for pc in ExampleConfigurator.get_particle_containers():
            name = "foo{}".format(i)
            wrapper.add_particle_container(name, pc)
            i += 1

    @staticmethod
    def get_particle_containers():

        """ Get example particle containers

        Returns particle container with mass, type/materialtype, and
        velocitiy.  They correspond to the configuration performed in
        configure_wrapper method
        """
        pcs = []
        for i in range(1, 4):
            pc = ParticleContainer()
            pc.data[CUBA.MASS] = 1
            pc.data[CUBA.MATERIAL_TYPE] = i

            random.seed(42)
            for i in range(100):
                coord = (random.uniform(0.0, 25.0),
                         random.uniform(0.0, 22.0),
                         0.0)
                p = Particle(coordinates=coord)
                p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
                pc.add_particle(p)
            pcs.append(pc)
        return pcs
