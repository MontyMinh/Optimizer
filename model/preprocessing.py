from model import *
from model.data import Data


def get_timeframe():
    """
    Get optimization timeframe

    Outputs to data.py
    ------------------
    Data.timeframe: list
        - Pull from "Timeframe"

    """
    Data.timeframe = list(pd.read_excel(Data.filepath).iloc[0])

    assert Data.timeframe[1] - \
        Data.timeframe[0] >= 1, 'Timeframe not in ascending order'


def raw_inputs():
    """
    Pull data from input Excel files.

    Below only includes a shortlist of attributes used
    and the sheet where the data comes from. For detailed
    documentation, see Attributes.txt

    Outputs to data.py
    ------------------
    Data.product_list: list
        - Pull from "Product List"

    Data.factory_list: list
        - Pull from "Factory List"

    Data.factory_names: dict
        - Pull from "Factory Per Product"

    Data.inbound_cost_per_product: dict
        - Pull from "Inbound Cost Per Product"

    Data.demand_volume: numpy.ndarray
        - Pull from "Sales Volume"

    Data.outbound_cost_per_product: dict
        - Pull from "Outbound Cost"

    Data.efficiency_per_product: dict
        - Pull from "Efficiency Per Product"

    Data.capacity_constraints: list
        - Pull from "Capacity Constraints"

    Data.supply_constraints: list
        - Pull from "Supply Constraints"

    Data.capacity_volume: numpy.ndarray
        - Pull from "Capacity Volume"

    """
    # Data.product_list
    Data.product_list = pd.read_excel(
        Data.filepath, sheet_name='Product List')['PRODUCT'].values.tolist()

    # Data.factory_list
    Data.factory_list = pd.read_excel(
        Data.filepath, sheet_name='Factory List')['FACTORY'].values.tolist()

    # Data.factory_name/s (df temporary stores the work sheet)
    df = pd.read_excel(Data.filepath,
                       sheet_name='Factory Per Product',
                       index_col=0)

    Data.factory_names = {
        prod: [fac for fac in df.columns[df.loc[prod]]
               if str(Data.year) in fac]
        for prod in Data.product_list
    }

    del df

    # Data.inbound_cost_per_product
    df = pd.read_excel(Data.filepath,
                       sheet_name='Inbound Cost Per Product',
                       index_col=0)

    Data.inbound_cost_per_product = {
        prod: df.loc[prod][Data.factory_names[prod]].tolist()
        for prod in Data.product_list
    }

    del df

    # Data.outbound_cost_per_product
    df = pd.read_excel(Data.filepath, sheet_name='Outbound Cost', index_col=0)

    Data.outbound_cost_per_product = {
        prod: df[df['Sales Product'] ==
                 prod][Data.factory_names[prod]].to_numpy().flatten('F')
        for prod in Data.product_list
    }

    # Data.demand_volume
    df = pd.read_excel(Data.filepath, sheet_name='Sales Volume', index_col=0)

    Data.demand_volume = np.hstack([
        df[df['Sales Product'] == prod][df.columns[
            2 + Data.year - Data.timeframe[0]]].to_numpy().flatten('F')
        for prod in Data.product_list
    ])[:, np.newaxis]

    del df

    # Data.efficiency_per_product
    df = pd.read_excel(Data.filepath,
                       sheet_name='Efficiency Per Product',
                       index_col=0)

    Data.efficiency_per_product = {
        prod: df.loc[prod][Data.factory_names[prod]].tolist()
        for prod in Data.product_list
    }

    del df

    # Data.capacity_constraints # Constraints has to start index from 1
    df = pd.read_excel(Data.filepath,
                       sheet_name='Capacity Constraints',
                       index_col='CONSTRAINT')

    df_prod = pd.DataFrame(
        columns=[prod for prod in df.columns
                 if str(Data.year) in prod]).columns

    Data.capacity_constraints = [
        df_prod[df[df_prod].iloc[cons]].to_list()
        for cons in range(df.shape[0])
    ]

    del df

    # Data.supply_constraints # Constraints has to start index from 1
    df = pd.read_excel(Data.filepath,
                       sheet_name='Supply Constraints',
                       index_col='CONSTRAINT')

    df_prod = pd.DataFrame(
        columns=[prod for prod in df.columns
                 if str(Data.year) in prod]).columns

    Data.supply_constraints = [
        df_prod[df[df_prod].iloc[cons]].to_list()
        for cons in range(df.shape[0])
    ]

    del df, df_prod

    # Data.capacity_volume
    Data.capacity_volume = pd.read_excel(
        Data.filepath, sheet_name='Capacity Volume',
        index_col='CONSTRAINT')[[str(Data.year) + " - " + str(fac)
                                for fac in Data.factory_list
                                 ]].to_numpy().flatten()

    Data.capacity_volume = Data.capacity_volume[~np.isnan(Data.capacity_volume
                                                          )][:, np.newaxis]

    # Revert the factory_names to simple no year names
    Data.factory_names = {prod: [fac.strip(str(Data.year) + " - ")
                                 for fac in Data.factory_names[prod]]
                          for prod in Data.factory_names}

    # Revert capacity constraints
    Data.capacity_constraints = [
        [prod.strip(str(Data.year) + " - ") for prod in cons]
        for cons in Data.capacity_constraints]

    # Revert supply constraints
    Data.supply_constraints = [
        [prod.strip(str(Data.year) + " - ") for prod in cons]
        for cons in Data.supply_constraints]


def processed_inputs():
    """
    Data processed from Raw Inputs

    Outputs to data.py
    ------------------
    Data.factory_sizes: dict
        - Process from Data.factory_names

    Data.customer_sizes: dict
        - Process from ...

    Data.dimF: int
        - Process from Data.factory_sizes

    Data.dimC: int
        - Process from Data.customer_sizes

    Data.dimFC: int
        - Process from Data.factory_sizes x Data.customer_sizes

    """

    # Data.factory_sizes
    Data.factory_sizes = {
        prod: len(Data.factory_names[prod])
        for prod in Data.product_list
    }

    # Data.customer_sizes (Pending changes)
    # Might want to do Data.customer_list and Data.customer_names
    # as well, for the postprocessing

    Data.customer_sizes = {
        prod:
            len(Data.outbound_cost_per_product[prod]) // Data.factory_sizes[
                prod]
        for prod in Data.product_list
    }

    # Data.dimF
    Data.dimF = sum(Data.factory_sizes.values())

    # Data.dimC
    Data.dimC = sum(Data.customer_sizes.values())

    # Data.dimFC
    Data.dimFC = sum(
        np.array(list(Data.factory_sizes.values())) *
        np.array(list(Data.customer_sizes.values())))


def preprocess():
    """
    Call on the raw and processed inputs, then checks if the inputs.
    are logical through a series of assert statement.

    After doing this,
    if we get an error in an assert statement, we know the values is wrong,
    else we know that the input is not the correct format.

    """
    # Retrieve the inputs
    raw_inputs()
    processed_inputs()

    # Assert logicality of inputs
