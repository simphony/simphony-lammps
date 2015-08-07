import unittest

from simlammps.config.domain import get_box


class TestDomain(unittest.TestCase):
    """ Tests the domain config class

    """
    def test_missing_domain(self):
        with self.assertRaises(RuntimeError):
            get_box([])

        with self.assertRaises(RuntimeError):
            get_box([{}, {}])

if __name__ == '__main__':
    unittest.main()
