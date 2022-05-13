from model import *
from model.data import Data


def generate_objective_vector():
    """
    Output to data.py
    ----------------------
    Data.inbound_cost_vector: numpy.ndarray
        Dimension: Σ|F| (total number of factories across all products)
        Major Order: 1.product, 2.factory

    Data.outbound_cost_vector: numpy.ndarray
        Dimension: Σ|FxC| (total number of factories x customers across
        all products)
        Major Order: 1.product, 2.factory, 3.customer

    Data.objective_vector: numpy.ndarray
        Objective vector to minimize function value

    """

    # Verify inputs
    assert isinstance(Data.inbound_cost_per_product,
                      dict), 'Inbound costs must be given in a dictionary'
    assert isinstance(Data.outbound_cost_per_product,
                      dict), 'Outbound costs must be given in a dictionary'

    # Verify length of dictionary
    print(f'{Data.product_list}')
    print(f'{Data.inbound_cost_per_product.keys()}')
    print(f'{Data.outbound_cost_per_product.keys()}')
    assert (len(Data.inbound_cost_per_product) == len(Data.product_list)), \
        'Number of products in Inbound cost per product is incorrect'
    assert (len(Data.outbound_cost_per_product) == len(Data.product_list)), \
        'Number of products in Outbound cost per product is incorrect'

    # Reshape dictionary inputs into vectors
    # Unpack inbound cost dictionary and stack into row vector
    Data.inbound_cost_vector = np.hstack(
        list(Data.inbound_cost_per_product.values()))

    # Unpack outbound cost dictionary in factory-then-customer major
    Data.outbound_cost_vector = np.hstack(
        [prod.flatten('F') for prod in
         Data.outbound_cost_per_product.values()])

    # Verify output dimension
    # Inbound cost vector dimension = (∑|F|)
    assert Data.inbound_cost_vector.shape == (
        Data.dimF,), 'Dimension of the inbound cost vector is incorrect (∑|F|)'

    # Outbound cost vector dimension = (∑|FxC|)
    assert Data.outbound_cost_vector.shape == (
        Data.dimFC,), 'Dimension of the outbound cost vector is incorrect (' \
                      '∑|FxC|)'

    # Horizontally stack inbound and outbound cost into row vectors
    Data.objective_vector = np.hstack([Data.inbound_cost_vector,
                                       Data.outbound_cost_vector])

    # Verify positivity
    assert np.all(
        Data.objective_vector > 0), 'Objective vector must be positive'


