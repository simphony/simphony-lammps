import random

from simphony.cuds.particles import Particle
from simphony.testing.utils import create_data_container


def create_particles(n=10, restrict=None):
    """ Create particles in a certain range

    Particles are created in a certain range and with
    certain values to correspond with testing of
    lammps-md wrapper

    """
    random.seed(24)

    particle_list = []
    for i in xrange(n):
        # TODO get desired range from somewhere else
        coord = (random.uniform(0.0, 25.0),
                 random.uniform(0.0, 22.0),
                 0.0)

        data = create_data_container(restrict=restrict)
        particle_list.append(
            Particle(coordinates=coord, data=data))
    return particle_list
