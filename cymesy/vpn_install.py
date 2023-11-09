"""
[TL;DR - RECOMMENDED FLOW]
On your server, run python3 vpn_install.py --server
Grab the output and on your client, run: xxx
Grab the output of the above, and back on your server run:

[SERVER SIDE] To merely bootstrap the server, run:
    python3 vpn_install.py --server
    Above command is executed whenevery any server action is run.

[SERVER SIDE] To "register" a new client/user:
    python3 vpn_install.py --server --client_ip CLIENT_IP --client_key CLIENT_KEY
    --client_ip and --client_key are generated on the client end. See more info below.

[CLIENT_SIDE] To create a new site/connection:
    python3 vpn_install.py --client --server_ip 177.1.1.9 --server_key abcdefg123klmn --site_name syr_office
    --server_key and --server_ip must be supplied by the server admin. See more info below.
    
    (alternatively) python3 vpn_install.py --client
    If the args from above aren't supplied the program will ask for your input along the way.


How do I find the server_key?
    First run python3 vpn_install.py --server on your server to bootstrap it. Then sudo cat /etc/wireguard/public.key.

How do I find the server_ip?
    On server's network - https://whatismyipaddress.com/

How do I find client_key?
    First run python3 vpn_install.py --client on your computer. Then sudo cat /etc/wireguard/public.key.

"""

import argparse
import subprocess
import ipaddress
import random
import os
from enum import Enum
import sys
from typing import List
import urllib.request

if not os.getuid() == 0:
    print("You must run this script as a superuser.")
    sys.exit(1)

#TODO
def print_connections():
    pass

class C(str, Enum):
    YLW = "\033[93m\033[1m"
    GRN = "\033[92m\033[1m"
    RED = "\033[91m\033[1m"
    CYN = "\033[96m\033[1m"
    END = "\033[0m\033[0m"


