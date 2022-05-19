"""
This folder contains the Python code of Model 4. It contains 4 files:

- preprocessing.py, file for collecting the data to run the optimization from
Excel sheets.
- optimization.py, file for setting up the linear program and optimize.
- postprocessing.py, file for calculating post-optimization metrics 
and arranging the output data back into Excel.
- program.py, file for running the entire program from start to finish.
- data.py, file for storing all the important program data.
- ui.py, file for hosting the user interface for interacting with the full
optimization program.

"""

import numpy as np
from scipy.linalg import block_diag
from scipy.optimize import linprog
from functools import reduce
import pandas as pd
import gc