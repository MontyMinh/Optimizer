from model import *
from model.data import Data, Results


def unpack_results():
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

    quick_save = lambda df, name: df.to_excel(
        writer, name, index=False, header=True, startrow=0, startcol=0)

    # Generate the outbound template
    df = pd.read_excel(Data.filepath,
                       sheet_name="Sales Volume & Outbound Cost")
    outbound_prefix = pd.DataFrame(data=np.vstack([
        np.repeat(df[df['Sales Product'] == prod][[
            'Customer ID', 'Sales Product', 'Province'
        ]].to_numpy(),
                  repeats=Data.factory_sizes[prod],
                  axis=0) for prod in Data.product_list
    ]),
                                   columns=['ID', 'Product', 'Province'])
    
    outbound_prefix['Factory'] = np.hstack([
        Data.factory_names[prod] * Data.customer_sizes[prod]
        for prod in Data.product_list
    ])
    
    Results.years = np.arange(2021, 2021+len(Results.volume))

    with pd.ExcelWriter(Results.save_location) as writer:

        # Inbound Volume
        '''quick_save(
            np.hstack(Results.volume)[:Results.split],
            'Inbound Volume Per Customer')'''

        # Outbound Volume
        df = outbound_prefix.copy()
        # Concatenate with the volume per year
        df[Results.years] = np.hstack(
            Results.volume)[Results.split:]
        # Remove all zeros rows
        df = df[df[Results.years].sum(axis = 1) != 0]
        quick_save(df, 'Outbound Volume Per Customer')

        # Inbound Cost
        '''quick_save(
            np.hstack(Results.cost)[:Results.split],
            'Inbound Cost Per Customer')'''

        # Outbound Cost
        df = outbound_prefix.copy()
        # Concatenate with the volume per year
        df[Results.years] = np.hstack(
            Results.cost)[Results.split:]
        # Remove all zeros rows
        df = df[df[Results.years].sum(axis = 1) != 0]
        quick_save(df, 'Outbound Cost Per Customer')
        
        del df


def postprocess():
    """Run postprocess methods"""

    unpack_results()

    # Free up memory
    keep = ["filepath", "factory_sizes", 
            "factory_names", "customer_sizes", 
            "product_list"]
    _ = [
        delattr(Data, attr) for attr in dir(Data)
        if (attr[:2] != '__') and (attr not in keep)
    ]
    del _
    gc.collect()

    save_to_excel()