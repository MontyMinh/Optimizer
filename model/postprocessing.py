from model import *
from model.data import Data, Results


def postprocess():
    """
    Unpack the program results into a volume vector
    and a cost vector.

    Input from data.py
    ------------------
    Data.linear_program: scipy.optimize.optimize.OptimizeResult
        Result of the linear program.

    Outputs to data.py
    ------------------
    Results.volume: list
        List of customers' volumes by optimization instances
    Results.cost: list
        List of customers' costs by optimization instances
    Results.split: int
        Index to split the above vector into inbound / outbound
    """
    # Unpack Volume
    Results.volume.append(Data.linear_program[:, np.newaxis])

    # Unpack Cost
    Results.cost.append(
        (Data.linear_program * Data.objective_vector)[:, np.newaxis])

    # Collect split index, to remove Data dependencies.
    # Next step is to free up all the memory from Data.
    Results.split = Data.dimF


def save_to_excel():
    """
    Method to save volume and cost data to Excel file

    Inputs from data.py
    -------------------
    Results.save_location: str (filepath)
        Path to save output Excel file
    Results.volume: list
        List of customers' volume by optimization instances
    Results.cost: list
        List of customers' cost by optimization instances
    """

    def quick_save(df, name): return df.to_excel(
        writer, name, index=False, header=True, startrow=0, startcol=0)

    # Generate the inbound template
    inbound_prefix = pd.DataFrame(data=np.vstack([
        np.hstack([Data.factory_names[prod] for prod in Data.product_list]),
        np.hstack([[prod for elem in Data.factory_names[prod]]
                   for prod in Data.product_list])
    ]).T,
        columns=['Factory', 'Product'])

    # Generate the outbound template
    df = pd.read_excel(Data.filepath,
                       sheet_name="Customer List")
    outbound_prefix = pd.DataFrame(data=np.vstack([
        np.repeat(df[df['Sales Product'] == prod][[
            'Customer ID', 'Sales Product', 'Province'
        ]].to_numpy(),
            repeats=Data.factory_sizes[prod],
            axis=0) for prod in Data.product_list
    ]),
        columns=['ID', 'Product', 'Province'])

    # Calculate the list of years
    Results.years = np.arange(Data.timeframe[0], Data.timeframe[1]+1)

    with pd.ExcelWriter(Results.save_location) as writer:

        # Inbound Volume
        df = inbound_prefix.copy()
        df[Results.years] = np.hstack(
            Results.volume)[:Results.split]
        df = df[df[Results.years].sum(axis=1) != 0]
        quick_save(df, 'Inbound Volume Per Factory')

        # Inbound Cost
        df = inbound_prefix.copy()
        df[Results.years] = np.hstack(
            Results.cost)[:Results.split]
        df = df[df[Results.years].sum(axis=1) != 0]
        quick_save(df, 'Inbound Cost Per Factory')

        # Outbound Volume
        df = outbound_prefix.copy()
        # Concatenate with the volume per year
        df[Results.years] = np.hstack(
            Results.volume)[Results.split:]
        # Remove all zeros rows
        df = df[df[Results.years].sum(axis=1) != 0]
        quick_save(df, 'Outbound Volume Per Customer')

        # Outbound Cost
        df = outbound_prefix.copy()
        # Concatenate with the volume per year
        df[Results.years] = np.hstack(
            Results.cost)[Results.split:]
        # Remove all zeros rows
        df = df[df[Results.years].sum(axis=1) != 0]
        quick_save(df, 'Outbound Cost Per Customer')


def free_memory():
    """Free memory by deleting some Data attributes"""

    # Free up memory
    keep = ["filepath", "factory_sizes",
            "factory_names", "product_list",
            "timeframe"]
    _ = [
        delattr(Data, attr) for attr in dir(Data)
        if (attr[:2] != '__') and (attr not in keep)
    ]
    del _
    gc.collect()
