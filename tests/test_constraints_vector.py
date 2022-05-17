import sys  # Get the path to the "model" directory
import unittest

import numpy as np

sys.path.append("C:\\Users\\monty.minh\\Documents\\Optimizer")

from model.data import Data
from model.optimization import generate_constraints_vector


class TestConstraintsVector(unittest.TestCase):
    def test_constraints_vector(self):

        for _ in range(100):
            constraints_vector = np.random.rand(np.random.randint(5, 20), 1)

            Data.demand_volume, Data.capacity_volume = np.split(
                constraints_vector,
                [np.random.randint(1, len(constraints_vector))])

            constraints_vector = np.vstack(
                [constraints_vector,
                 np.zeros((np.random.randint(5, 20), 1))])

            Data.dimC, Data.capacity_rows = Data.demand_volume.size, \
                                            Data.capacity_volume.size
            Data.supply_rows = constraints_vector.size - Data.dimC - \
                               Data.capacity_rows

            generate_constraints_vector()

            self.assertTrue(np.array_equal(Data.constraints_vector,
                                           constraints_vector))


if __name__ == '__main__':
    unittest.main()
