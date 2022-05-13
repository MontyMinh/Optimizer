import sys  # Get the path to the "model" directory
import unittest

import numpy as np
from scipy.linalg import block_diag

sys.path.append("C:\\Users\\monty.minh\\Documents\\Optimizer")

from model.data import Data
from model.optimization import generate_demand_matrix


class DemandTest:
    """Class for generating random test inputs and verify that the demand
    matrix is constructed correctly"""

    no_products = None
    factory_names = None
    customer_names = None
    no_factories = None
    no_customers = None

    @classmethod
    def generate_random_inputs(cls):
        """Generate random Data inputs"""

        cls.no_customers = np.random.randint(1, 10)
        cls.no_factories = np.random.randint(1, 5)
        cls.no_products = np.random.randint(1, 5)

        if cls.no_customers == 1:
            cls.customer_names = dict(
                zip(range(cls.no_products), [np.array([0])] * cls.no_products))
        else:  # Allow for one customer
            cls.customer_names = {
                prod: np.sort(
                    np.random.choice(np.arange(cls.no_customers),
                                     size=np.random.randint(1,
                                                            cls.no_customers),
                                     replace=False))
                for prod in range(cls.no_products)
            }

        if cls.no_factories == 1:
            cls.factory_names = dict(
                zip(range(cls.no_products), [np.array([0])] * cls.no_products))
        else:  # Allow for one factory
            cls.factory_names = {
                prod: np.sort(
                    np.random.choice(np.arange(cls.no_factories),
                                     size=np.random.randint(1,
                                                            cls.no_factories),
                                     replace=False))
                for prod in range(cls.no_products)
            }

        # Inputs from Data
        Data.customer_sizes = {
            prod: len(cls.customer_names[prod])
            for prod in range(cls.no_products)
        }

        Data.factory_sizes = {
            prod: len(cls.factory_names[prod])
            for prod in range(cls.no_products)
        }

        Data.product_list = list(range(cls.no_products))

        Data.dimF = sum(Data.factory_sizes.values())
        Data.dimC = sum(Data.customer_sizes.values())

        Data.dimFC = sum([
            Data.factory_sizes[prod] * Data.customer_sizes[prod]
            for prod in range(cls.no_products)
        ])

    @classmethod
    def alternative_demand_matrix(cls):
        """Construct the demand matrix in an alternative method"""

        block_list = []

        for prod in Data.product_list:
            block = np.zeros(
                (cls.no_customers, cls.no_customers * cls.no_factories))

            # Row Index
            row_index = np.repeat(cls.customer_names[prod],
                                  repeats=Data.factory_sizes[prod])

            # Column Index
            column_index = np.hstack(cls.no_customers *
                                     cls.factory_names[prod] +
                                     cls.customer_names[prod][:, np.newaxis])

            # Fill ones in the appropriate place
            block[row_index, column_index] = 1

            # Remove columns and rows with all zeros
            block = block[:, ~np.all(block ==
                                     0, axis=0)][~np.all(block == 0, axis=1)]

            block_list.append(block)

        # Append with the inbound block then return
        return np.hstack(
            [np.zeros((Data.dimC, Data.dimF)),
             block_diag(*block_list)])


class TestDemandMatrix(unittest.TestCase):
    def test_demand_matrix(self):
        for _ in range(100):
            DemandTest.generate_random_inputs()  # Random Inputs
            generate_demand_matrix()  # Generate Demand Matrix

            self.assertTrue(
                np.array_equal(DemandTest.alternative_demand_matrix(),
                               Data.demand_matrix)
            )  # Compare the demand matrix, with an alternative method


if __name__ == '__main__':
    unittest.main()
