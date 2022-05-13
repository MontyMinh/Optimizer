import sys  # Get the path to the "model" directory
import unittest

import numpy as np
from scipy.linalg import block_diag

sys.path.append("C:\\Users\\monty.minh\\Documents\\Optimizer")

from model.data import Data
from model.optimization import generate_combination_matrices


class CombinationTest:
    """Class for generating random test inputs and verify that the combination
    matrix is constructed correctly"""

    outbound_combination_matrix = None
    inbound_combination_matrix = None
    no_products = None
    customer_names = None
    no_factories = None
    no_customers = None

    @classmethod
    def generate_random_inputs(cls):
        """Generate random Data inputs"""

        cls.no_customers = np.random.randint(1, 20)
        cls.no_factories = np.random.randint(1, 10)
        cls.no_products = np.random.randint(1, 10)

        if cls.no_customers == 1:
            cls.customer_names = dict(
                zip(range(cls.no_products), [np.array([0])] * cls.no_products))
        else:  # Allow for one customer
            cls.customer_names = {
                prod: np.sort(
                    np.random.choice(np.arange(cls.no_customers),
                                     size=np.random.randint(
                                         1, cls.no_customers),
                                     replace=False))
                for prod in range(cls.no_products)
            }

        if cls.no_factories == 1:
            Data.factory_names = dict(
                zip(range(cls.no_products), [np.array([0])] * cls.no_products))
        else:  # Allow for one factory
            Data.factory_names = {
                prod: np.sort(
                    np.random.choice(np.arange(cls.no_factories),
                                     size=np.random.randint(
                                         1, cls.no_factories),
                                     replace=False))
                for prod in range(cls.no_products)
            }

        # Inputs from Data
        Data.factory_list = list(range(cls.no_factories))
        Data.product_list = list(range(cls.no_products))

        Data.customer_sizes = {
            prod: len(cls.customer_names[prod])
            for prod in range(cls.no_products)
        }

        Data.factory_sizes = {
            prod: len(Data.factory_names[prod])
            for prod in range(cls.no_products)
        }

        Data.efficiency_per_product = dict(
            zip(range(cls.no_products), [
                np.random.uniform(0.8, 1, Data.factory_sizes[prod])
                for prod in range(cls.no_products)
            ]))

        Data.dimF = sum(Data.factory_sizes.values())
        Data.dimC = sum(Data.customer_sizes.values())

        Data.dimFC = sum([
            Data.factory_sizes[prod] * Data.customer_sizes[prod]
            for prod in range(cls.no_products)
        ])

    @classmethod
    def alternative_combination_matrix(cls):
        """Construct the combination matrix in an alternative method"""

        # Alternative Inbound Combination Matrix,
        # Here we start by choosing out the appropriate index and
        # replace those elements with the efficiency values
        CombinationTest.inbound_combination_matrix = np.zeros(
            (cls.no_factories * cls.no_products,
             cls.no_factories * cls.no_products))

        matrix_index = np.hstack([
            cls.no_factories * prod + Data.factory_names[prod]
            for prod in Data.product_list
        ])

        CombinationTest.inbound_combination_matrix[
            matrix_index, matrix_index] = np.hstack(
            list(Data.efficiency_per_product.values()))

        CombinationTest.inbound_combination_matrix = \
            -CombinationTest.inbound_combination_matrix[
             :, ~np.all(
                CombinationTest.inbound_combination_matrix == 0, axis=0)]

        # Alternative Outbound Combination Matrix
        # Here we just iterate over all the products
        # and find out which factories produce and which
        # don't. Then we either put [1, ..., 1] or [] as
        # appropriate

        block_list = []

        for prod in Data.product_list:

            subblock_list = []

            for fac in Data.factory_list:

                if fac in Data.factory_names[prod]:
                    subblock_list.append([1] * Data.customer_sizes[prod])
                else:
                    subblock_list.append([])

            block_list.append(block_diag(*subblock_list))

        CombinationTest.outbound_combination_matrix = block_diag(*block_list)


class TestCombinationMatrices(unittest.TestCase):
    def test_combination_matrices(self):
        for _ in range(100):
            # Generate Random Inputs
            CombinationTest.generate_random_inputs()

            # Generate the combination matrix
            generate_combination_matrices()

            # Generate the alternative combination matrix
            CombinationTest.alternative_combination_matrix()

            # Check inbound equality
            self.assertTrue(np.array_equal(
                Data.inbound_combination_matrix,
                CombinationTest.inbound_combination_matrix)
            )

            # Check outbound equality
            self.assertTrue(np.array_equal(
                Data.outbound_combination_matrix,
                CombinationTest.outbound_combination_matrix)
            )


if __name__ == '__main__':
    unittest.main()
