import json

# load settings file
def load_settings():
    with open("input_data/settings.json", 'r') as f:
        settings = json.load(f)
    return settings