class Prompt:
    """
    Class helping operators interact with shell.
    Ask for input, ask for acknowledgement, prompt yes or no.

    Heavily influenced by click module.
    """

    CYAN = "\033[96m\033[1m"
    RED = "\033[91m\033[1m"
    GRAY = "\033[0m\033[1m"
    ENDC = "\033[0m\033[0m"

    @staticmethod
    def choose(prompt: str, options: List) -> str:
        """
        Ask user for input. Input is limited to the options provided
        as an argument. User must choose one of the options.

        Note that options are case sensitive.

        Returns
        -------
            user_input: str - one of the options provided as an arg
                              most likely a string/int
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        while True:
            print(f"Valid (case sensitive) options are: {options}")
            user_input = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} ")
            if user_input in options:
                return user_input

            print(f'"{user_input}" is not a valid option!')

    @staticmethod
    def confirm(prompt: str):
        """
        Prompt user to hit ENTER.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        _ = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} [ENTER]")

    @staticmethod
    def input(prompt: str) -> str:
        """
        Ask operator for input. Note that no input is accepted.

        Returns
        -------
            str: user_input - may be empty.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        user_input = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} ")
        return user_input

    @staticmethod
    def yes_no(prompt: str) -> bool:
        """
        Ask operator to choose "y" or "n" to prompt.

        Returns
        -------
            bool: True  - if operator chose "y"
            bool: False - if operator chose "n"
        """

        if prompt.endswith(":") or prompt.endswith("."):
            prompt = prompt[:-1]

        while True:
            user_input = input(
                f">> {Prompt.CYAN}{prompt} {Prompt.GRAY}[Y/n]{Prompt.ENDC}: "
            )
            if user_input:
                if user_input.lower() == "y":
                    return True
                if user_input.lower() == "n":
                    return False

            print(f'"{user_input}" is an invalid input! Enter "y" or "n".')


def install_prerequisites(args):
    """
    Install the required system packages for client/server.
    """

    print("Installing/updating required system packages...")
    packages = ["wireguard"]

    if args.client:
        packages.extend(["net-tools", "resolvconf"])

    for i, package in enumerate(packages):
        print(f"({i+1}/{len(packages)}): {package}")
        cmd = f"apt -qq list {package} 2>/dev/null | grep 'installed'"
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
            p.communicate()
            if p.returncode == 0:
                print("Already installed.")
                continue

        print("Installing...")
        cmd = f"sudo apt-get --yes install {package}"
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
            p.communicate()


def generate_public_private_keypair():
    """
    Valid for both client and the server. Skipped if both already exist.
    """

    if os.path.exists("/etc/wireguard/private.key") and os.path.exists(
        "/etc/wireguard/private.key"
    ):
        print("\nWireguard keys already exist. Skipping generation.\n")
    else:
        # Must be the very first time Wireguard is being set up.
        print("\nGenerating private-public key pair.")
        cmd = (
            "umask 077; wg genkey | sudo tee /etc/wireguard/private.key; "
            "sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key"
        )
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
            print(p.communicate())


def add_site(args):
    """
    To be run on client side only. Add a VPN connection/site.
    We need to know the following:
        server_ip   :   global IP of the VPN server
        server_key  :   server's /etc/wireguard/public.key
        site_name   :   what are we calling this connection?

    One configuration is complete, the client must ship some information
    to the server admin, namely:
        client_key  :   client's public key
        client_ip   :   client's randomly generated ip address
    """

    with open("/etc/wireguard/private.key", "r", encoding="utf-8") as f:
        private_key = f.read()

    server_ip = str(args.server_ip)

    gen_ip_addr = f"10.8.0.{random.randint(6, 255)}"
    content = (
        f"[Interface]\n"
        f"PrivateKey = {private_key}\n"
        f"Address = {gen_ip_addr}/24\n"
        f"PostUp = ip rule add table 200 from {server_ip}\n"
        f"PostUp = ip route add table 200 default via {server_ip}\n"
        f"PreDown = ip rule delete table 200 from {server_ip}\n"
        f"PreDown = ip route delete table 200 default via {server_ip}\n"
        "\n"
        "[Peer]\n"
        f"PublicKey = {args.server_key}\n"
        "AllowedIPs = 0.0.0.0/0, ::/0\n"
        f"Endpoint = {server_ip}:51820"
    )

    while True:
        if not args.site_name:
            args.site_name = Prompt.input(
                "How do you want to name this connection? ex. syr, factory, home, office...:"
            )

        if not os.path.exists(f"/etc/wireguard/{args.site_name}.conf"):
            break

        print(f'\nSite "{args.site_name}" already exists!')
        if Prompt.yes_no("Are you sure you want to override?"):
            break

        args.site_name = None

    with open(f"/etc/wireguard/{args.site_name}.conf", "w+") as f:
        f.write(content)

    with open("/etc/wireguard/public.key", "r") as f:
        public_key = f.read().rstrip()

    print(C.GRN + "\nShare the following client IP and public key with your VPN admin:" + C.END)
    print(gen_ip_addr)
    print(public_key)
    print(C.GRN + "\nOr simply share the following one-liner for use w/ this script:" + C.END)
    print(
        f"python3 vpn_install.py --server --client_ip {gen_ip_addr} --client_key {public_key}"
    )
    print(C.YLW + f"\nConnect to {args.site_name} via \"sudo wg-quick up {args.site_name}\"." + C.END)


def bootstrap_server():
    """
    To be run server only.

    This function appends appropriate info to config files and
    finishes with wireguard systemd service restart.
    """

    with open("/etc/wireguard/private.key", "r", encoding="utf-8") as f:
        private_key = f.read()

    if os.path.exists("/etc/wireguard/wg0.conf"):
        print("Server config already exists. Skipping.\n")
    else:
        # First time setting up wireguard, most likely.
        content = (
            "[Interface]\n"
            f"PrivateKey = {private_key}\n"
            "Address = 10.8.0.1/24\n"
            "ListenPort = 51820\n"
            "SaveConfig = true\n"
            "PostUp = ufw route allow in on wg0 out on eth0\n"
            "PostUp = iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE\n"
            "PostUp = ip6tables -t nat -I POSTROUTING -o eth0 -j MASQUERADE\n"
            "PreDown = ufw route delete allow in on wg0 out on eth0\n"
            "PreDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE\n"
            "PreDown = ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE\n"
        )
        with open("/etc/wireguard/wg0.conf", "w+", encoding="utf-8") as f:
            f.write(content)

    with open("/etc/sysctl.conf", "r", encoding="utf-8") as f:
        sysctl_conf = f.read()

    # setup ipv4 ip forwarding
    if "net.ipv4.ip_forward=1" in sysctl_conf:
        print("sysctl.conf already configured. Skipping.\n")
    else:
        with open("/etc/sysctl.conf", "a", encoding="utf-8") as f:
            f.write("net.ipv4.ip_forward=1")

    cmd = (
        "sudo ufw allow 51820/udp; "
        "sudo ufw allow OpenSSH; "
        "sudo systemctl enable wg-quick@wg0.service"
    )

    print("Opening 51820/udp and restarting the wireguard service...")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
        p.communicate()


def add_client(args):
    print("Adding client...")

    cmd = f"sudo wg set wg0 peer {args.client_key} allowed-ips {args.client_ip}"
    print(cmd)
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
        print(p.communicate())

    cmd = "sudo systemctl restart wg-quick@wg0.service"
    print(cmd)
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
        print(p.communicate())

    print("Done")


def delete_client():
    # TODO
    # "sudo wg show"
    pass
    os.system(
        f"sudo wg set wg0 peer PeURxj4Q75RaVhBKkRTpNsBPiPSGb5oQijgJsTa29hg= remove"
    )


def test_firewall():
    # check to see if firewall open
    # sudo nmap -sU -p 51820 192.168.9.196
    # TODO
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Wireguard")

    parser.add_argument(
        "--client",
        action="store_true",
        help="If you're setting up a Wireguard client.",
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="If you're setting up a Wireguard server.",
    )

    parser.add_argument(
        "--server_ip",
        type=ipaddress.ip_address,
        help="Required argument if you're a client.",
    )

    parser.add_argument(
        "--site_name",
        type=str,
        help="Required argument if you're a client.",
    )

    parser.add_argument(
        "--server_key",
        type=str,
        help="Required argument if you're a client.",
    )

    parser.add_argument(
        "--client_key",
        type=str,
        help="Required argument if you're on a server and adding a client.",
    )

    parser.add_argument(
        "--client_ip",
        type=ipaddress.ip_address,
        help="Required argument if you're on a server and adding a client.",
    )

    args = parser.parse_args()

    if args.client and args.server:
        # User is confused, and so are we. This cannot be both server and the client.
        print("You cannot pass --server and --client args together. That's confusing!")
        sys.exit(1)

    if not args.client and not args.server:
        # User has not passed neither client nor server flag.
        if Prompt.choose("Are you a server [S] or are you a client [C]?", ["S", "C"]) == "S":
            args.server = True
        else:
            args.client = True

    install_prerequisites(args)
    generate_public_private_keypair()

    if args.server:
        bootstrap_server()

    if args.client:
        if not args.server_ip:
            while True:
                print(
                    f"\nYou have not passed server's IP address (--server_ip).\n"
                    "You can look it up in the network controller it or simply "
                    'google "what is my ip address?" at the VPN (server) site.'
                )

                server_ip = Prompt.input("What is the IP of the VPN site?")
                try:
                    ipaddress.ip_address(server_ip)
                except ValueError:
                    print(f"Not a valid IP address!\n")
                else:
                    args.server_ip = server_ip
                    break

        if not args.server_key:
            print(
                f"\nYou have not passed server's public key (--server_key).\n"
                "You can acquire it by running the following command [on the server, of course]:\n"
                "sudo cat /etc/wireguard/public.key"
            )

            args.server_key = Prompt.input("What is the public server key?")

        generate_public_private_keypair()
        add_site(args)

    if args.server:
        if args.client_key and args.client_ip:
            add_client(args)
        else:
            with open("/etc/wireguard/public.key", "r", encoding="utf-8") as f:
                key = f.read()

            with urllib.request.urlopen("https://ident.me") as u:
                external_ip = u.read().decode("utf8")
            
            print(
                "\nTo add this site as a connection, run the following command on your client:"
            )
            print(
                f"python3 vpn_install.py --client --server_ip {external_ip} --server_key {key}"
            )
