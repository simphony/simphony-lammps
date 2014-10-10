import os
import unittest

from simlammps.lammps_wrapper import LammpsWrapper
from simphony.cuds.particles import Particle


class TestLammpsFileParticleContainer(unittest.TestCase):

    def setUp(self):
        self.wrapper = LammpsWrapper()
        infile = os.path.dirname(__file__) + "/../example/in.flow.pois"
        lines = open(infile, 'r').readlines()
        for line in lines:
            self.wrapper._lammps.command(line)
        self.wrapper.run()

        for name, pc in self.wrapper.iter_particle_containers():
            self.pc = pc
            break
        else:
            self.fail("no particle containers to test with")

    def test_update_non_existing_particle(self):
        with self.assertRaises(Exception):
            p = Particle(id=100000000, coordinates=(0.0, 0.0, 0.0))
            self.pc.update_particle(p)

    def test_get_non_existing_particle(self):
        with self.assertRaises(Exception):
            self.pc.get_particle(100000000)

    def test_update_particle(self):
        particle = None
        for p in self.pc.iter_particles():
            particle = p
            break
        else:
            self.fail("could not find a particle to test with")

        particle.coordinates = (42.0, 42.0, 42.0)
        self.pc.update_particle(particle)
        updated_p = self.pc.get_particle(particle.id)

        self.assertEqual(p.coordinates, updated_p.coordinates)

    def test_add_particle_without_id(self):
        p = Particle(coordinates=(0.0, 2.5, 0.0))
        id = self.pc.add_particle(p)
        added_p = self.pc.get_particle(id)
        self.assertEqual(p.coordinates, added_p.coordinates)
