import os
import json

class ConfigWrapper:
    def __init__(self, config_data):
        self._data = config_data

    def get(self, section, key, default=None):
        return self._data.get(section, {}).get(key, default)

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return ConfigWrapper(config_data)
