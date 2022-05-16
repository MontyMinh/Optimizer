from model import *
from model.data import Data


def generate_objective_vector():
    """
    Inputs to data.py
    -----------------
    Data.inbound_cost_per_product: dict
        Dictionary containing the inbound cost to factories for all products

    Data.outbound_cost_per_product: dict
        Dictionary containing the outbound cost to factories for all products

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimC: int
        Σ|C| (total number of customers across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Outputs to data.py
    ------------------
    Data.objective_vector: numpy.ndarray
        Objective vector to minimize function value

    """

    # Verify inputs
    assert isinstance(Data.inbound_cost_per_product,
                      dict), 'Inbound costs must be given in a dictionary'
    assert isinstance(Data.outbound_cost_per_product,
                      dict), 'Outbound costs must be given in a dictionary'

    # Verify inputs dimension
    assert (len(Data.inbound_cost_per_product) == len(Data.product_list)), \
        'Number of products in Inbound cost per product is incorrect'
    assert (len(Data.outbound_cost_per_product) == len(Data.product_list)), \
        'Number of products in Outbound cost per product is incorrect'
    assert np.all(np.array([Data.dimF, Data.dimC, Data.dimFC]) > 0), \
        'Dimensions of constraints matrices must be positive'

    # Reshape dictionary inputs into vectors
    # Unpack inbound cost dictionary and stack into row vector
    inbound_cost_vector = np.hstack(
        list(Data.inbound_cost_per_product.values()))

    # Unpack outbound cost dictionary in factory-then-customer major
    outbound_cost_vector = np.hstack([
        prod.flatten('F') for prod in Data.outbound_cost_per_product.values()
    ])

    # Verify output dimension
    # Inbound cost vector dimension = (∑|F|)
    assert inbound_cost_vector.shape == (
        Data.dimF,
    ), 'Dimension of the inbound cost vector is incorrect (∑|F|)'

    # Outbound cost vector dimension = (∑|FxC|)
    assert outbound_cost_vector.shape == (
        Data.dimFC,), 'Dimension of the outbound cost vector is incorrect (' \
                      '∑|FxC|)'

    # Horizontally stack inbound and outbound cost into row vectors
    Data.objective_vector = np.hstack(
        [inbound_cost_vector, outbound_cost_vector])

    # Verify positivity
    assert np.all(
        Data.objective_vector > 0), 'Objective vector must be positive'


def generate_demand_matrix():
    """
    Inputs from data.py
    -------------------
    Data.customer_sizes: dict
        Dictionary containing the number of customer for all products

    Data.factory_sizes: dict
        Dictionary containing the number of factories for all products

    Data.product_list: list
        List of products to optimize

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimC: int
        Σ|C| (total number of customers across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Outputs to data.py
    ------------------
    Data.demand_matrix: numpy.ndarray
        Demand matrix to realize customers' demand, made by horizontally
        concatenate the inbound and outbound demand matrix.

    """

    # Verify inputs type
    assert isinstance(Data.customer_sizes,
                      dict), 'Customer sizes must be given in a dictionary'
    assert isinstance(sum(Data.customer_sizes.values()),
                      int), 'Customer sizes values must be integers'
    assert isinstance(Data.factory_sizes,
                      dict), 'Factory sizes values must be a dictionary'
    assert isinstance(sum(Data.factory_sizes.values()),
                      int), 'Factory sizes values must be integers'
    assert isinstance(Data.product_list,
                      list), 'Product list must be given in a list (Duhh!?)'

    # Verify inputs values
    assert np.all(np.array(list(Data.customer_sizes.values())) > 0
                  ), 'Customer sizes must be positive'

    assert np.all(np.array(list(Data.factory_sizes.values())) > 0
                  ), 'Factory sizes must be positive'

    # Verify input length
    assert len(Data.product_list) > 0, 'Number of products in list to ' \
                                       'optimize must be positive'
    assert (len(Data.customer_sizes) == len(Data.product_list)), \
        'Number of products in customer sizes is incorrect'
    assert (len(Data.factory_sizes) == len(Data.product_list)), \
        'Number of products in factory sizes is incorrect'

    # Reshape dictionary inputs into matrices
    # Construct zero inbound cost matrix (Σ|C|, Σ|F|)
    inbound_demand_matrix = np.zeros(
        (Data.dimC, Data.dimF))  # Demand Inbound Block

    # Construct block diagonal outbound cost matrix (Σ|C|, Σ|FxC|)
    outbound_demand_matrix = block_diag(*[
        np.tile(np.eye(Data.customer_sizes[product]),
                reps=Data.factory_sizes[product])
        for product in Data.product_list
    ])  # Demand Outbound Block

    # Verify output dimension
    # Outbound demand matrix dimension = (Σ|C|, Σ|FxC|)
    assert outbound_demand_matrix.shape == (Data.dimC, Data.dimFC), \
        'Dimension of outbound demand matrix is incorrect (Σ|C|, Σ|FxC|)'

    # Horizontally stack inbound and outbound block into the full demand matrix
    Data.demand_matrix = np.hstack(
        [inbound_demand_matrix, outbound_demand_matrix])

    # Verify non-negative
    assert np.all(
        Data.demand_matrix >= 0), 'Demand matrix must be non-negative'


