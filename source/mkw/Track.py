from typing import Generator
import re

from source.mkw import Tag, Slot

TOKEN_START = "{{"
TOKEN_END = "}}"

common_token_map = {  # these operators and function are considered safe to use in the template
   operator: operator
   for operator in
   ["+", "-", "*", "/", "%", "**", ",", "(", ")", "[", "]", "==", "!=", "in", ">", "<", ">=", "<=", "and", "or", "&",
    "|", "^", "~", "<<", ">>", "not", "is", "if", "else", "abs", "int", "bin", "hex", "oct", "chr", "ord", "len",
    "str", "bool", "float", "round", "min", "max", "sum", "zip", "any", "all", "issubclass", "reversed", "enumerate",
    "list", "sorted", "hasattr", "for", "range", "type", "isinstance", "repr", "None", "True", "False"
    ]

} | {  # these methods are considered safe, except for the magic methods
   f".{method}": f".{method}"
   for method in dir(str) + dir(list) + dir(int) + dir(float)
   if not method.startswith("__")
}


class TokenParsingError(Exception):
    def __init__(self, token: str):
        super().__init__(f"Invalid token while parsing track representation:\n{token}")


# representation of a custom track
class Track:
    def __init__(self, special: Slot = None, music: Slot = None, tags: list[Tag] = None, weight: int = None, **kwargs):
        self.special: Slot = special if special is not None else "T11"
        self.music: Slot = music if music is not None else "T11"
        self.tags: list[Tag] = tags if tags is not None else []
        self.weight: int = weight if weight is not None else 1

        # others not mandatory attributes
        for key, value in kwargs.items():
            # if the attribute start with __, this is a magic attribute, and it should not be modified
            if key.startswith("__"): continue
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, track_dict: dict) -> "Track | TrackGroup":
        """
        create a track from a dict, or create a track group is it is a group
        :param track_dict: dict containing the track information
        :return: Track
        """
        if "group" in track_dict:
            from source.mkw.TrackGroup import TrackGroup
            return TrackGroup.from_dict(track_dict)
        return cls(**track_dict)

    def get_tracks(self) -> Generator["Track", None, None]:
        """
        Get all the track elements
        :return: track elements
        """
        for _ in range(self.weight):
            yield self

    def repr_format(self, mod_config: "ModConfig", format: str) -> str:
        """
        return the representation of the track from the format
        :param mod_config: configuration of the mod
        :return: formatted representation of the track
        """

        token_map = common_token_map | {  # replace the suffix and the prefix by the corresponding values
            "prefix": self.get_prefix(mod_config, ""),
            "suffix": self.get_prefix(mod_config, ""),
        } | {  # replace the track attribute by the corresponding values
                        f"track.{attr}": f"track.{attr}" for attr, value in self.__dict__.items()
                    } | {  # replace the track variable by the corresponding value, if not used with an attribute
                        "track": "track"
                    }

        def format_token(match: re.Match) -> str:
            # get the token string without the brackets, then strip it
            process_token = match.group(1).strip()
            final_token: str = ""

            def matched(match: re.Match | str | None, value: str = None) -> bool:
                """
                check if token is matched, if yes, add it to the final token and remove it from the processing token
                :param match: match object
                :param value: if the match is a string, the value to replace the text with
                :return: True if matched, False otherwise
                """
                nonlocal final_token, process_token

                # if there is no match or the string is empty, return False
                if not match: return False

                if isinstance(match, re.Match):
                    process_token_raw = process_token[match.end():]
                    value = match.group()

                else:
                    if not process_token.startswith(match): return False
                    process_token_raw = process_token[len(match):]

                process_token = process_token_raw.lstrip()

                final_token += value + (len(process_token_raw) - len(process_token)) * " "

                return True

            while process_token:  # while there is still tokens to process
                # if the section is a string, add it to the final token
                # example : "hello", "hello \" world"
                if matched(re.match(r'^\"(?:[^"\\]|\\.)*\"', process_token)):
                    continue

                # if the section is a float or an int, add it to the final token
                # example : 102, 102.59
                if matched(re.match(r'^[0-9]+(?:\.[0-9]+)?', process_token)):
                    continue

                # if the section is a variable, operator or function, replace it by its value
                # example : track.special, +
                for key, value in token_map.items():
                    if matched(key, value):
                        break

                # else, the token is invalid, so raise an error
                else:
                    raise TokenParsingError(process_token)

            # if final_token is set, eval final_token and return the result
            if final_token:
                return str(eval(final_token, {}, {"track": self}))
            else:
                return final_token

        # pass everything between TOKEN_START and TOKEN_END in the function
        return re.sub(rf"{TOKEN_START}(.*?){TOKEN_END}", format_token, format)

    def get_prefix(self, mod_config: "ModConfig", default: any = None) -> any:
        """
        return the prefix of the track
        :param default: default value if no prefix is found
        :param mod_config: mod configuration
        :return: formatted representation of the track prefix
        """
        for tag in filter(lambda tag: tag in mod_config.tags_prefix, self.tags):
            return mod_config.tags_prefix[tag]
        return default

    def get_suffix(self, mod_config: "ModConfig", default: any = None) -> any:
        """
        return the suffix of the track
        :param default: default value if no suffix is found
        :param mod_config: mod configuration
        :return: formatted representation of the track suffix
        """
        for tag in filter(lambda tag: tag in mod_config.tags_suffix, self.tags):
            return mod_config.tags_suffix[tag]
        return default

    def get_highlight(self, mod_config: "ModConfig", default: any = None) -> any:
        ...
