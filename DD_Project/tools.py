import json
import pandas as pd
import datetime
import numpy as np

# load settings file
def load_settings():
    """
    Read the settings from correct JSON file, as defined in main.py
    """
    with open("input_data/settings.json", 'r') as f:
        settings = json.load(f)

    ip = settings["investigation_periods"]
    for key in ip:
        ip[key] = (pd.Timestamp(ip[key][0]), pd.Timestamp(ip[key][1]))

    settings["investigation_periods"] = ip


    settings["start_time"] = datetime.datetime(*settings["start_time"])
    settings["end_time"] = datetime.datetime(*settings["end_time"])

    cp = settings["CAR_periods"]
    for key in cp:
        cp[key] = np.asarray(cp[key])

    settings["CAR_periods"] = cp


    return settings

def bold_rows(x):
    """
    Helper for generating prettier output for report
    """
    lenx = x.shape[0]-1
    return ['font-weight: bold' if (v == x.loc[lenx]) else '' for v in x]

def display_table(df, label="table:excluded_companies", caption="Summary of discarded input", column_format=None):
    """
    Helper for generating prettier output for report
    """
    settings = load_settings()
    if not settings["df_latex"]:
        return df

    # check if dataframe has multiindex
    if isinstance(df.index, pd.MultiIndex):
        return df.to_latex(label=label, caption=caption, column_format=column_format)

    return df.style\
.apply(bold_rows)\
.applymap_index(lambda v: "font-weight: bold;", axis="index")\
.applymap_index(lambda v: "font-weight: bold;", axis="columns")\
.format(na_rep="-", precision=1)\
.hide(axis="index")\
.format(thousands=",")\
.format_index(escape="latex", axis=1)\
.to_latex(convert_css=True
          , column_format=column_format
          , position="H"
          , position_float="centering"
          , hrules=True
          , label=label
          , caption=caption
          , multirow_align="t"
          , multicol_align="r"
          #, index = False
          , siunitx = True
)