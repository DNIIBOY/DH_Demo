from AsciiArt import *
from rich import pretty
from rich.console import Console
import json
import pyperclip
import re

UI_STATES = ["select_user", "pick_shared", "pick_private", "show_keys"]
USERS = ["Alice", "Bob"]
with open("defaultValues.json", "r") as f:
    DEFAULT_VALUES = json.loads(f.read())

pretty.install()
console = Console()


class Placeholder:
    def __init__(self):
        """Placeholder class for the Diffie-Hellman class"""
        self.name = ""
        self.g = -1
        self.p = -1
        self.port = 9000
        self.remote_port = 9001

    @staticmethod
    def send_request(request_type: str) -> bool:
        """Placeholder for send_request"""
        print("Sending request of type ", request_type)
        return True


class UIHandler:
    def __init__(self, DH):
        self.DH = DH
        self._state = UI_STATES[0]
        self.user = ""

    @property
    def state(self):
        return self._state

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
        self.DH.port = DEFAULT_VALUES[self.user.lower() + "Port"]
        self.DH.remote_port = 8000 if self.user == "Bob" else 8001
        self.DH.start()
        self.state = 1

    def pick_shared(self):
        """
        Pick the shared prime and generator
        :return:
        """
        console.clear()
        name_title = ([alice_art, bob_art] + USERS[2:])[USERS.index(self.user)]
        console.print(name_title)
        console.print("=" * 40)
        console.print("Pick a shared prime and generator")
        console.print("Shared prime (p): ", end="")

        p = input()
        p = get_value(p, DEFAULT_VALUES["p"])
        console.print(p)

        console.print("Generator (g): ", end="")
        g = input()
        g = get_value(g, DEFAULT_VALUES["g"])
        console.print(g)

        self.DH.p = p
        self.DH.g = g
        self.DH.send_request(request_type="shared")

        self.state = 2

    def pick_private(self):
        """
        Pick the private key for this user
        :return:
        """
        console.clear()
        name_title = ([alice_art, bob_art] + USERS[2:])[USERS.index(self.user)]
        console.print(name_title)
        console.print("=" * 40)
        console.print(f"Shared prime (p): {self.DH.p}")
        console.print(f"Generator (g): {self.DH.g}")
        console.print("=" * 40)
        console.print("Pick a private key")
        console.print(f"Private key ({self.user[0].lower()}): ", end="")
        secret = input()
        secret = get_value(secret)
        console.print(secret)

        self.DH.secret = secret
        self.state = 3

    def show_keys(self):
        """
        Show the public and private keys
        :return:
        """
        pass


def get_value(inp, default=-1):
    if inp == "":
        inp = pyperclip.paste()
        inp = re.sub(r"(\n|\r|\s|\t)", "", inp)
    try:
        inp = int(inp)
    except ValueError:
        try:
            inp = int(inp, 16)
        except ValueError:
            inp = ""
    inp = default if not inp else inp
    return inp


def main():
    PH = Placeholder()
    UIH = UIHandler(PH)
    UIH.state = 0


if __name__ == '__main__':
    main()
