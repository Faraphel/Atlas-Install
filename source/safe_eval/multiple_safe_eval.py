from typing import TYPE_CHECKING, Iterable, Callable

from source.safe_eval.safe_eval import safe_eval
from source.safe_eval import better_safe_eval_error

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval, TemplateSafeEval, Env


TOKEN_START, TOKEN_END = "{{", "}}"


def multiple_safe_eval(template: "TemplateMultipleSafeEval", env: "Env" = None,
                       macros: dict[str, "TemplateSafeEval"] = None, args: Iterable[str] = None) -> Callable:
    """
    Similar to safe_eval, but expression need to be enclosed between "{{" and "}}".
    Example : "{{ track.author }} is the track creator !"
    """

    lambda_templates: list[str | Callable] = []

    while len(template) > 0:
        token_start: int = template.find(TOKEN_START)  # the position of the "{{"
        part_template_start: int = token_start + len(TOKEN_START)  # the position just after the start token
        part_template_end: int = template.find(TOKEN_END)  # the position before the end token
        token_end: int = part_template_end + len(TOKEN_END)  # the end position of the "}}"

        # if there is no more template, add all the template into the lambda
        if token_start < 0 or part_template_end < 0:
            lambda_templates.append(template)
            template = ""

        # if there is still a template part, add the remaining text, then add the lambda template between the tokens.
        else:
            lambda_templates.append(template[:token_start])
            lambda_templates.append(safe_eval(
                    template=template[part_template_start:part_template_end].strip(),
                    env=env,
                    macros=macros,
                    args=args,
            ))
            template = template[token_end:]

    return better_safe_eval_error(lambda *args, **kwargs: "".join([
        str(part(*args, **kwargs)) if callable(part) else part
        for part in lambda_templates
    ]), template=template)


