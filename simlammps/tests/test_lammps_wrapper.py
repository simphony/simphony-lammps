import unittest

from simlammps.lammps_wrapper import LammpsWrapper, InterfaceType
from simlammps.testing.abc_lammps_md_engine_check import ABCLammpsMDEngineCheck


class TestLammpsMDEngineINTERNAL(ABCLammpsMDEngineCheck, unittest.TestCase):

    def setUp(self):
        ABCLammpsMDEngineCheck.setUp(self)

    def engine_factory(self):
        return LammpsWrapper(interface=InterfaceType.INTERNAL)


class TestLammpsMDEngineFileIO(ABCLammpsMDEngineCheck, unittest.TestCase):

    def setUp(self):
        ABCLammpsMDEngineCheck.setUp(self)

    def engine_factory(self):
        return LammpsWrapper(interface=InterfaceType.FILEIO)


if __name__ == '__main__':
    unittest.main()
