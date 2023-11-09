import os
import time
import subprocess
import usb.core

from .environment import Environment
from .system import system_command
from .utils import Prompt
from . import log

"""
lpinfo --include-schemes usb -v
    Show currently connected printers via USB.

lpstat -v
    Print a list of installed printers, connected or not.

lpadmin \
    -p 'name of your printer - extract from lpinfo' \
    -v 'uri of the printer - extract from lpinfo' \
    -E

    Installs the printer. Restart of cups.service advised.
    
    Note that -E arg is necessary, it enables the printer.
    As for naming, I extract the model from lpinfo, 
    replace all odd signs like "%20" with "-" and append S/N.

    Before running this command, make sure the printer is not
    already installed via lpstat -v. Best identifier for the printer
    is the serial number, I guess.
"""


class Zebra:
    """
    https://www.zebra.com/content/dam/zebra/manuals/printers/common/programming/zpl-zbi2-pm-en.pdf
    """

    def __init__(self, serial_number: str = "", vid: str = "", pid: str = ""):
        if not serial_number:
            env_var = os.environ["MFG_PRINTER"]
            if "-" in env_var:
                serial_number, vid, pid = env_var.split("-")
            else:
                serial_number = env_var

        self.serial_number = serial_number
        log.info(f"Trying to reach Zebra S/N {self.serial_number}...\n")
        self.name = Zebra.get_printer_name(serial_number)
        self.vid = vid
        self.pid = pid

    def test_print(self):
        """
        Print junk.
        """

        ZPL = """
        ^XA

        ^LT-6^LH100,100

        ^FO250,350
        ^A@N,70,30,XXX.FNT
        ^FDRJ = Denzel; JV = Dan Blizerian^FS

        ^XZ
        """

        self.print(zpl=ZPL)

    def print(self, zpl: str) -> bool:
        """
        https://www.zebra.com/content/dam/zebra/manuals/printers/common/programming/zpl-zbi2-pm-en.pdf
        Print - format the print job in ZPL.
        Note that cancels all previous jobs before printing.

        Args
        ----
            zpl -- Zebra Programming Language code
        """

        stdout = system_command(f"lpinfo --include-schemes usb -v")[1]
        if self.serial_number not in stdout:
            log.error(
                f"{self.serial_number} is not connected. Skipping print.", bold=True
            )
            return False

        if not self.name:
            return False

        os.system("cancel -a -x")

        if self.vid and self.pid:
            dev = usb.core.find(
                idVendor=int(self.vid, 16),
                idProduct=int(self.pid, 16),
            )

            try:
                dev.reset()
            except Exception:
                pass

        time.sleep(0.3)

        log.info(
            f"Queueing a print job for Zebra SN {self.serial_number}, {self.name}.",
            fg="yellow",
        )

        with subprocess.Popen(
            ["lp", "-d", self.name, "-"],
            shell=False,
            stdin=subprocess.PIPE,
            encoding="ascii",
        ) as p:
            stdout = p.communicate(input=zpl)[0]

        return True

    def is_connected(self) -> bool:
        """
        Check if the Zebra is connected via USB.
        If connected and vid/pid are known, reset usb dev.
        """

        stdout = system_command(f"lpinfo --include-schemes usb -v")[1]

        if self.serial_number in stdout:
            if self.vid and self.pid:
                dev = usb.core.find(
                    idVendor=int(self.vid, 16),
                    idProduct=int(self.pid, 16),
                )

                try:
                    dev.reset()
                except Exception:
                    pass

            return True

        return False

    @classmethod
    def install_printer(cls):
        """
        Find connected Zebra printer (only one expected) and extract its S/N.
        Then export the serial number to environment variables in the following format:
        MFG_PRINTER="SERIALNUM-VID-PID"
        This function also sets the udev rules.
        """

        log.info("Discovering connected printers... This may take up to 15 sec...")
        stdout = system_command(f"lpinfo --include-schemes usb -v")[1]
        printers_found = list(filter(None, stdout.split("\n")))
        zebra_printers = list(filter(lambda k: "Zebra" in k, printers_found))

        if len(zebra_printers) == 0:
            log.error("No Zebra printers connected.")
            return False

        if len(zebra_printers) > 1:
            log.error(
                f"There are {len(zebra_printers)} Zebra printers connected.\n"
                "Installation supports only one printer at a time.\n"
                "Please disconnect all printers except the one you want to install."
            )
            return False

        # direct usb://Zebra%20Technologies/ZTC%20ZT410-600dpi%20ZPL?serial=18J194403879
        serial_number = zebra_printers[0].split("serial=")[1]
        uri = "usb://" + zebra_printers[0].split("usb://", maxsplit=1)[1]
        model = uri.split("usb://", maxsplit=1)[-1].split("?", maxsplit=1)[0]
        model = model.replace("%20", "-").replace("/", "-")

        if not serial_number:
            log.error(f"Couldnt extract serial number from {zebra_printers[0]}!")
            return False

        # Now that we have the serial check if printer is installed via lpstat
        stdout = system_command(f"lpstat -v")[1]
        if serial_number not in stdout:
            log.info("Printer must be installed first.")
            # Note that adding it under model-serial name.
            cmd = f"lpadmin -p '{model}-{serial_number}' -v '{uri}' -E"
            log.info(cmd)
            _, stdout, _ = system_command(cmd)
            log.info("Restarting cups.service...")
            os.system("systemctl restart cups")
            time.sleep(2)

        # Get VID:PID
        cmd = "lsusb | grep 'Zebra' | grep -oP '[a-zA-Z0-9]{4}:[a-zA-Z0-9]{4}'"
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) as p:
            vid, pid = p.communicate()[0].strip().decode("utf-8").split(":")

        # Update and reload /etc/udev/rules.d/?.rules
        if not os.path.isfile("/etc/udev/rules.d/99-zebra.rules"):
            rule = f'SUBSYSTEM=="usb", ATTR{{idVendor}}=="{vid}", MODE="0666"'
            with open("/etc/udev/rules.d/99-zebra.rules", "w+") as f:
                f.write(f"{rule}")
                f.flush()

            os.system("udevadm control --reload-rules; udevadm trigger")

        is_supplementary = False
        while True:
            log.info(
                "If this is a REGULAR Zebra label printer, enter [R].\n"
                "If this is a SUPPLEMENTARY (Packout ONLY) label printer, enter [S].",
                fg="yellow",
            )
            user_input = Prompt.input("Your input", flush=True)
            if user_input.lower() == "r":
                break
            elif user_input.lower() == "s":
                is_supplementary = True
                break

        printer_key = "MFG_PRINTER_XXL" if is_supplementary else "MFG_PRINTER"
        Environment.set_variable(printer_key, "-".join([serial_number, vid, pid]))
        zebra = Zebra(serial_number, vid, pid)
        zebra.test_print()
        return True

    @classmethod
    def get_printer_name(cls, serial_number: str):
        """
        Decode printer name from printer serial number via lpstat -v.
        """
        stdout = system_command(f"lpstat -v")[1]
        if serial_number not in stdout:
            log.error(
                f"Is {serial_number} a valid Zebra serial number? "
                "Cannot find this printer via lpstat -v."
            )
            return None

        printers = list(filter(None, stdout.split("\n")))
        my_printer = None
        for printer in printers:
            if serial_number in printer:
                my_printer = printer.rstrip()
                break

        if not my_printer:
            raise Exception("Something went wrong.")

        printer_name = my_printer.split(":")[0].split()[-1]
        return printer_name


