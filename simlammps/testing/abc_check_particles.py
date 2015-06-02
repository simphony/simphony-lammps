import abc
import uuid
from functools import partial

from simphony.testing.utils import (
    compare_particles, create_data_container)
from simphony.cuds.particles import Particle

from simlammps.testing.utils import create_particles

# THIS IS A COPY from simphony-common
#   - TODO using our own create particles to ensure
#     that they are located in the simulation box
#   - TODO not supporting delete yet (so we don't
#     run delete related tests yet.)


_valid_coordinates = (0.1, 0.1, 0.1)


class ContainerAddParticlesCheck(object):

    __metaclass__ = abc.ABCMeta

    def setUp(self, restrict=None):
        self.particle_list = create_particles(restrict=restrict)
        self.container = self.container_factory('foo')
        self.ids = [
            self.container.add_particle(particle)
            for particle in self.particle_list]

    @abc.abstractmethod
    def container_factory(self, name):
        """ Create and return the container object
        """

    def test_has_particle(self):
        container = self.container
        self.assertTrue(container.has_particle(self.ids[6]))
        self.assertFalse(container.has_particle(uuid.UUID(int=1234)))

    def test_add_particle_ok(self):
        container = self.container
        for index, particle in enumerate(self.particle_list):
            self.assertTrue(container.has_particle(particle.uid))
            self.assertEqual(particle.uid, self.ids[index])

    def test_add_particle_with_id(self):
        container = self.container
        uid = uuid.uuid4()
        particle = Particle(
            uid=uid,
            coordinates=_valid_coordinates,
            data=create_data_container())
        particle_uid = container.add_particle(particle)
        self.assertEqual(particle_uid, uid)
        self.assertTrue(container.has_particle(uid))

    def test_exception_when_adding_particle_twice(self):
        container = self.container
        with self.assertRaises(ValueError):
            container.add_particle(self.particle_list[3])


class ContainerManipulatingParticlesCheck(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def container_factory(self, name, restrict=None):
        """ Create and return the container object
        """

    def setUp(self, restrict=None):
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.particle_list = create_particles(restrict=restrict)
        self.particle_list[0].uid = uuid.uuid4()
        self.container = self.container_factory('foo')
        self.ids = [
            self.container.add_particle(particle)
            for particle in self.particle_list]

    def test_get_particle(self):
        container = self.container
        for uid, particle in map(None, self.ids, self.particle_list):
            self.assertEqual(container.get_particle(uid), particle)

    def test_update_particle(self):
        container = self.container
        particle = container.get_particle(self.ids[2])
        particle.coordinates = _valid_coordinates
        container.update_particle(particle)
        retrieved = container.get_particle(particle.uid)
        self.assertEqual(retrieved, particle)

    def test_exception_when_update_particle_when_wrong_id(self):
        container = self.container
        particle = Particle(uid=uuid.uuid4())
        with self.assertRaises(ValueError):
            container.update_particle(particle)
        particle = Particle()
        with self.assertRaises(ValueError):
            container.update_particle(particle)

    # TODO not yet supported
    def DUMMY_test_remove_particle(self):
        container = self.container
        particle = self.particle_list[0]
        container.remove_particle(particle.uid)
        self.assertFalse(container.has_particle(particle.uid))

    # TODO not yet supported
    def DUMMY_test_exception_when_removing_particle_with_bad_id(self):
        container = self.container
        with self.assertRaises(KeyError):
            container.remove_particle(uuid.UUID(int=23325))
        with self.assertRaises(KeyError):
            container.remove_particle(None)

    def test_iter_particles_when_passing_ids(self):
        particles = [particle for particle in self.particle_list[::2]]
        ids = [particle.uid for particle in particles]
        iterated_particles = [
            particle for particle in self.container.iter_particles(ids)]
        for particle, reference in map(None, iterated_particles, particles):
            self.assertEqual(particle, reference)

    def test_iter_all_particles(self):
        particles = {particle.uid: particle for particle in self.particle_list}
        iterated_particles = [
            particle for particle in self.container.iter_particles()]
        # The order of iteration is not important in this case.
        self.assertEqual(len(particles), len(iterated_particles))
        for particle in iterated_particles:
            self.assertEqual(particle, particles[particle.uid])

    def test_exception_on_iter_particles_when_passing_wrong_ids(self):
        ids = [particle.uid for particle in self.particle_list]
        ids.append(uuid.UUID(int=20))
        with self.assertRaises(KeyError):
            for particle in self.container.iter_particles(ids):
                pass
        self.assertEqual(particle.uid, self.particle_list[-1].uid)
