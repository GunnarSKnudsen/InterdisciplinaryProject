# load pickles from tests arguments
from eventstudystatistics import adjBMP, grank
import numpy as np

params = (np.random.random((10000, 41)), np.random.random((10000, 100)), np.random.random((10000, 100)), np.random.random((10000, 41)), [0, 19] )

grank(*params)
adjBMP(*params)

# Profile this to see how long it takes to run