from model import *
from model.data import Data, Results


def unpack_results():
    """
    Unpack the program results into a volume vector
    and a price vector.

    Input from data.py
    ------------------
    Data.linear_program: scipy.optimize.optimize.OptimizeResult
        Result of the linear program.

    Outputs to data.py
    ------------------
    Results.volume: list
        List of customers' volumes by optimization instances
    Results.price: list
        List of customers' prices by optimization instances
    Results.split: int
        Index to split the above vector into inbound / outbound
    """

    # Unpack Volume
    Results.volume.append(Data.linear_program[:, np.newaxis])

    # Unpack Price
    Results.price.append(
        (Data.linear_program * Data.objective_vector)[:, np.newaxis])

    # Collect split index, to remove Data dependencies.
    # Next step is to free up all the memory from Data.
    Results.split = Data.dimF


def delete_optimization_data():
    """Method to delete Data to free up memory"""

    del Data
    gc.collect()


def save_to_excel():
    """
    Method to save volume and price data to Excel file

    Inputs from data.py
    -------------------
    Results.save_location: str (filepath)
        Path to save output Excel file
    Results.volume: list
        List of customers' volume by optimization instances
    Results.price: list
        List of customers' price by optimization instances
    """

    quick_save = lambda array, name: pd.DataFrame(array).to_excel(
        writer, name, index=False, header=False, startrow=1, startcol=2)

    with pd.ExcelWriter(Results.save_location) as writer:
        quick_save(
            np.hstack(Results.volume)[:Results.split],
            'Inbound Volume Per Customer')
        quick_save(
            np.hstack(Results.volume)[Results.split:],
            'Outbound Volume Per Customer')
        quick_save(
            np.hstack(Results.price)[:Results.split],
            'Inbound Price Per Customer')
        quick_save(
            np.hstack(Results.price)[Results.split:],
            'Outbound Price Per Customer')


def postprocess():
    """Run postprocess methods"""

    unpack_results()
    delete_optimization_data()
    save_to_excel()