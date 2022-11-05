import json
import pandas as pd
import datetime
import numpy as np

# load settings file
def load_settings():
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