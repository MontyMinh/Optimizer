import sys  # Get the path to the "model" directory
import unittest

import numpy as np
from scipy.linalg import block_diag

sys.path.append("C:\\Users\\monty.minh\\Documents\\Optimizer")

from model.data import Data
from model.optimization import generate_combination_matrices
from model.optimization import generate_capacity_matrix
from model.optimization import generate_supply_matrix


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

        Data.capacity_constraints = [list(cons) for cons in {
            tuple(sorted(np.random.choice(Data.product_list,
                                          size=np.random.randint(1,
                                                                 len(Data.product_list) + 1),
                                          replace=False).tolist())) for i in
            range(3)}]

        Data.supply_constraints = [list(cons) for cons in {
            tuple(sorted(np.random.choice(Data.product_list,
                                          size=np.random.randint(1,
                                                                 len(Data.product_list) + 1),
                                          replace=False).tolist())) for i in
            range(3)}]

    @classmethod
    def alternative_combination_matrix(cls):
        """Construct the combination matrix in an alternative method"""

        # Alternative Inbound Combination Matrix,
        # Here we start by choosing out the appropriate index and
        # replace those elements with the efficiency values
        cls.inbound_combination_matrix = np.zeros(
            (cls.no_factories * cls.no_products,
             cls.no_factories * cls.no_products))

        matrix_index = np.hstack([
            cls.no_factories * prod + Data.factory_names[prod]
            for prod in Data.product_list
        ])

        cls.inbound_combination_matrix[
            matrix_index, matrix_index] = np.hstack(
            list(Data.efficiency_per_product.values()))

        cls.inbound_combination_matrix = \
            -cls.inbound_combination_matrix[
             :, ~np.all(
                cls.inbound_combination_matrix == 0, axis=0)]

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

        cls.outbound_combination_matrix = block_diag(*block_list)

    @classmethod
    def alternative_capacity_matrix(cls):
        """Construct the capacity matrix in an alternative method"""

        cap_list = []

        for cons in Data.capacity_constraints:

            mat = 0
            for prod in cons:
                mat += Data.outbound_combination_matrices[prod]

            cap_list.append(mat)

        outbound_capacity_matrix = np.vstack(cap_list)

        outbound_capacity_matrix = outbound_capacity_matrix[
            ~np.all(outbound_capacity_matrix == 0, axis=1)]

        # Then we build the all zero inbound matrix with the same number of
        # rows
        # as the outbound matrix
        inbound_capacity_matrix = np.zeros(
            (outbound_capacity_matrix.shape[0], Data.dimF))

        cls.capacity_matrix = np.hstack(
            [inbound_capacity_matrix, outbound_capacity_matrix])

    @classmethod
    def alternative_supply_matrix(cls):
        """Construct the supply matrix in an alternative method"""

        # Inbound section of the supply matrix
        sup_list_in = []

        for cons in Data.supply_constraints:

            mat = 0
            for prod in cons:
                mat += Data.inbound_combination_matrices[prod]

            sup_list_in.append(mat)

        inbound_supply_matrix = np.vstack(sup_list_in)

        inbound_supply_matrix = inbound_supply_matrix[
            ~np.all(inbound_supply_matrix == 0, axis=1)]

        # Outbound section of the supply matrix
        sup_list_out = []

        for cons in Data.supply_constraints:

            mat = 0
            for prod in cons:
                mat += Data.outbound_combination_matrices[prod]

            sup_list_out.append(mat)

        outbound_supply_matrix = np.vstack(sup_list_out)

        outbound_supply_matrix = outbound_supply_matrix[
            ~np.all(outbound_supply_matrix == 0, axis=1)]

        cls.supply_matrix = np.hstack(
            [inbound_supply_matrix, outbound_supply_matrix])


class TestCombinationMatrices(unittest.TestCase):
    def test_combination_matrices(self):
        for _ in range(100):
            # Generate Random Inputs
            CombinationTest.generate_random_inputs()

            # Generate the combination matrix
            generate_combination_matrices()
            generate_capacity_matrix()
            generate_supply_matrix()

            # Generate the alternative combination matrix
            CombinationTest.alternative_combination_matrix()
            CombinationTest.alternative_capacity_matrix()
            CombinationTest.alternative_supply_matrix()

            # Check inbound equality
            self.assertTrue(np.array_equal(np.vstack(list(
                Data.inbound_combination_matrices.values())),
                CombinationTest.inbound_combination_matrix)
            )

            # Check outbound equality
            self.assertTrue(np.array_equal(np.vstack(list(
                Data.outbound_combination_matrices.values())),
                CombinationTest.outbound_combination_matrix)
            )

            # Check capacity equality
            self.assertTrue(np.array_equal(CombinationTest.capacity_matrix,
                                           Data.capacity_matrix))

            # Check capacity equality
            self.assertTrue(np.array_equal(CombinationTest.supply_matrix,
                                           Data.supply_matrix))

            if __name__ == '__main__':
                unittest.main()
