import subprocess


class WSZSTError(Exception):
    def __init__(self, wszst_tools, error_id=0):
        error_message = subprocess.run([wszst_tools, "ERROR", str(error_id)],
                                       stdout=subprocess.PIPE, check=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW).stdout.decode()
        super().__init__(f"({wszst_tools}) Error ({error_id}) : {error_message}")


def better_wszst_error(wszst_tools):
    """
    raise a better message when an error occur while using one of the wiimm's tools.
    :param wszst_tools: tools used
    :return: function with better error when exception occur
    """
    def gen_wrapped_func(func):
        def wrapped_func(*args, **kwargs):
            """
            function that will be returned instead of the function, will call it in a thread
            :param func: function
            :param args: args of the original function
            :param kwargs: kwargs of the original function
            """
            try:
                return func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                raise WSZSTError(wszst_tools, e.returncode)

        return wrapped_func
    return gen_wrapped_func
