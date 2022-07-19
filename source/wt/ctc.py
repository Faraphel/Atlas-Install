from source.wt import *

tools_path = tools_szs_dir / "wctct"


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def bmg_ctfile(ctfile: "Path | str") -> str:

    process = _tools_run_popen("BMG", "-", "--lecode")
    stdout, _ = process.communicate(input=ctfile.encode("utf-8"))
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout.decode("utf-8")
