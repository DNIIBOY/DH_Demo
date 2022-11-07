from AsciiArt import *
from rich import pretty
from rich.console import Console
import os

UI_STATES = ["select_user", "pick_shared", "pick_private", "show_keys"]
USERS = ["Alice", "Bob"]

pretty.install()
console = Console()


class Placeholder:
    def __init__(self):
        """Placeholder class for the Diffie-Hellman class"""
        self.name = ""


class UIHandler:
    def __init__(self, DH):
        self.DH = DH
        self._state = UI_STATES[0]
        self.user = ""

    @property
    def state(self):
        return self.state

    @state.setter
    def state(self, value: str | int):
        if isinstance(value, int):
            value = UI_STATES[value]
        self._state = value
        match value:
            case "select_user":
                self.select_user()
            case "pick_shared":
                self.pick_shared()
            case "pick_private":
                self.pick_private()
            case "show_keys":
                self.show_keys()
            case _:
                raise ValueError("Invalid state")

    def select_user(self):
        """
        Selects the user to be Alice or Bob
        """
        console.clear()
        console.print(title)
        console.print(f"{', '.join([f'({u[0]}){u[1:]}' for u in USERS[:-1]])} or ({USERS[-1][0]}){USERS[-1][1:]}: ", end="")
        user = input().lower()
        self.user = [u for u in USERS if u.lower().startswith(user)][0]
        self.DH.name = self.user
        self.state = 1

    def pick_shared(self):
        """
        Pick the shared prime and generator
        :return:
        """
        console.clear()
        name_title = ([alice_art, bob_art] + USERS[2:])[USERS.index(self.user)]
        console.print(name_title)
        console.print("Pick a shared prime and generator")

    def pick_private(self):
        """
        Pick the private key, for this user
        :return:
        """
        pass

    def show_keys(self):
        """
        Show the public and private keys
        :return:
        """
        pass


def main():
    PH = Placeholder()
    UIH = UIHandler(PH)
    UIH.state = 0


if __name__ == '__main__':
    main()
