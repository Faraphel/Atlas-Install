import ast
from typing import TYPE_CHECKING, Iterable, Callable

from source.safe_eval import better_safe_eval_error
from source.safe_eval.macros import replace_macro
from source.safe_eval.safe_function import get_all_safe_functions
from source.translation import translate as _


if TYPE_CHECKING:
    from source import TemplateSafeEval, Env


safe_eval_cache: dict[hash, Callable] = {}


class SafeEvalException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


# dict of every value used by every safe_eval call
all_globals = {
    "__builtins__": {},
} | {
    func.__name__: func for func in get_all_safe_functions()
}


def safe_eval(template: "TemplateSafeEval", env: "Env" = None, macros: dict[str, "TemplateSafeEval"] = None,
              args: Iterable[str] = None) -> Callable:
    """
    Run a python code in an eval function, but avoid all potential dangerous function.
    :env: additional variables that will be used when evaluating the template
    :lambda_args: arguments that the final lambda function can receive
    :macros: dictionary associating a macro name to a macro value

    :return: the lambda expression
    """
    global safe_eval_cache

    if len(template) == 0: return lambda *_, **__: ""
    if env is None: env = {}
    if macros is None: macros = {}
    args = tuple(args) if args is not None else ()  # allow the argument to be any iterable

    template_key: hash = hash((template, args, tuple(env.items())))  # unique identifiant for every template
    # if the safe_eval return a callable and have already been called, return the cached callable
    if template_key in safe_eval_cache: return safe_eval_cache[template_key]

    # replace the macro in the template
    template = replace_macro(template=template, macros=macros)
    # escape backslash to avoid unreadable expression
    template = template.replace("\\", "\\\\")

    # prepare the execution environment
    globals_ = all_globals | env
    locals_ = {}

    # convert the template to an ast expression
    stmt: ast.stmt = ast.parse(template, feature_version=(3, 10)).body[0]
    if not isinstance(stmt, ast.Expr):
        raise SafeEvalException(_("ERROR_INVALID_AST_TYPE") % type(stmt).__name__)

    # check every node for disabled expression
    for node in ast.walk(stmt):
        match type(node):

            # when accessing any attribute
            case ast.Attribute:
                # ban all magical function, disabling the __class__.__bases__[0] ... tricks
                if "__" in node.attr:
                    raise SafeEvalException(_("ERROR_FORBIDDEN_MAGIC_ATTRIBUTE") % node.attr)

                # ban modification to environment
                if isinstance(node.ctx, ast.Store):
                    raise SafeEvalException(_("ERROR_CANNOT_SET_ATTRIBUTE") % node.attr)

            # when accessing any variable
            case ast.Name:
                # ban modification to environment, but allow custom variable to be changed
                if isinstance(node.ctx, ast.Store):
                    if node.id in globals_ | locals_:
                        raise SafeEvalException(_("ERROR_CANNOT_SET_ENVIRONMENT") % node.id)
                    elif node.id in args:
                        raise SafeEvalException(_("ERROR_CANNOT_SET_ARGUMENT") % node.id)

            # when assigning a value with ":="
            case ast.NamedExpr:
                # embed the value into a deepcopy, to avoid interaction with class attribute
                node.value = ast.Call(
                    func=ast.Name(id="copy", ctx=ast.Load()),
                    args=[node.value], keywords=[],
                )

            case ast.Call:
                if isinstance(node.func, ast.Attribute):  # if this is a method
                    if not isinstance(node.func.value, ast.Constant):  # if the method is not on a constant
                        raise SafeEvalException(_("ERROR_CAN_ONLY_CALL_CONSTANT_METHOD"))

                elif isinstance(node.func, ast.Name):  # if this is a direct function call
                    if node.func.id not in globals_ | locals_:  # if the function is not in env
                        raise SafeEvalException(_("ERROR_CAN_ONLY_CALL_ENV_FUNCTION"))

                else:  # else don't allow the function call
                    raise SafeEvalException(_("ERROR_CAN_ONLY_CALL_ENV_FUNCTION"))

            # Forbidden type. Some of them can't be accessed with the eval mode, but just in case, still ban them
            case (
                ast.Assign | ast.AugAssign |    # Assign should only be done by ":=" with check in eval
                ast.Raise | ast.Assert |        # Error should not be raised manually
                ast.Delete |                    # Value should not be deleted
                ast.Import | ast.ImportFrom |   # Import could lead to extremely dangerous functions
                ast.Lambda | ast.FunctionDef |  # Defining functions can allow skipping some check
                ast.Global | ast.Nonlocal |     # Changing variables range could cause some issue
                ast.ClassDef |                  # Declaring class could maybe allow for dangerous calls
                ast.AsyncFor | ast.AsyncWith | ast.AsyncFunctionDef | ast.Await |  # Just in case
                # comprehension are extremely dangerous since their can associate value
                ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
            ):
                raise SafeEvalException(_("ERROR_FORBIDDEN_SYNTAX") % type(node).__name__)

    # embed the whole expression into a lambda expression
    stmt.value = ast.Lambda(
        body=stmt.value,
        args=ast.arguments(
            args=[ast.arg(arg=arg) for arg in args],
            posonlyargs=[], kwonlyargs=[],
            kw_defaults=[], defaults=[],
        )
    )

    # convert into a ast.Expression, object needed for the compilation
    expression: ast.Expression = ast.Expression(stmt.value)

    # if a node have been altered, fix the missing locations
    ast.fix_missing_locations(expression)

    # return the evaluated formula
    lambda_template = eval(compile(expression, "<safe_eval>", "eval"), globals_, locals_)
    safe_eval_cache[template_key] = lambda_template  # cache the callable for potential latter call
    return better_safe_eval_error(lambda_template, template=template)
