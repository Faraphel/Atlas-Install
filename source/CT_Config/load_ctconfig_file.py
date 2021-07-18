import json


def load_ctconfig_file(self, ctconfig_file: str = "./ct_config.json"):
    """
    :param ctconfig_file: path to the ctconfig file
    :return: ?
    """
    with open(ctconfig_file, encoding="utf-8") as f:
        ctconfig_json = json.load(f)
    self.load_ctconfig_json(ctconfig_json)