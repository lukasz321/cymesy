from typing import List, Set, Dict, Tuple, Optional


def get_current_file_dir():
    import pathlib

    return pathlib.Path(__file__).parent.absolute()


def get_current_working_dir():
    import pathlib

    return pathlib.Path().absolute()


def write_inline(filepath: str, seeked_text: str, new_line: str) -> bool:
    """
    Substitute a line in a text file.
    """
    import fileinput

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


def add_environment_var(variable: str, value: str):
    """
    Add environment variable to /etc/environment or whatever.
    """
    env_var_file = "/etc/environment"

    substituted = write_inline(
        filepath=env_var_file, seeked_text=variable, new_line=f'{variable}="{value}"'
    )

    if not substituted:
        with open(env_var_file, "a+") as f:
            new_var = f'{variable}="{value}"'
            f.write(new_var)
            f.flush()

        print(f"Appended {new_var} to /etc/environment.")

    print(f"\nRe-exporting environment variables...")
    os.system(
        "for env in $( cat /etc/environment ); do export $(echo $env | sed -e 's/\"//g'); done"
    )
    print("Done")


def load_config_yaml() -> Dict:
    """
    Load config.yaml located in the same directory.
    """
    import os, yaml

    p = os.path.realpath(__file__).rsplit("/", 1)[0]
    f = open(os.path.join(p, "config.yaml"), "r")
    config = yaml.safe_load(f)
    f.close()


def stitch_lists(keys, values) -> Dict:
    """
    Stitch two lists into a dict.
    """
    return dict(zip(keys, values))


def get_own_ip_address() -> str:
    """
    Figure out own IP address that isn't localhost.
    """
    import socket, subprocess

    ip_address = "127.0.0.1"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except:
        pass
    finally:
        s.close()

    # In case the socket method fails...
    if ip_address.startswith("127"):
        output = subprocess.check_output(["hostname", "-i"])
        if output:
            output = output.decode("utf-8")
            ip_address = output.split(" ")[0]

    if ip_address.startswith("127"):
        return None
    else:
        return ip_address


def system_command(cmd: str) -> Tuple[int, str, str]:
    """
    Run a blocking system command.
    Return status, stdout, stderr.
    """
    import shlex
    import subprocess

    try:
        args = shlex.split(cmd)
        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        )

        stdout, stderr = proc.communicate(cmd)
        status = proc.wait()
    except:
        status = -1
        stdout = stderr = None

    return status, stdout, stderr
