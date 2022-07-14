from source.wt import *

tools_path = tools_szs_dir / ("wstrt.exe" if system == "win64" else "wstrt")


_tools_run = get_tools_run_function(tools_path)
_tools_run_popen = get_tools_run_popen_function(tools_path)


def patch_data(dol_data: bytes, region: int = None, https: str = None, domain: str = None,
               sections: list[Path] = None) -> bytes:
    """
    Patch a main.dol file content
    :param https: can be RESTORE, HTTP, DOMAIN, SAKE0 or SAKE1. Allow for modifying url to custom server
    :param domain: if https is set to DOMAIN, url to the custom server
    :param sections: sections that can be added to manage cheat
    :param region: optional region for the game
    :param dol_data: main.dol file content
    :return: patched main.dol file content
    """
    args = []
    if region is not None: args.extend(["--region", region])
    if https is not None: args.extend(["--https", https])
    if domain is not None: args.extend(["--domain", domain])
    for section in sections if sections is not None else []:
        args.extend(["--add-section", section])

    process = _tools_run_popen("PATCH", "-", "--DEST", "-", "--clean-dol", "--add-lecode", *args)
    stdout, _ = process.communicate(input=dol_data)
    if process.returncode != 0:
        raise WTError(tools_path, process.returncode)

    return stdout
