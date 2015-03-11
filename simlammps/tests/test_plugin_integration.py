import unittest


class TestPluginIntegration(unittest.TestCase):

    def test_plugin_integration(self):

        from simphony.engine import lammps

        self.assertTrue(hasattr(lammps, 'LammpsWrapper'))


if __name__ == '__main__':
    unittest.main()
