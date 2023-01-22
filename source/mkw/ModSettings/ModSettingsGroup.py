from source.mkw.ModSettings import AbstractModSettings


class ModSettingsGroup(dict):
    """
    Represent a group of mod settings
    """

    def __init__(self, d: dict) -> None:
        """
        Convert a json type dict into a mod settings dictionary
        :param d: the json dict
        :return: the new dictionary
        """
        super().__init__({name: AbstractModSettings.get(data) for name, data in d.items()})

    def export_values(self) -> dict[str, dict]:
        """
        Export the settings values into a dictionary
        :return: the settings values
        """
        return {key: value.export_value() for key, value in self.items()}

    def import_values(self, values_dict: dict[str, dict]) -> None:
        """
        Import values to the settings
        :param values_dict: the dictionary with the settings values
        """
        for name, values in values_dict.items():
            self[name].import_value(**values)