def generate_combination_matrices():
    """
    Inputs to data.py
    -----------------
    Data.efficiency_per_product: dict
        Dictionary of efficiency of all factories for all products

    Data.factory_names: dict
        Dictionary of factory names for all products

    Data.product_list: list
        List of products to optimize

    Data.factory_list: list
        List of factories to optimize

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Outputs to data.py
    ------------------
    Data.inbound_combination_matrices: dict
        Dictionary of block diagonal matrices containing the production
        efficiency of a factory {product: associated matrix}. Each
        product corresponds to a matrix with:
            - #Columns: ∑|F| (total number of factories across all products)
            - #Rows: # Factories (total number of factories)

    Data.outbound_combination_matrices: dict
        Dictionary of block diagonal matrices to apply outbound constraints
        on a per-factory basis. {product: associated matrix}. Each product
        corresponds to a matrix with:
            - #Column: ∑|FxC| (total number of factories x customers
            across all products)
            - #Rows: # Factories (total
            number of factories)
    """

    # Verify inputs type
    assert isinstance(
        Data.efficiency_per_product,
        dict), 'Efficiency per product must be given in a dictionary'
    assert isinstance(Data.factory_names,
                      dict), 'Factory names must be given in a dictionary'

    # Verify inputs values
    assert len(
        Data.product_list) > 0, 'Number of products in list to ' \
                                'optimize must be positive'
    assert len(Data.factory_list
               ) > 0, 'Number of factories in list to optimize must be ' \
                      'positive'
    assert np.all(np.hstack(list(Data.efficiency_per_product.values())) > 0
                  ), 'Efficiency must be positive'
    assert np.all(
        np.array([len(prod) for prod in
                  Data.factory_names.values()]) >= 0), 'There are no ' \
                                                       'factories to ' \
                                                       'optimize for some ' \
                                                       'products!'
    assert np.all(
        np.array([len(prod) for prod in Data.factory_names.values()]) <= len(
            Data.factory_list)), 'There are more factory names than allowed'

    # Build the combination matrix
    """
    Starting from the inside out, we first 
    iterate over all the product. 
    For a given product "p", we put the 
    corresponding efficiency value  
    in the place of the factories that produce 
    the product and [] in the 
    place of factories that don't. Then, 
    we form each product into a block 
    using the block_diag function. After which, 
    we build the matrix using 
    block_diag on all the previous blocks. 
    Lastly, add a negative sign per
    the model.
    """

    # Generator to iterate over efficiency elements
    efficiency_array = (
        eff_arr
        for eff_arr in np.hstack(list(Data.efficiency_per_product.values())))

    inbound_combination_matrix = -block_diag(*[
        block_diag(*block) for block in [[
            next(efficiency_array)
            if factory in Data.factory_names[product] else []
            for factory in Data.factory_list
        ] for product in Data.product_list]
    ])
    """
    Starting from the inside out, we first iterate over all the product. 
    For a given product "p", we put a list [1 * #customer buying "p"] 
    in the place of the factories that product and [] in the place of 
    factories that don't. Then, we form each product into a block using
    the block_diag function. After which, we build the matrix using 
    block_diag on all the previous blocks.
    """

    outbound_combination_matrix = block_diag(*[
        block_diag(*block)
        for block in [
            [
                [1] * Data.customer_sizes[product]
                if factory in Data.factory_names[product] else []
                for factory in Data.factory_list]
            for product in Data.product_list
        ]
    ])

    # Verify matrix dimension
    # Inbound combination matrix dimension == (Σ#Fx#P, Σ|C|)
    assert inbound_combination_matrix.shape == (
        len(Data.factory_list) * len(Data.product_list), Data.dimF
    ), 'Dimension of inbound combination matrix is incorrect (Σ#Fx#P, Σ|F|)'

    # Outbound combination matrix dimension == (Σ#Fx#P, Σ|FxC|)
    assert outbound_combination_matrix.shape == (
        len(Data.factory_list) * len(Data.product_list),
        Data.dimFC), 'Dimension of combination matrix is incorrect (Σ#Fx#P, ' \
                     'Σ|FxC|)'

    # Split the matrix into dictionary
    # Inbound combination dictionary
    Data.inbound_combination_matrices = dict(
        zip(
            Data.product_list,
            np.split(inbound_combination_matrix,
                     len(Data.product_list),
                     axis=0)))

    # Outbound combination dictionary
    Data.outbound_combination_matrices = dict(
        zip(
            Data.product_list,
            np.split(outbound_combination_matrix,
                     len(Data.product_list),
                     axis=0)))


