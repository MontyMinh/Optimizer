import unittest
import numpy as np
from scipy.linalg import block_diag
import sys  # Get the path to the "model" directory

sys.path.append("C:\\Users\\monty.minh\\Documents\\Model4.0")

from model.modeldata import Data
from model.optimization import generate_combination_matrices
from functools import reduce


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
