import random

from simphony.core.cuba import CUBA
from simphony.cuds.meta.api import Material
from simphony.cuds.particles import Particle, Particles


class MDExampleConfigurator:
    """  Class which handles configuration of MD examples

    Class provides an example configuration for a
    lammps molecular dynamic engine

    Attributes:
    -----------
    materials : list of Material
        materials

    """

    def __init__(self,
                 materials=None,
                 box_origin=None,
                 box_vectors=None,
                 number_time_steps=10):
        """ Initialize the configurator

        Parameters
        ----------
        wrapper : ABCModelingEngine
            wrapper to be configured
        materials : Material, list
            list of materials (if None, then 3 materials will be created)
        number_time_steps : int
            number of time steps to run

        """
        # box origin and box vectors
        if box_origin is None:
            self._box_origin = (0.0, 0.0, 0.0)
        else:
            self._box_origin = box_origin
        if box_vectors is None:
            self._box_vectors = [(101.0, 0.0, 0.0),
                                 (0.0, 101.0, 0.0),
                                 (0.0, 0.0, 1001.0)]
        else:
            self._box_vectors = box_vectors

        if materials is None:
            self._materials = []
            random.seed(42)
            for _ in xrange(3):
                material = Material()
                material.data.update({CUBA.MASS: random.uniform(1.0, 2.0)})
                self._materials.append(material)
        else:
            self._materials = materials

        self._number_time_steps = number_time_steps

    @property
    def materials(self):
        return self._materials

    def set_configuration(self, wrapper):
        """ Configure example engine with example settings

        The wrapper is configured with required CM, SP, BC and SD parameters

        Parameters
        ----------
        wrapper : ABCModelingEngine
            wrapper to be configured

        """

        # CM
        wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = self._number_time_steps
        wrapper.CM[CUBA.TIME_STEP] = 0.003
        wrapper.CM[CUBA.THERMODYNAMIC_ENSEMBLE] = "NVE"

        # SP
        pair_potential = ("lj:\n"
                          "  global_cutoff: 1.12246\n"
                          "  parameters:\n")

        # TODO currently pair potentials are using 1-n integers
        material_types = set(
            mat_int for mat_int in xrange(1, len(self._materials)+1))
        while material_types:
            m_type = material_types.pop()
            for other in ([t for t in material_types] + [m_type]):
                pair_potential += "  - pair: [{}, {}]\n".format(m_type,
                                                                other)
                pair_potential += ("    epsilon: 1.0\n"
                                   "    sigma: 1.0\n"
                                   "    cutoff: 1.2246\n")
        wrapper.SP[CUBA.PAIR_POTENTIAL] = pair_potential

        # BC
        wrapper.BC[CUBA.FACE] = (
            "periodic", "periodic", "periodic")

        wrapper.SD.add(self._materials)

    def configure_wrapper(self, wrapper):
        """ Configure example wrapper with example settings and particles

        The wrapper is configured with required CM, SP, BC parameters
        and is given particles (see add_particles)

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        # configure
        self.set_configuration(wrapper)

        # add particle containers
        self.add_particles(wrapper)

    def add_particles(self, wrapper):
        """ Add containers of particles to wrapper

        The wrapper is configured with containers of particles that contain
        mass, type/materialtype, and velocity.  They correspond to
        the configuration performed in configure_wrapper method

        Parameters
        ----------
        wrapper : ABCModelingEngine

        """
        random.seed(42)
        for i in range(1, 4):
            pc = self.get_empty_particles(name="foo{}".format(i))

            for _ in range(10):
                # determine valid coordinates from simulation box
                xrange = (self._box_origin[0], self._box_vectors[0][0])
                yrange = (self._box_origin[1], self._box_vectors[1][1])
                zrange = (self._box_origin[2], self._box_vectors[2][2])

                coord = (random.uniform(xrange[0], xrange[1]),
                         random.uniform(yrange[0], yrange[1]),
                         random.uniform(zrange[0], zrange[1]))

                material_i = random.randint(0, len(self._materials)-1)

                p = Particle(coordinates=coord)
                p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
                p.data[CUBA.MATERIAL_TYPE] = self._materials[material_i].uid
                pc.add([p])

            wrapper.add_dataset(pc)

    def get_empty_particles(self, name):
        """ Get an empty particle container

        The returned data set is configured accordingly.

        Parameters
        ----------
        name : str
            name of particle container

        Returns
        -------
        pc : Particles
            dataset with no particles but properly configured

        """
        pc = Particles(name=name)
        pc.data = {CUBA.VECTOR: self._box_vectors,
                   CUBA.ORIGIN: self._box_origin}
        return pc
