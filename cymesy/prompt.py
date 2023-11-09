import time
import sys
import re
from termios import tcflush, TCIFLUSH
from typing import List, Tuple
from dateutil.relativedelta import relativedelta, MO
from datetime import date

CYAN = "\033[96m\033[1m"
GRAY = "\033[0m\033[1m"
ENDC = "\033[0m\033[0m"


class Prompt:
    """
    Class helping user interact with termianl.
    Ask for input, ask for acknowledgement, prompt yes or no, etc.

    Heavily influenced by click module.
    See __main__ at the bottom of this file for examples.
    """

    @staticmethod
    def choose(prompt: str, options: List) -> str:
        """
        Ask user for input. Input is limited to the options provided
        in the list (`options` argument). User must choose one of the options.

        Note that options are case sensitive.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        while True:
            print(f"Valid (case sensitive) options are: {options}")
            user_input = input(f">> {CYAN}{prompt}{ENDC} ")
            if user_input in options:
                return user_input

            print(f'"{user_input}" is not a valid option!')

    @staticmethod
    def confirm(prompt: str):
        """
        An alias for Prompt.acknowledge.
        """

        Prompt.acknowledge(prompt=prompt)

    @staticmethod
    def acknowledge(prompt: str):
        """
        Prompt user to hit ENTER.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        tcflush(sys.stdin, TCIFLUSH)
        _ = input(f">> {CYAN}{prompt}{ENDC} [ENTER]")

    @staticmethod
    def input(prompt: str, flush: bool = False) -> str:
        """
        Ask user for input. Note that no input is accepted, so return may be "".
        """

        if flush:
            tcflush(sys.stdin, TCIFLUSH)

        user_input = input(f">> {CYAN}{prompt}{ENDC}: ")
        return user_input

    @staticmethod
    def yes_no(prompt: str) -> bool:
        """
        Ask operator to choose "y" or "n" to prompt.
        """

        if prompt.endswith(":") or prompt.endswith("."):
            prompt = prompt[:-1]

        while True:
            user_input = input(f">> {CYAN}{prompt} {GRAY}[Y/n]{ENDC}: ")
            if user_input:
                if user_input.lower() == "y":
                    return True
                if user_input.lower() == "n":
                    return False

            print(f'"{user_input}" is an invalid input! Enter "y" or "n".')

    @staticmethod
    def date_range() -> Tuple[str, str]:
        """
        Ask user start and end date.
        Use case: asking for records generated between date YYYY-MM-DD and YYYY2-MM2-DD2.

        Returns
        -------
            Tuple(str(start_date), str(end_date)
        """

        def print_valid_options():
            print("\nValid options:")
            print("  w:           since Monday")
            print("  t:           today")
            print("  m:           30 days ago")
            print("  YYYY-MM-dd:  your custom date")

        while True:
            print_valid_options()
            start_date = Prompt.input("ENTER START DATE")
            if start_date == "w":
                today = date.today()
                last_monday = today + relativedelta(weekday=MO(-1))
                start_date = last_monday.strftime("%Y-%m-%d")
                break

            if start_date == "t":
                today = date.today()
                start_date = today.strftime("%Y-%m-%d")
                break

            if start_date == "m":
                today = date.today()
                mo = today - relativedelta(days=30)
                start_date = mo.strftime("%Y-%m-%d")
                break

            p = re.compile("\d{4}-\d{2}-\d{2}")
            if p.match(start_date):
                break

            print(YLW + "Nope! Expecting YYYY-MM-DD." + ENDC + "\n")

        while True:
            end_date = Prompt.input("ENTER END DATE")
            if end_date == "w":
                today = date.today()
                last_monday = today + relativedelta(weekday=MO(-1))
                end_date = last_monday.strftime("%Y-%m-%d")
                break

            if end_date == "t":
                today = date.today()
                end_date = today.strftime("%Y-%m-%d")
                break

            if end_date == "m":
                today = date.today()
                mo = today - relativedelta(days=30)
                end_date = mo.strftime("%Y-%m-%d")
                break

            p = re.compile("\d{4}-\d{2}-\d{2}")
            if p.match(end_date):
                break

            print(YLW + "Nope! Expecting YYYY-MM-DD." + ENDC + "\n")

        return (start_date, end_date)


if __name__ == "__main__":
    true_or_false = Prompt.yes_no("Works?")
    date_range = Prompt.date_range()
    user_input = Prompt.input("How old are you?")
    true_or_false = Prompt.confirm("Press ENTER if you accept the terms")
    Prompt.confirm("Do you confirm?")
    user_choice = Prompt.choose(
        "Choose [A] if you like apples or [P] if you like pears", options=["a", "p"]
    )
