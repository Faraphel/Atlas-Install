import ast
import copy

from source.safe_eval.macros import replace_macro
from source.safe_eval.safe_function import get_all_safe_functions


# TODO: exception class


# dict of every value used by every safe_eval call
all_globals = {
    "__builtins__": {},
    "deepcopy": copy.deepcopy
} | {
    func.__name__: func for func in get_all_safe_functions()
}


def safe_eval(template: str, env: dict[str, any] = None, macros: dict[str, str] = None,
              return_lambda: bool = False, lambda_args: list[str] = None) -> any:
    """
    Run a python code in an eval function, but avoid all potential dangerous function.
    :env: additional variables that will be used when evaluating the template
    :return_lambda: if enabled, return a lambda function instead of the result of the expression
    :lambda_args: arguments that the final lambda function can receive
    :macros: dictionary associating a macro name to a macro value

    :return: the evaluated expression or the lambda expression
    """

    if len(template) == 0: return ""
    if env is None: env = {}
    if macros is None: macros = {}

    # replace the macro in the template
    template = replace_macro(template=template, macros=macros)

    # escape backslash to avoid unreadable expression
    template = template.replace("\\", "\\\\")

    # prepare the execution environment
    globals_ = all_globals | env
    locals_ = {}

    # convert the template to an ast expression
    stmt: ast.stmt = ast.parse(template).body[0]
    if not isinstance(stmt, ast.Expr):
        raise Exception(f'Invalid ast type for safe_eval : "{type(stmt).__name__}"')

    # check every node for disabled expression
    for node in ast.walk(stmt):
        match type(node):

            # when accessing any attribute
            case ast.Attribute:
                # ban all magical function, disabling the __class__.__bases__[0] ... tricks
                if "__" in node.attr:
                    raise Exception(f'Magic attribute are forbidden : "{node.attr}"')

                # ban modification to environment
                if isinstance(node.ctx, ast.Store):
                    raise Exception(f'Can\'t set value of attribute : "{node.attr}"')

            # when accessing any variable
            case ast.Name:
                # ban modification to environment, but allow custom variable to be changed
                if isinstance(node.ctx, ast.Store) and node.id in globals_ | locals_:
                    raise Exception(f'Can\'t set value of environment : "{node.id}"')

            # when calling any function
            case ast.Call:
                # ban the function and method from the environment
                for callnode in ast.walk(node.func):
                    if isinstance(callnode, ast.Attribute):
                        for attrnode in ast.walk(callnode.value):
                            if isinstance(attrnode, ast.Name) and attrnode.id in globals_ | locals_:
                                raise Exception(f'Calling this function is not allowed : "{callnode.attr}"')

            # when assigning a value with ":="
            case ast.NamedExpr:
                # embed the value into a deepcopy, to avoid interaction with class attribute
                node.value = ast.Call(
                    func=ast.Name(id="deepcopy", ctx=ast.Load()),
                    args=[node.value], keywords=[],
                )

            # Forbidden type. Some of them can't be accessed with the eval mode, but just in case, still ban them
            case (
                ast.Assign | ast.AugAssign |    # Assign should only be done by ":=" with check in eval
                ast.Raise | ast.Assert |        # Error should not be raised manually
                ast.Delete |                    # Value should not be deleted
                ast.Import | ast.ImportFrom |   # Import could lead to extremely dangerous functions
                ast.Lambda | ast.FunctionDef |  # Defining functions can allow skipping some check
                ast.Global | ast.Nonlocal |     # Changing variables range could cause some issue
                ast.ClassDef |                  # Declaring class could maybe allow for dangerous calls
                ast.AsyncFor | ast.AsyncWith | ast.AsyncFunctionDef | ast.Await  # Just in case
            ):
                raise Exception(f'Forbidden syntax : "{type(node).__name__}"')

    if return_lambda:
        # if return_lambda is enabled, embed the whole expression into a lambda expression
        stmt.value = ast.Lambda(
            body=stmt.value,
            args=ast.arguments(
                args=[ast.arg(arg=lambda_arg) for lambda_arg in lambda_args],
                posonlyargs=[], kwonlyargs=[],
                kw_defaults=[], defaults=[],
            )
        )

    # convert into a ast.Expression, object needed for the compilation
    expression: ast.Expression = ast.Expression(stmt.value)

    # if a node have been altered, fix the missing locations
    ast.fix_missing_locations(expression)

    # return the evaluated formula
    return eval(compile(expression, "<safe_eval>", "eval"), globals_, locals_)
