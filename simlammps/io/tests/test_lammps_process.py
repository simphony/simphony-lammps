import unittest
import shutil
import tempfile

from simlammps.io.lammps_process import LammpsProcess


class TestLammpsProcess(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.lammps = LammpsProcess(log_directory=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_run_hello_world(self):
        command = "print \"hello world\""
        self.lammps.run(command)

    def test_run_problem(self):
        command = "thisisnotalammpscommmand"
        with self.assertRaises(RuntimeError):
            self.lammps.run(command)

    def test_cannot_find_lammps(self):
        lammps_name = "this_is_not_lammps"
        with self.assertRaises(RuntimeError):
            self.lammps = LammpsProcess(lammps_name=lammps_name)


if __name__ == '__main__':
    unittest.main()
