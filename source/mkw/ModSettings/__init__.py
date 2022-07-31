from source.mkw.ModSettings.TypeSettings import AbstractTypeSettings


class InvalidSettingsType(Exception):
    def __init__(self, settings_type: str):
        super().__init__(f"Error : Type of mod settings '{settings_type}' not found.")


class ModSettings:
    def __new__(cls, settings_dict: dict) -> dict[str, AbstractTypeSettings]:
        """
        Load all the settings in mod_settings_dict
        :param settings_dict: dictionnary containing all the settings defined for the mod
        """
        settings: dict[str, AbstractTypeSettings] = {}

        for settings_name, settings_data in settings_dict.items():
            for subclass in filter(
                    lambda subclass: subclass.type == settings_data["type"], AbstractTypeSettings.__subclasses__()
            ):
                settings_data.pop("type")
                settings[settings_name] = subclass(**settings_data)
                break
            else: raise InvalidSettingsType(settings_name)

        return settings