def generate_capacity_matrix():
    """
    Inputs to data.py
    -----------------
    Data.capacity_constraints: list
        List of capacity constraints for by product combinations

    Data.inbound_combination_matrices: dict
        Dictionary of inbound combination matrices for all products

    Data.outbound_combination_matrices: dict
        Dictionary of outbound combination matrices for all products

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Outputs to data.py
    ------------------
    Data.capacity_matrix: numpy.ndarray
        Capacity matrix to realize the factories' production capacity,
        made by concatenating the inbound and outbound capacity matrix.

    Data.capacity_rows: int
        Dimension of the capacity part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.

    """

    # Verify inputs types
    assert isinstance(Data.capacity_constraints,
                      list), 'Capacity constraints must be in a list'

    assert isinstance(
        Data.inbound_combination_matrices,
        dict), 'Inbound combination matrices must be in a dictionary'

    assert isinstance(
        Data.outbound_combination_matrices,
        dict), 'Outbound combination matrices must be in a dictionary'

    # Verify for the case cap_cons = []
    assert len(Data.capacity_constraints
               ) > 0, 'At least one capacity constraints must be defined'

    # Verify for the case cap_cons = [[1, 2], []] (The [] is not allowed)
    assert np.all(
        np.array([len(cons) for cons in Data.capacity_constraints]) > 0
    ), 'Capacity constraints cannot be empty'

    # Verify for the case cap_cons = [[1, 2], [1, 2]] (the [1, 2] cannot
    # repeat)
    # and also that order doesn't matter ([1, 2] is equivalent to [2, 1])
    orderless_capacity_constraints = [
        sorted(cons) for cons in Data.capacity_constraints
    ]

    assert len({
        tuple(cons)
        for cons in orderless_capacity_constraints
    }) == len(orderless_capacity_constraints
              ), 'Capacity constraints (in any order) cannot repeat'

    # Verify for the case cap_cons = [[1, 2], [0, 0]] (the [0, 0] is not
    # allowed)
    assert np.all(
        np.array([len(set(cons)) for cons in Data.capacity_constraints]) ==
        np.array([len(cons) for cons in Data.capacity_constraints])
    ), 'A single product combination cannot appear more than once in one ' \
       'constraints'

    # Verify that the capacity combinations are in the original product_list
    assert set(reduce(lambda a, b: a + b, Data.capacity_constraints)).issubset(
        set(Data.product_list)), (
            'Capacity combinations list not valid. ' +
            'Some products are not in the defined product list')

    # Build the capacity matrix
    # First build the outbound matrix by adding up all the capacity constraints
    outbound_capacity_matrix = np.vstack([
        np.sum(
            [Data.outbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.capacity_constraints
    ])
    # Strip away all-zeros rows
    outbound_capacity_matrix = outbound_capacity_matrix[
        ~np.all(outbound_capacity_matrix == 0, axis=1)]

    # Then we build the all zero inbound matrix with the same number of rows
    # as the outbound matrix
    inbound_capacity_matrix = np.zeros(
        (outbound_capacity_matrix.shape[0], Data.dimF))

    # Verify output dimensions
    # Find the number of distinct factories over all the capacity constraints
    Data.capacity_rows = sum([
        len(
            reduce(lambda a, b: a.union(b),
                   [set(Data.factory_names[prod]) for prod in cons]))
        for cons in Data.capacity_constraints
    ])

    # Outbound capacity dimension == (Data.capacity_rows, Σ|FxC|)
    assert outbound_capacity_matrix.shape == (
        Data.capacity_rows, Data.dimFC
    ), 'Dimension of outbound capacity matrix is incorrect (' \
       'Data.capacity_rows, Σ|FxC|)'

    # Horizontally stack the inbound and outbound section to form the full
    # capacity matrix
    Data.capacity_matrix = np.hstack(
        [inbound_capacity_matrix, outbound_capacity_matrix])


def generate_supply_matrix():
    """
    Inputs to data.py
    -----------------
    Data.supply_constraints: list
        List of supply constraints for by product combinations

    Data.inbound_combination_matrices: dict
        Dictionary of inbound combination matrices for all products

    Data.outbound_combination_matrices: dict
        Dictionary of outbound combination matrices for all products

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Outputs to data.py
    ------------------
    Data.supply_matrix: numpy.ndarray
        Supply matrix to realize the factories' production supply,
        made by concatenating the inbound and outbound supply matrix.

    Data.supply_rows: int
        Dimension of the supply part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.


    """

    # Verify inputs types
    assert isinstance(
        Data.inbound_combination_matrices,
        dict), 'Inbound combination matrices must be in a dictionary'

    assert isinstance(
        Data.outbound_combination_matrices,
        dict), 'Outbound combination matrices must be in a dictionary'

    assert isinstance(Data.supply_constraints,
                      list), 'Supply constraints must be in a list'

    # Verify for the case sup_cons = []
    assert len(Data.supply_constraints
               ) > 0, 'At least one supply constraints must be defined'

    # Verify for the case sup_cons = [[1, 2], []] (The [] is not allowed)
    assert np.all(
        np.array([len(cons) for cons in Data.supply_constraints]) > 0
    ), 'supply constraints cannot be empty'

    # Verify for the case sup_cons = [[1, 2], [1, 2]] (the [1, 2] cannot
    # repeat)
    # and also that order doesn't matter ([1, 2] is equivalent to [2, 1])
    orderless_supply_constraints = [
        sorted(cons) for cons in Data.supply_constraints
    ]

    assert len({
        tuple(cons)
        for cons in orderless_supply_constraints
    }) == len(orderless_supply_constraints
              ), 'supply constraints (in any order) cannot repeat'

    # Verify for the case sup_cons = [[1, 2], [0, 0]] (the [0, 0] is not
    # allowed)
    assert np.all(
        np.array([len(set(cons)) for cons in Data.supply_constraints]) ==
        np.array([len(cons) for cons in Data.supply_constraints])
    ), 'A single product combination cannot appear more than once in one ' \
       'constraints'

    # Verify that the supply combinations are in the original product_list
    assert set(reduce(lambda a, b: a + b, Data.supply_constraints)).issubset(
        set(Data.product_list)), (
            'supply combinations list not valid. ' +
            'Some products are not in the defined product list')

    # Build the supply matrix
    # First build the inbound matrix by adding up all the supply constraints
    inbound_supply_matrix = np.vstack([
        np.sum(
            [Data.inbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.supply_constraints
    ])
    # Strip away all-zeros rows
    inbound_supply_matrix = inbound_supply_matrix[
        ~np.all(inbound_supply_matrix == 0, axis=1)]

    # Then build the outbound matrix by adding up all the supply constraints
    outbound_supply_matrix = np.vstack([
        np.sum(
            [Data.outbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.supply_constraints
    ])
    # Strip away all-zeros rows
    outbound_supply_matrix = outbound_supply_matrix[
        ~np.all(outbound_supply_matrix == 0, axis=1)]

    # Verify output dimensions
    # Find the number of distinct factories over all the supply constraints
    Data.supply_rows = sum([
        len(
            reduce(lambda a, b: a.union(b),
                   [set(Data.factory_names[prod]) for prod in cons]))
        for cons in Data.supply_constraints
    ])

    # Inbound supply dimension == (Data.supply_rows, Σ|F|)
    assert inbound_supply_matrix.shape == (
        Data.supply_rows, Data.dimF
    ), 'Dimension of inbound supply matrix is incorrect (Data.supply_rows, ' \
       'Σ|F|)'

    # Outbound supply dimension == (Data.supply_rows, Σ|FxC|)
    assert outbound_supply_matrix.shape == (
        Data.supply_rows, Data.dimFC
    ), 'Dimension of outbound supply matrix is incorrect (Data.supply_rows, ' \
       'Σ|FxC|)'

    # Horizontally stack the inbound and outbound section to form the full
    # supply matrix
    Data.supply_matrix = np.hstack(
        [inbound_supply_matrix, outbound_supply_matrix])


def generate_constraints_matrix():
    """
    Inputs to data.py
    -----------------
    Data.demand_matrix: numpy.ndarray
        Demand matrix to realize customers' demand, made by horizontally
        concatenate the inbound and outbound demand matrix.

    Data.capacity_matrix: numpy.ndarray
        Capacity matrix to realize the factories' production capacity,
        made by concatenating the inbound and outbound capacity matrix.

    Data.supply_matrix: numpy.ndarray
        Supply matrix to realize the factories' production supply,
        made by concatenating the inbound and outbound supply matrix.

    Data.dimF: int
        Σ|F| (total number of factories across all products)

    Data.dimC: int
        Σ|C| (total number of customers across all products)

    Data.dimFC: int
        Σ|FxC| (total number of factories x customers across all products)

    Data.capacity_rows: int
        Dimension of the capacity part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.

    Data.supply_rows: int
        Dimension of the supply part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.

    Outputs to data.py
    ------------------
    Data.constraints_matrix: numpy.ndarray
        Constraints matrix to implement demand, capacity, supply constraints
    """

    Data.constraints_matrix = np.vstack([Data.demand_matrix,
                                         Data.capacity_matrix,
                                         Data.supply_matrix])

    assert Data.constraints_matrix.shape == (Data.dimC + Data.capacity_rows
                                             + Data.supply_rows, Data.dimF +
                                             Data.dimFC), 'Constraints ' \
                                                          'matrix dimension ' \
                                                          'is incorrect, ' \
                                                          '(Σ|C| + #cap_rows ' \
                                                          '' \
                                                          '' \
                                                          '' \
                                                          '' \
                                                          '+ # sup_rows, ' \
                                                          'Σ|F| + Σ|FxC|)'

    assert Data.constraints_matrix.shape == Data.constraints_matrix[
                                            :, ~np.all(
        Data.constraints_matrix == 0, axis=0)
                                            ][
        ~np.all(Data.constraints_matrix == 0, axis=1)
    ].shape, 'Constraints matrix contains columns or rows with all zeros'


def generate_constraints_vector():
    """
    Inputs from data.py:
    --------------------
    Data.demand_volume: numpy.ndarray
        Vector defining the demand constraints associated with
        the demand matrix.
        #Dimension: Σ|C| (number of customers across all products)

    Data.capacity_volume: numpy.ndarray
        Vector defining the capacity constraints associated with
        the capacity matrix
        #Dimension: #cap_rows (calculate by taking the union of all
        the factories across all products)

    Data.dimC: int
        Σ|C| (number of customers across all products)

    Data.capacity_rows: int
        Dimension of the capacity part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.

    Data.supply_rows: int
        Dimension of the supply part of the constraints vector,
        calculate by taking the union of all the factories across
        all products.

    Outputs to data.py:
    -------------------
    Data.constraints_vector: numpy.ndarray
        Vector associated with the constraints matrix, defining
        the constraints for demand, capacity and supply.
        #Dimension: Σ|C| + #cap_rows + #sup_rows (number of rows
        of the constraints matrix)

    """

    # Verify inputs type
    assert isinstance(
        Data.demand_volume,
        np.ndarray), 'Demand constraints vector must be a numpy array'

    assert isinstance(
        Data.capacity_volume,
        np.ndarray), 'Capacity constraints vector must be a numpy array'

    # Verify inputs dimension
    assert np.all(
        np.array([Data.dimC, Data.capacity_rows, Data.supply_rows]) > 0
    ), 'Dimension of a section of the constraints vector must be positive'

    assert Data.demand_volume.shape == (
        Data.dimC,
        1), 'Dimension of demand constraints vector is incorrect (∑|C|, 1)'

    assert Data.capacity_volume.shape == (
        Data.capacity_rows, 1
    ), 'Dimension of capacity constraints vector is incorrect (#caps_rows, 1)'

    # Verify inputs value
    assert np.all(Data.demand_volume > 0), 'Demand volume has to be positive'

    assert np.all(
        Data.capacity_volume > 0), 'Capacity volume has to be positive'

    # Stack the subvectors into the full constraints vector
    Data.constraints_vector = np.vstack([
        Data.demand_volume, Data.capacity_volume,
        np.zeros((Data.supply_rows, 1))
    ])

    # Verify output dimension
    assert Data.constraints_vector.shape == (
        Data.dimC + Data.capacity_rows + Data.supply_rows,
        1), 'Constraints vector is incorrect (Σ|C| + #cap_rows + #sup_rows)'


def optimize():
    pass
