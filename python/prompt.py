import time
import sys
from termios import tcflush, TCIFLUSH

from typing import List

class Prompt:
    """
    Class helping operators interact with shell.
    Ask for input, ask for acknowledgement, prompt yes or no.

    Heavily influenced by click module.
    See __main__ at the bottom of this file for examples.
    """

    CYAN = "\033[96m\033[1m"
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
        _ = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC} [ENTER]")

    @staticmethod
    def wait(seconds: int, prompt: str = "Retrying in"):
        """
        Essentially a nice "interactive" sleep time with a countdown.
        """

        print("")
        for i in range(1, seconds + 1):
            print(
                f"{prompt} {seconds-i} seconds...",
                fg="white",
                inline=True,
            )
            time.sleep(1)

    @staticmethod
    def input(prompt: str, flush: bool = False) -> str:
        """
        Ask operator for input. Note that no input is accepted.

        Returns
        -------
            str: user_input - may be empty.
        """

        if flush:
            tcflush(sys.stdin, TCIFLUSH)

        user_input = input(f">> {Prompt.CYAN}{prompt}{Prompt.ENDC}: ")
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


if __name__ == "__main__":
    true_or_false = Prompt.yes_no("Works?")
    user_input = Prompt.input("How old are you?")
    true_or_false = Prompt.confirm("Press ENTER if you accept the terms")
    Prompt.confirm("Do you confirm?")
    user_choice = Prompt.choose(
        "Choose [A] if you like apples or [P] if you like pears", options=["a", "p"]
    )
