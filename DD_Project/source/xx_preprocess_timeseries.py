import pandas as pd

from os import listdir
from os.path import isfile, join


def preprocess_timeseries(_raw_location, _preprocessed_location):
    # List of files to process
    filenames = [f for f in listdir(_raw_location) if isfile(join(_raw_location, f))]

    # So far, nothing to preprocess, so just copying the files
    for f in filenames:
        print(f'Processing {f}')
        file_content = pd.read_csv(_raw_location + f, index_col=0)
        file_content.to_csv(_preprocessed_location + f)