def generate_demand_matrix():
    """
    Output to data.py
    ----------------------
    Data.inbound_demand_matrix: numpy.ndarray
        All zeros matrix for the inbound section of the demand matrix.
        #Rows: Σ|C| (total number of customer across all products)
        #Columns: Σ|F| (total number of factories across
        all products)
        Major order: 1.product, 2.factory, 3.customer

    Data.outbound_demand_matrix: numpy.ndarray
        Block diagonal matrix for the outbound section of the demand matrix.
        #Rows: Σ|C| (total number of customer across all products)
        #Columns: Σ|FxC| (total number of factories x customer across
        all products)

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
    assert (len(Data.customer_sizes) == len(Data.product_list)), \
        'Number of products in customer sizes is incorrect'

    assert (len(Data.factory_sizes) == len(Data.product_list)), \
        'Number of products in factory sizes is incorrect'

    # Reshape dictionary inputs into matrices
    # Construct zero inbound cost matrix (Σ|C|, Σ|F|)
    Data.inbound_demand_matrix = np.zeros(
        (Data.dimC, Data.dimF))  # Demand Inbound Block

    # Construct block diagonal outbound cost matrix (Σ|C|, Σ|FxC|)
    Data.outbound_demand_matrix = block_diag(*[
        np.tile(np.eye(Data.customer_sizes[product]),
                reps=Data.factory_sizes[product])
        for product in Data.product_list
    ])  # Demand Outbound Block

    # Verify output dimension
    # Outbound demand matrix dimension = (Σ|C|, Σ|FxC|)
    assert Data.outbound_demand_matrix.shape == (Data.dimC, Data.dimFC), \
        'Dimension of outbound demand matrix is incorrect (Σ|C|, Σ|FxC|)'

    # Horizontally stack inbound and outbound block into the full demand matrix
    Data.demand_matrix = np.hstack(
        [Data.inbound_demand_matrix, Data.outbound_demand_matrix])

    # Verify non-negative
    assert np.all(
        Data.demand_matrix >= 0), 'Demand matrix must be non-negative'


def generate_combination_matrices():
    """
    Output to data.py
    ----------------------
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
    assert len(Data.factory_list
               ) > 0, 'Number of factories to optimize must be positive'
    assert np.all(np.hstack(list(Data.efficiency_per_product.values())) > 0
                  ), 'Efficiency must be positive'
    assert np.all(
        np.array([len(prod) for prod in Data.factory_names.values()]) <= len(
            Data.factory_list)), 'There are more factory names than allowed'

    # Build the combination matrix
    """
    Starting from the inside out, we first iterate over all the product. 
    For a given product "p", we put the corresponding efficiency value  
    in the place of the factories that produce the product and [] in the 
    place of factories that don't. Then, we form each product into a block 
    using the block_diag function. After which, we build the matrix using 
    block_diag on all the previous blocks. Lastly, add a negative sign per
    the model.
    """

    # Generator to iterate over efficiency elements
    efficiency_array = (
        eff_arr
        for eff_arr in np.hstack(list(Data.efficiency_per_product.values())))

    Data.inbound_combination_matrix = -block_diag(*[
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

    Data.outbound_combination_matrix = block_diag(*[
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
    assert Data.inbound_combination_matrix.shape == (
        len(Data.factory_list) * len(Data.product_list), Data.dimF
    ), 'Dimension of inbound combination matrix is incorrect (Σ#Fx#P, Σ|F|)'

    # Outbound combination matrix dimension == (Σ#Fx#P, Σ|FxC|)
    assert Data.outbound_combination_matrix.shape == (
        len(Data.factory_list) * len(Data.product_list),
        Data.dimFC), 'Dimension of combination matrix is incorrect (Σ#Fx#P, ' \
                     'Σ|FxC|)'

    # Split the matrix into dictionary
    # Inbound combination dictionary
    Data.inbound_combination_matrices = dict(
        zip(
            Data.product_list,
            np.split(Data.inbound_combination_matrix,
                     len(Data.product_list),
                     axis=0)))

    # Outbound combination dictionary
    Data.outbound_combination_matrices = dict(
        zip(
            Data.product_list,
            np.split(Data.outbound_combination_matrix,
                     len(Data.product_list),
                     axis=0)))


def generate_capacity_matrix():
    """
    Output to data.py
    ----------------------
    Data.inbound_capacity_matrix: numpy.ndarray
        All zero matrix representing the inbound
        section of the joint capacity constraints.
        #Rows: Depends on the number constraints and the
        intersection of factories in each of the joint combination
        #Columns: ∑|F| (total number of factories across all products)

    Data.outbound_capacity_matrix: numpy.ndarray
        Sum of the outbound combination matrices, use to represent the
        joint constraints on capacity of factories. For example, to
        limit the capacity of bulk + bag, we add the bulk matrix to
        the bag matrix.
        #Rows: Depends on the number constraints and the
        intersection of factories in each of the joint combination,
        but will be the same as the inbound capacity matrix.
        #Columns: ∑|FxC| (total number of factories x customers
        across all products)

    Data.capacity_matrix: numpy.ndarray
        Capacity matrix to realize the factories' production capacity,
        made by concatenating the inbound and outbound capacity matrix.

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
    Data.outbound_capacity_matrix = np.vstack([
        np.sum(
            [Data.outbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.capacity_constraints
    ])
    # Strip away all-zeros rows
    Data.outbound_capacity_matrix = Data.outbound_capacity_matrix[
        ~np.all(Data.outbound_capacity_matrix == 0, axis=1)]

    # Then we build the all zero inbound matrix with the same number of rows
    # as the outbound matrix
    Data.inbound_capacity_matrix = np.zeros(
        (Data.outbound_capacity_matrix.shape[0], Data.dimF))

    # Verify output dimensions
    # Find the number of distinct factories over all the capacity constraints
    Data.capacity_rows = sum([
        len(
            reduce(lambda a, b: a.union(b),
                   [set(Data.factory_names[prod]) for prod in cons]))
        for cons in Data.capacity_constraints
    ])

    # Outbound capacity dimension == (Data.capacity_rows, Σ|FxC|)
    assert Data.outbound_capacity_matrix.shape == (
        Data.capacity_rows, Data.dimFC
    ), 'Dimension of outbound capacity matrix is incorrect (' \
       'Data.capacity_rows, Σ|FxC|)'


def generate_supply_matrix():
    """
    Output to data.py
    ----------------------
    Data.inbound_supply_matrix: numpy.ndarray
        Sum of the inbound combination matrices, use to represent the
        joint constraints on supply of factories. For example, to
        limit the inbound supply of bulk + bag, we add the bulk matrix
        to the bag matrix.
        #Rows: Depends on the number constraints and the
        intersection of factories in each of the joint combination,
        but will be the same as the outbound supply matrix.
        #Columns: ∑|F| (total number of factories across all products)

    Data.outbound_supply_matrix: numpy.ndarray
        Sum of the outbound combination matrices, use to represent the
        joint constraints on supply of factories. For example, to
        limit the outbound supply of bulk + bag, we add the bulk matrix
        to the bag matrix.
        #Rows: Depends on the number constraints and the
        intersection of factories in each of the joint combination,
        but will be the same as the inbound supply matrix.
        #Columns: ∑|FxC| (total number of factories x customers
        across all products)

    Data.supply_matrix: numpy.ndarray
        Supply matrix to realize the factories' production supply,
        made by concatenating the inbound and outbound supply matrix.

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
    Data.inbound_supply_matrix = np.vstack([
        np.sum(
            [Data.inbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.supply_constraints
    ])
    # Strip away all-zeros rows
    Data.inbound_supply_matrix = Data.inbound_supply_matrix[
        ~np.all(Data.inbound_supply_matrix == 0, axis=1)]

    # Then build the outbound matrix by adding up all the supply constraints
    Data.outbound_supply_matrix = np.vstack([
        np.sum(
            [Data.outbound_combination_matrices[prod] for prod in combination],
            axis=0) for combination in Data.supply_constraints
    ])
    # Strip away all-zeros rows
    Data.outbound_supply_matrix = Data.outbound_supply_matrix[
        ~np.all(Data.outbound_supply_matrix == 0, axis=1)]

    # Verify output dimensions
    # Find the number of distinct factories over all the supply constraints
    Data.supply_rows = sum([
        len(
            reduce(lambda a, b: a.union(b),
                   [set(Data.factory_names[prod]) for prod in cons]))
        for cons in Data.supply_constraints
    ])

    # Inbound supply dimension == (Data.supply_rows, Σ|F|)
    assert Data.inbound_supply_matrix.shape == (
        Data.supply_rows, Data.dimF
    ), 'Dimension of inbound supply matrix is incorrect (Data.supply_rows, ' \
       'Σ|F|)'

    # Outbound supply dimension == (Data.supply_rows, Σ|FxC|)
    assert Data.outbound_supply_matrix.shape == (
        Data.supply_rows, Data.dimFC
    ), 'Dimension of outbound supply matrix is incorrect (Data.supply_rows, ' \
       'Σ|FxC|)'
