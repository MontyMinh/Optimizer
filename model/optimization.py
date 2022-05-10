from model import *
from model.modeldata import Data


def generate_objective_vector():
    """
    Output to modeldata.py
    -----------------
    Data.inbound_cost_vector: numpy.ndarray
        Dimension: ΣF_u (total number of factories across all products)
        Major Order: 1.product, 2.factory

    Data.outbound_cost_vector: numpy.ndarray
        Dimension: Σ(FxC)_u (total number of (factories x customers) across
        all products)
        Major Order: 1.product, 2.factory, 3.customer

    Data.objective_vector: numpy.ndarray
        Objective vector to minimize function value

    """

    # Verify inputs
    assert isinstance(Data.inbound_cost_per_product,
                      dict), 'Inbound costs must be positive'
    assert isinstance(Data.outbound_cost_per_product,
                      dict), 'Outbound costs must be positive'

    # Reshape dictionary inputs into vectors
    ## Unpack inbound cost dictionary and stack into row vector
    Data.inbound_cost_vector = np.hstack(
        list(Data.inbound_cost_per_product.values()))

    ## Unpack outbound cost dictionary in factory-then-customer major
    Data.outbound_cost_vector = np.hstack(
        [prod.flatten('F') for prod in Data.outbound_cost_per_product.values()])

    # Verify vector dimensions
    ## Inbound cost vector dimension = (∑|F|)
    assert Data.inbound_cost_vector.shape == (
        Data.dimF,), 'Dimension of the inbound cost vector is incorrect (∑|F|)'

    ## Outbound cost vector dimension = (∑|FxC|)
    assert Data.outbound_cost_vector.shape == (
        Data.dimFC,), 'Dimension of the outbound cost vector is incorrect (∑|FxC|)'

    # Horizontally stack inbound and outbound cost into row vectors
    Data.objective_vector = np.hstack([Data.inbound_cost_vector,
                                      Data.outbound_cost_vector])