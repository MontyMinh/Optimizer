from model import *
from model.data import Data


class RandomInputs:
    """Class to generate random models to test optimization.py"""

    def __init__(self,
                 no_products=3,
                 no_factories=5,
                 no_customers=10,
                 factory_sizes_range=(1, 5),
                 customer_sizes_range=(1, 10),
                 inbound_cost_range=(0, 1),
                 outbound_cost_range=(0, 1),
                 efficiency_range=(0.8, 1),
                 no_capacity_constraints=4,
                 capacity_constraints_range=(1, 3),
                 no_supply_constraints=5,
                 supply_constraints_range=(1, 3),
                 demand_volume_range=(1, 20),
                 capacity_volume_range=(1000, 10_000)):
        """Initialized Parameters to Generate Inputs"""

        self.no_products = no_products
        self.no_factories = no_factories
        self.factory_sizes_range = factory_sizes_range

        self.no_customers = no_customers
        self.customer_sizes_range = customer_sizes_range

        self.inbound_cost_range = inbound_cost_range
        self.outbound_cost_range = outbound_cost_range

        self.efficiency_range = efficiency_range

        self.no_capacity_constraints = no_capacity_constraints
        self.capacity_constraints_range = capacity_constraints_range

        self.no_supply_constraints = no_supply_constraints
        self.supply_constraints_range = supply_constraints_range

        self.demand_volume_range = demand_volume_range
        self.capacity_volume_range = capacity_volume_range

        # Check that the inputs is valid
        assert self.factory_sizes_range[
                   1] <= self.no_factories, 'The sample size must be smaller '\
                                            'than the number of factories'

        assert self.customer_sizes_range[
                   1] <= self.no_customers, 'The sample size must be smaller '\
                                            'than the number of customers'

        assert self.efficiency_range[
                   1] <= 1, 'Efficiency cannot be bigger than 1'

        assert self.capacity_constraints_range[
                   0] > 0, 'Capacity constraints cannot be empty'
        assert self.capacity_constraints_range[
                   1] <= self.no_products, 'Number of capacity_constraints ' \
                                           'cannot exceed the number of ' \
                                           'factories'

        assert self.supply_constraints_range[
                   0] > 0, 'supply constraints cannot be empty'
        assert self.supply_constraints_range[
                   1] <= self.no_products, 'Number of supply_constraints ' \
                                           'cannot exceed the number of ' \
                                           'products'

    def generate(self):
        """Generate Random Pre-Processing Inputs for User Defined Parameters"""

        Data.product_list = list(range(self.no_products))
        Data.factory_list = np.arange(self.no_factories)

        Data.factory_sizes = dict(
            zip(Data.product_list, [
                np.random.randint(self.factory_sizes_range[0],
                                  self.factory_sizes_range[1] + 1)
                for _ in Data.product_list
            ]))

        Data.customer_sizes = dict(
            zip(Data.product_list, [
                np.random.randint(self.customer_sizes_range[0],
                                  self.customer_sizes_range[1] + 1)
                for _ in Data.product_list
            ]))

        Data.factory_names = dict(
            zip(Data.product_list, [
                np.random.choice(a=Data.factory_list,
                                 size=Data.factory_sizes[prod],
                                 replace=False) for prod in Data.product_list
            ]))

        Data.dimF = sum(Data.factory_sizes.values())

        Data.dimC = sum(Data.customer_sizes.values())
        Data.dimFC = sum(
            np.array(list(Data.customer_sizes.values())) *
            np.array(list(Data.factory_sizes.values())))

        Data.inbound_cost_per_product = dict(
            zip(Data.product_list, [
                np.random.uniform(*self.inbound_cost_range,
                                  size=Data.factory_sizes[prod])
                for prod in Data.product_list
            ]))

        Data.outbound_cost_per_product = dict(
            zip(Data.product_list, [
                np.random.uniform(
                    *self.outbound_cost_range,
                    size=Data.factory_sizes[prod] * Data.customer_sizes[prod])
                for prod in Data.product_list
            ]))

        Data.efficiency_per_product = dict(
            zip(Data.product_list, [
                np.random.uniform(*self.efficiency_range,
                                  size=Data.factory_sizes[prod])
                for prod in Data.product_list
            ]))

        Data.capacity_constraints = [
            list(cons) for cons in {
                tuple(
                    sorted(
                        np.random.choice(
                            Data.product_list,
                            size=np.random.randint(
                                self.capacity_constraints_range[0],
                                self.capacity_constraints_range[1] + 1),
                            replace=False).tolist()))
                for _ in range(self.no_capacity_constraints)
            }
        ]

        Data.supply_constraints = [
            list(cons) for cons in {
                tuple(
                    sorted(
                        np.random.choice(Data.product_list,
                                         size=np.random.randint(
                                             self.supply_constraints_range[0],
                                             self.supply_constraints_range[1] +
                                             1),
                                         replace=False).tolist()))
                for _ in range(self.no_supply_constraints)
            }
        ]

        Data.demand_volume_per_product = dict(
            zip(Data.product_list, [
                np.random.uniform(*self.demand_volume_range,
                                  size=Data.customer_sizes[prod])
                for prod in Data.product_list
            ]))

        capacity_rows = sum([
            len(
                reduce(lambda a, b: a.union(b),
                       [set(Data.factory_names[prod]) for prod in cons]))
            for cons in Data.capacity_constraints
        ])

        Data.capacity_volume = np.random.uniform(
            *self.capacity_volume_range, size=capacity_rows)[:, np.newaxis]
