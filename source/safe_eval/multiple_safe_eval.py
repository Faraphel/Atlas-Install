import re

from source.safe_eval import safe_eval


TOKEN_START, TOKEN_END = "{{", "}}"


def multiple_safe_eval(template: str, env: dict[str, any] = None, macros: dict[str, str] = None) -> str:
    """
    Similar to safe_eval, but expression need to be enclosed between "{{" and "}}".
    Example : "{{ track.author }} is the track creator !"
    """

    def format_part_template(match: re.Match) -> str:
        """
        when a token is found, replace it by the corresponding value
        :param match: match in the format
        :return: corresponding value
        """
        # get the token string without the brackets, then strip it. Also double antislash
        part_template = match.group(1).strip()
        return str(safe_eval(template=part_template, env=env, macros=macros))

    # pass everything between TOKEN_START and TOKEN_END in the function
    return re.sub(rf"{TOKEN_START}(.*?){TOKEN_END}", format_part_template, template)
