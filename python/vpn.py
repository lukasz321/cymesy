import subprocess
import ipaddress
import argparse
import random
import os

if not os.getuid() == 0:
    print("You must run this script as a superuser.")
    exit(1)

def install_prerequisites(side):
    packages = ["wireguard"]
    
    if side == "client":
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


def generate_keys(side):
    if os.path.exists("/etc/wireguard/private.key"):
        print("\033[91m" + "danger zone!" + "\033[0m")
        print("keys already exist. if you generate a new set,\ "
                "you will break all your current wireguard connections.")
        
        while True:
            user_input = input("\ndo you want to continue? [y/n]: ")
            if user_input == "y":
                break
            elif user_input == "n":
                return

    cmd = "umask 077; wg genkey | sudo tee /etc/wireguard/private.key; "\
            "sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key"
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
        p.communicate()

    if side == "client":
        generate_keys_client_side()
    elif side == "server":
        generate_keys_server_side()


def generate_keys_client_side():
    # kwargs?
    with open("/etc/wireguard/private.key", "r"):
        private_key = f.read()

    content = \
            "[Interface]"
    f"PrivateKey = {private_key}"\
    f"Address = 10.8.0.{random.randint(6, 255)}/24"\
    "PostUp = ip rule add table 200 from 74.67.192.201"\
    "PostUp = ip route add table 200 default via 74.67.192.201"\
    "PreDown = ip rule delete table 200 from 74.67.192.201"\
    "PreDown = ip route delete table 200 default via 74.67.192.201"\

    "[Peer]"\
    f"PublicKey = {server_public_key}"\
    "AllowedIPs = 0.0.0.0/0, ::/0"\
    f"Endpoint = {server_ip}:51820"

    # Ask how do you want to name this connection?
    # Check if it already exists...
    with open("/etc/wireguard/{server_name}.conf", "w+"):
        f.write(content)

    # Read public key.
    # Spit out ip address.
    # Tell user how to turn on.


def generate_keys_server_side():
    with open("/etc/wireguard/private.key", "r"):
        private_key = f.read()

    content = \
        "[Interface]"\
        f"PrivateKey = {private_key}"
        "Address = 10.8.0.1/24"\
        "ListenPort = 51820"\
        "SaveConfig = true"\
        "PostUp = ufw route allow in on wg0 out on eth0"\
        "PostUp = iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE"\
        "PostUp = ip6tables -t nat -I POSTROUTING -o eth0 -j MASQUERADE"\
        "PreDown = ufw route delete allow in on wg0 out on eth0"\
        "PreDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"\
        "PreDown = ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"\
    
    with open("/etc/wireguard/wg0.conf", "w+") as f:
        f.write(content)
    
    with open("/etc/sysctl.conf", "r"):
        sysctl_conf = f.read()

    #setup ipv4 ip forwarding
    if "net.ipv4.ip_forward=1" not in sysctl_conf:
        with open("/etc/sysctl.conf", "a") as f:
            f.write("net.ipv4.ip_forward=1")

    cmd = "sudo ufw allow 51820/udp; "\
            "sudo ufw allow OpenSSH; "\
            "sudo systemctl enable wg-quick@wg0.service"

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
        p.communicate()


def add_client(public_key, ip_address):
    cmd = "sudo wg set wg0 peer {public_key} allowed-ips {ip_address}"


def delete_client(ip_address):
    sudo wg show
    sudo wg set wg0 peer PeURxj4Q75RaVhBKkRTpNsBPiPSGb5oQijgJsTa29hg= remove


def test_firewall():
# check to see if firewall open
    sudo nmap -sU -p 51820 192.168.9.196

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Setup Wireguard")

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
        "--add_client",
        action="store_true",
        help="Required argument if you're on a server and adding a client.",
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

    
    parser.parse_args()

    if not args.client and not args.server:
        print("You gotta --")
        exit(1)
    elif args.client and args.server:
        print("")
        exit(1)
    elif args.client:
        if not (args.server_ip):
            print("")
        else:
            print("ok")
    elif args.server:
        if args.add_client:
            if not (args.client_key or args.client_ip):
                exit(1)
            else:
                # add client
                pass
        else:
            # set up the server
            pass
