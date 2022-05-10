import unittest
import numpy as np
import sys  # Get the path to the "model" directory
sys.path.append("C:\\Users\\monty.minh\\Documents\\Model4.0")

from model.modeldata import Data
from model.optimization import generate_objective_vector


# Class generate random inputs
class DataTest:

    """Class for generating random test inputs"""

    inbound_cost_vector, outbound_cost_vector = None, None
    objective_vector = None

    @classmethod
    def generate_random_inputs(cls):
        """
        Generate random inputs for objective vector unit test

        For inbound cost vector, we first generate the
        vector and split it into sub-vectors per product.

        For outbound cost vector, we first randomize the
        rectangular dimension. Then we generate a random
        vector and split it back into rectangular matrices
        with column - row major.

        Finally, we concatenate them to form the objective vector.

        """

        # Inbound Cost Vector
        cls.inbound_cost_vector = np.random.rand(np.random.randint(20, 100))

        Data.dimF = len(cls.inbound_cost_vector)  # number of factor-product

        split_index_in = np.sort(
            np.random.choice(np.arange(len(cls.inbound_cost_vector)),
                             np.random.randint(5, 10),
                             replace=False))

        Data.inbound_cost_per_product = dict(
            zip(np.arange(len(split_index_in) + 1),
                np.hsplit(cls.inbound_cost_vector, split_index_in)))

        # Outbound Cost Vector
        dimension_split = [
            np.random.randint(1, 6, 2) for _ in range(np.random.randint(3, 10))
        ]

        split_index_out = np.cumsum(np.product(np.vstack(dimension_split), axis=1))

        cls.outbound_cost_vector = np.random.rand(split_index_out[-1])

        Data.dimFC = len(cls.outbound_cost_vector)

        Data.outbound_cost_per_product = dict([
            (index, prod.reshape(*dimension_split[index], order='F'))
            for index, prod in enumerate(
                np.split(cls.outbound_cost_vector, split_index_out[:-1]))
        ])

        cls.objective_vector = np.hstack([cls.inbound_cost_vector, cls.outbound_cost_vector])


class TestObjectiveVector(unittest.TestCase):
    def test_objective_vector(self):

        """Compare construction with randomly generated random inputs"""

        for _ in range(100):  # Test 100 times
            # Generate Random Inbound Inputs
            DataTest.generate_random_inputs()
            # Construct the correct vector
            generate_objective_vector()

            self.assertTrue(np.array_equal(DataTest.objective_vector, Data.objective_vector))  # add assertion here


if __name__ == '__main__':
    unittest.main()
