from model import *
from model.preprocessing import *
from model.optimization import *
from model.postprocessing import *


def execute():
    """Execute the Optimizer from end to end"""

    # Get timeframe
    get_timeframe()

    for Data.year in range(Data.timeframe[0], Data.timeframe[1]+1):

        # Run program
        preprocess()  # preprocessing
        optimize()  # optimization
        postprocess()  # postprocess

        # Free up memory
        free_memory()

    # Save data
    save_to_excel()
