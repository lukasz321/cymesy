import os
import fileinput

from typing import Tuple, Dict


async def exec_command_async(cmd: str) -> Tuple[int, str, str]:
    """ """
    import asyncio

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    # io streams are returned as unicode bytes, so decode to get strings
    stdout = stdout.decode("utf8", errors="ignore")
    stderr = stderr.decode("utf8", errors="ignore")

    return proc.returncode, stdout, stderr


def pipeable_command(cmd: str) -> Tuple[int, str, str]:
    import subprocess

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    ) as p:
        stdout, stderr = p.communicate()
        status = int(p.returncode)

    stdout = stdout.decode("utf8", errors="ignore")
    stderr = stderr.decode("utf8", errors="ignore")

    return status, stdout, stderr


def system_command(cmd: str) -> Tuple[int, str, str]:
    """
    IMPORTANT: this function does not support pipes.
    """
    import shlex
    import subprocess

    try:
        args = shlex.split(cmd)
        with subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        ) as p:

            stdout, stderr = p.communicate(cmd)
            status = p.wait()
    except Exception:
        status = -1
        stdout = stderr = None

    return status, stdout, stderr


def write_inline(filepath: str, seeked_text: str, new_line: str) -> bool:
    """
    Substitute a line with "new_line" if "seeked_text" is found.
    """
    substituted = False
    old_line = None
    for line in fileinput.input(filepath, inplace=1):
        if seeked_text in line:
            old_line = line
            line = new_line
            substituted = True

        print(line.rstrip())

    if substituted:
        print(f"Substituted {old_line.rstrip()} with {new_line.rstrip()}.")

    return substituted


def write_inline_env_vars(filepath: str, seeked_text: str, new_line: str) -> bool:
    """
    Substitute a line with "new_line" if "seeked_text" is found.
    This one looks for an EXACT match of an env variable...
    """
    substituted = False
    old_line = None
    for line in fileinput.input(filepath, inplace=1):
        if seeked_text == line.split("=", maxsplit=1)[0]:
            old_line = line
            line = new_line
            substituted = True

        print(line.rstrip())

    if substituted:
        print(f"Substituted {old_line.rstrip().split('=')[0]}")

    return substituted


def get_installed_package_version(pkg: str) -> Dict:
    command = f'python3 -c "import {pkg}; print({pkg}.__version__)"'
    status, stdout, stderr = system_command(command)
    if status == 0:
        installed_version = stdout.strip()
        # print(f"{pkg} version {installed_version}")
    else:
        installed_version = None
        # print(f'Cannot import package "{pkg}".')

    return {"pkg": pkg, "version": installed_version}


def set_environment_var(
    variable: str, value: str, env_var_file: str = "/etc/environment"
):
    """
    Set environment variable. If the variable already exists,
    substitute it with new value "value".
    """
    substituted = write_inline_env_vars(
        filepath=env_var_file, seeked_text=variable, new_line=f'{variable}="{value}"'
    )

    if not substituted:
        with open(env_var_file, "a") as f:
            new_var = f'{variable}="{value}"'
            f.write(new_var)
            f.flush()

        print(f"Appended {new_var.split('=')[0]} to {env_var_file}.")


def get_environment(env_var_file: str = "/etc/environment") -> Dict:
    """
    Dump all environment variables starting with MFG_.
    """
    with open(env_var_file, "r") as f:
        env_file = f.read()

    env_dict = dict()

    for line in env_file.split("\n"):
        line = line.replace('"', "").replace("'", "")
        if "MFG_" in line:
            mfg_var = line.split("=")
            env_dict[mfg_var[0]] = mfg_var[1]

    return env_dict