def main():
    import argparse

    parser = argparse.ArgumentParser("Perform actions on a Zebra printer.")

    parser.add_argument(
        "--install",
        action="store_true",
        help="Install or reinstall a Zebra printer. "
        "Must connect one printer at a time. "
        "Reboot required for the changes to take effect.",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test connection to printer by printing a label.",
    )

    parser.add_argument(
        "--name",
        action="store_true",
        help="Ouput the name/model of connected currently connected printer. "
        "Note that printer must be installed first (via --install).",
    )

    args = parser.parse_args()

    if args.install:
        success = Zebra.install_printer()
        if success:
            Prompt.acknowledge("Restart the terminal for changes to take effect, OK?")
    elif args.test:
        if os.environ.get("MFG_PRINTER"):
            sn, vid, pid = os.environ["MFG_PRINTER"].split("-")
            zebra = Zebra(sn, vid, pid)
            zebra.test_print()
            time.sleep(1)
        else:
            log.warning("MFG_PRINTER not defined in the environment.")

        if os.environ.get("MFG_PRINTER_XXL"):
            sn, vid, pid = os.environ["MFG_PRINTER_XXL"].split("-")
            zebra = Zebra(sn, vid, pid)
            zebra.test_print()
        else:
            log.warning("MFG_PRINTER_XXL not defined in the environment.")
    elif args.name:
        if os.environ.get("MFG_PRINTER"):
            print(Zebra.get_printer_name(os.environ["MFG_PRINTER"].split("-")[0]))

        if os.environ.get("MFG_PRINTER_XXL"):
            print(Zebra.get_printer_name(os.environ["MFG_PRINTER_XXL"].split("-")[0]))
    else:
        log.error(
            "************************************************",
            fg="yellow",
            bold=True,
            blink=True,
        )
        log.error(
            "You need to pass an argument! See options below.", fg="yellow", bold=True
        )
        log.error(
            "************************************************",
            fg="yellow",
            bold=True,
            blink=True,
        )
        parser.print_help()


if __name__ == "__main__":
    main()
