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

    # box origin and box vectors
    box_origin = (0.0, 0.0, 0.0)
    box_vectors = [(101.0, 0.0, 0.0),
                   (0.0, 101.0, 0.0),
                   (0.0, 0.0, 1001.0)]

    @staticmethod
    def set_configuration(wrapper, material_types=None):
        """ Configure example engine with example settings

        The wrapper is configured with required CM, SP, BC parameters

        Parameters
        ----------
        wrapper : ABCModelingEngine
            wrapper to be configured
        material_types : iterable of int
            material type that needs to be configured (used for pair
            potentials). If None, then 3 (i.e. 1,2,3) material types
            are assumed.

        """

        # CM
        wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = 10
        wrapper.CM[CUBA.TIME_STEP] = 0.003
        wrapper.CM_extension[CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"

        if material_types is None:
            material_types = set([1, 2, 3])
        else:
            material_types = set(material_types)

        # SP
        pair_potential = ("lj:\n"
                          "  global_cutoff: 1.12246\n"
                          "  parameters:\n")
        while material_types:
            m_type = material_types.pop()
            for other in ([t for t in material_types] + [m_type]):
                pair_potential += "  - pair: [{}, {}]\n".format(m_type,
                                                                other)
                pair_potential += ("    epsilon: 1.0\n"
                                   "    sigma: 1.0\n"
                                   "    cutoff: 1.2246\n")
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
                # determine valid coordinates from simulation box
                xrange = (MDExampleConfigurator.box_origin[0],
                          MDExampleConfigurator.box_vectors[0][0])
                yrange = (MDExampleConfigurator.box_origin[1],
                          MDExampleConfigurator.box_vectors[1][1])
                zrange = (MDExampleConfigurator.box_origin[2],
                          MDExampleConfigurator.box_vectors[2][2])

                coord = (random.uniform(xrange[0], xrange[1]),
                         random.uniform(yrange[0], yrange[1]),
                         random.uniform(zrange[0], zrange[1]))
                p = Particle(coordinates=coord)
                p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
                pc.add_particles([p])

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

        pc.data_extension = {CUBAExtension.BOX_VECTORS:
                             MDExampleConfigurator.box_vectors,
                             CUBAExtension.BOX_ORIGIN:
                             MDExampleConfigurator.box_origin}

        pc_w = wrapper.add_dataset(pc)

        return pc_w
