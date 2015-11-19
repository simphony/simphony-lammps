import unittest

from simphony.testing.abc_check_engine import ParticlesEngineCheck
from simphony.cuds.abc_particles import ABCParticles

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.testing.abc_lammps_md_engine_check import ABCLammpsMDEngineCheck
from simlammps.testing.md_example_configurator import MDExampleConfigurator


class TestLammpsMDEngineINTERNAL(ABCLammpsMDEngineCheck, unittest.TestCase):

    def setUp(self):
        ABCLammpsMDEngineCheck.setUp(self)

    def engine_factory(self):
        return LammpsWrapper(use_internal_interface=True)


class TestLammpsMDEngineFILEIO(ABCLammpsMDEngineCheck, unittest.TestCase):

    def setUp(self):
        ABCLammpsMDEngineCheck.setUp(self)

    def engine_factory(self):
        return LammpsWrapper(use_internal_interface=False)


class FixedParticlesEngineCheck(ParticlesEngineCheck):
    """ Class addresses issues with ABCEngineCheck  (See simphony-common #219)

    """

    def setUp(self):
        self._md_configurator = MDExampleConfigurator()
        ParticlesEngineCheck.setUp(self)

    def check_instance_of_dataset(self, ds):
        # TODO add to ParticlesEngineCheck
        self.assertTrue(isinstance(ds, ABCParticles))

    def test_delete_dataset(self):
        engine = self.engine_factory()
        # add a few empty datasets
        for i in xrange(5):
            name = "test_" + str(i)
            engine.add_dataset(self.create_dataset(name=name))

        datasets_and_names = [(ds, ds.name) for ds in engine.iter_datasets()]

        # delete each of the datasets
        for (dataset, name) in datasets_and_names:
            engine.remove_dataset(name)
            # test that we can't get deleted datasets
            with self.assertRaises(ValueError):
                engine.get_dataset(name)
            # test that we can't use the deleted datasets
            with self.assertRaises(Exception):
                self.compare_dataset(dataset, dataset)

    def test_iter_dataset(self):
        engine = self.engine_factory()
        # add a few empty datasets
        ds_names = []

        for i in xrange(5):
            name = "test_{}".format(i)
            ds_names.append(name)
            engine.add_dataset(self.create_dataset(name=name))

        # test iterating over all
        names = [
            ds.name for ds in engine.iter_datasets()]
        # TODO this method is overridden as the order of the names is not
        # important
        self.assertEqual(len(names), len(ds_names))
        self.assertEqual(set(names), set(ds_names))

        # test iterating over a specific subset
        subset = ds_names[:3]
        names = [
            ds.name for ds in engine.iter_datasets(subset)]
        self.assertEqual(names, subset)

        for ds in engine.iter_datasets(ds_names):
            self.check_instance_of_dataset(ds)

    def test_get_dataset_names(self):
        engine = self.engine_factory()
        # add a few empty datasets
        ds_names = []

        for i in xrange(5):
            name = "test_{}".format(i)
            ds_names.append(name)
            engine.add_dataset(
                self._md_configurator.get_empty_particles(name=name))

        # test that we are getting all the names
        # TODO  #218
        names = engine.get_dataset_names()
        self.assertEqual(len(names), len(ds_names))
        self.assertEqual(set(names), set(ds_names))


class TestINTERNALEngineCheck(FixedParticlesEngineCheck, unittest.TestCase):

    def engine_factory(self):
        return LammpsWrapper(use_internal_interface=True)

    def create_dataset(self, name):
        """ Create and return a cuds object

        """
        return self._md_configurator.get_empty_particles(name)


class TestFILEIOEngineCheck(FixedParticlesEngineCheck, unittest.TestCase):

    def engine_factory(self):
        return LammpsWrapper(use_internal_interface=False)


if __name__ == '__main__':
    unittest.main()
