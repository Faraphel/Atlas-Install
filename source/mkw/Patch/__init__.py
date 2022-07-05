from pathlib import Path


class PathOutsidePatch(Exception):
    def __init__(self, forbidden_path: Path, allowed_range: Path):
        super().__init__(f"Error : path {forbidden_path} outside of allowed range {allowed_range}")


class InvalidPatchMode(Exception):
    def __init__(self, mode: str):
        super().__init__(f"Error : mode \"{mode}\" is not implemented")


class InvalidPatchOperation(Exception):
    def __init__(self, operation: str):
        super().__init__(f"Error : operation \"{operation}\" is not implemented")


class InvalidImageLayerType(Exception):
    def __init__(self, layer_type: str):
        super().__init__(f"Error : layer type \"{layer_type}\" is not implemented")

# TODO : implement BMG
# TODO : recreate SZS

configuration_example = {
    "operation": {  # other operation for the file
        "bmg-replace": {
            "mode": "regex",  # regex or id
            "template": {
                "CWF": "{{ ONLINE_SERVICE }}",  # regex type expression
                "0x203F": "{{ ONLINE_SERVICE }}"  # id type expression
            }
        }
    }
}
